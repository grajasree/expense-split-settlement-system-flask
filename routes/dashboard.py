from decimal import Decimal
from flask import Blueprint, render_template, session, jsonify, request
from db import get_db
from routes.auth_utils import login_required
from routes.groups import calculate_group_budget_status, simplify_debts

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_id = session['user_id']
    db = get_db()

    with db.cursor() as cursor:
        # 1. Get user's groups
        cursor.execute("""
            SELECT g.id, g.name,
                   COALESCE(gb.monthly_budget, 0.00) AS monthly_budget,
                   COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) AS total_spent
            FROM `groups` g
            JOIN group_members gm ON g.id = gm.group_id
            LEFT JOIN group_budgets gb ON g.id = gb.group_id
            WHERE gm.user_id = %s
            ORDER BY g.name ASC
        """, (user_id,))
        user_groups = cursor.fetchall()
        group_ids = [g['id'] for g in user_groups]

        if not group_ids:
            return render_template(
                'dashboard.html',
                empty_state=True,
                group_count=0,
                total_expenses=Decimal('0.00'),
                total_paid=Decimal('0.00'),
                user_owes=Decimal('0.00'),
                others_owe=Decimal('0.00'),
                recent_expenses=[],
                budget_alerts=[],
                groups_summary=[]
            )

        format_p = ','.join(['%s'] * len(group_ids))

        # 2. Total expenses in groups
        cursor.execute(f"SELECT COALESCE(SUM(amount), 0.00) AS total FROM expenses WHERE group_id IN ({format_p})", group_ids)
        total_expenses = Decimal(str(cursor.fetchone()['total']))

        # 3. Total paid by user
        cursor.execute(f"SELECT COALESCE(SUM(amount), 0.00) AS paid FROM expenses WHERE paid_by = %s AND group_id IN ({format_p})", [user_id] + group_ids)
        total_paid = Decimal(str(cursor.fetchone()['paid']))

        # 4. Total user share
        cursor.execute(f"""
            SELECT COALESCE(SUM(es.share_amount), 0.00) AS share
            FROM expense_splits es
            JOIN expenses e ON es.expense_id = e.id
            WHERE es.user_id = %s AND e.group_id IN ({format_p})
        """, [user_id] + group_ids)
        total_share = Decimal(str(cursor.fetchone()['share']))

        # 5. Recent expenses (latest 6)
        cursor.execute(f"""
            SELECT e.id, e.description, e.amount, e.category, e.date, e.group_id,
                   g.name AS group_name, u.name AS payer_name, e.paid_by,
                   COALESCE(es.share_amount, 0.00) AS my_share
            FROM expenses e
            JOIN `groups` g ON e.group_id = g.id
            JOIN users u ON e.paid_by = u.id
            LEFT JOIN expense_splits es ON e.id = es.expense_id AND es.user_id = %s
            WHERE e.group_id IN ({format_p})
            ORDER BY e.date DESC, e.id DESC
            LIMIT 6
        """, [user_id] + group_ids)
        recent_expenses = cursor.fetchall()

    # Calculate exact owes / gets back via settlements across user's groups
    user_owes = Decimal('0.00')
    others_owe = Decimal('0.00')

    with db.cursor() as cursor:
        for g in user_groups:
            gid = g['id']
            cursor.execute("""
                SELECT u.id, u.name
                FROM group_members gm
                JOIN users u ON gm.user_id = u.id
                WHERE gm.group_id = %s
            """, (gid,))
            m_dict = {m['id']: m['name'] for m in cursor.fetchall()}

            cursor.execute("SELECT paid_by AS user_id, SUM(amount) AS total FROM expenses WHERE group_id = %s GROUP BY paid_by", (gid,))
            p_map = {r['user_id']: Decimal(str(r['total'])) for r in cursor.fetchall()}

            cursor.execute("""
                SELECT es.user_id, SUM(es.share_amount) AS total
                FROM expense_splits es
                JOIN expenses e ON es.expense_id = e.id
                WHERE e.group_id = %s
                GROUP BY es.user_id
            """, (gid,))
            s_map = {r['user_id']: Decimal(str(r['total'])) for r in cursor.fetchall()}

            net_map = {uid: p_map.get(uid, Decimal('0.00')) - s_map.get(uid, Decimal('0.00')) for uid in m_dict}
            settlements = simplify_debts(net_map, m_dict)

            for s in settlements:
                if s['debtor_id'] == user_id:
                    user_owes += s['amount']
                elif s['creditor_id'] == user_id:
                    others_owe += s['amount']

    # Budget warnings and summaries
    budget_alerts = []
    groups_summary = []
    for g in user_groups:
        b_info = calculate_group_budget_status(g['monthly_budget'], g['total_spent'])
        groups_summary.append({
            'id': g['id'],
            'name': g['name'],
            **b_info
        })
        if b_info['percent'] >= 75 and b_info['budget'] > 0:
            budget_alerts.append({
                'group_name': g['name'],
                'group_id': g['id'],
                'percent': b_info['percent'],
                'status': b_info['status'],
                'badge_class': b_info['badge_class'],
                'alert_class': b_info['alert_class'],
                'spent': b_info['spent'],
                'budget': b_info['budget']
            })

    return render_template(
        'dashboard.html',
        empty_state=False,
        group_count=len(user_groups),
        total_expenses=total_expenses,
        total_paid=total_paid,
        user_owes=user_owes,
        others_owe=others_owe,
        recent_expenses=recent_expenses,
        budget_alerts=budget_alerts,
        groups_summary=groups_summary,
        user_groups=user_groups
    )

@dashboard_bp.route('/api/chart-data')
@login_required
def chart_data():
    """
    Returns live dynamic chart data for Chart.js from MySQL database.
    Supports filters for group_id, start_date, and end_date.
    Calculates total spending and average monthly spending from actual records.
    """
    user_id = session['user_id']
    group_filter = request.args.get('group_id', 'all')
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    db = get_db()

    with db.cursor() as cursor:
        cursor.execute("SELECT group_id FROM group_members WHERE user_id = %s", (user_id,))
        user_groups = cursor.fetchall()
        user_group_ids = [g['group_id'] for g in user_groups]

        if not user_group_ids:
            return jsonify({
                'monthly': {'labels': [], 'data': []},
                'categories': {'labels': [], 'data': []},
                'group_comparison': {'labels': [], 'data': []},
                'budget_comparison': {'labels': [], 'spent': [], 'budget': []},
                'total_spending': 0.0,
                'avg_monthly_spending': 0.0,
                'active_months_count': 0
            })

        # Filter target group IDs
        if group_filter != 'all' and group_filter.isdigit():
            target_gid = int(group_filter)
            target_group_ids = [target_gid] if target_gid in user_group_ids else user_group_ids
        else:
            target_group_ids = user_group_ids

        format_p = ','.join(['%s'] * len(target_group_ids))
        where_clauses = [f"group_id IN ({format_p})"]
        params = list(target_group_ids)

        if start_date:
            where_clauses.append("date >= %s")
            params.append(start_date)
        if end_date:
            where_clauses.append("date <= %s")
            params.append(end_date)

        where_sql = " AND ".join(where_clauses)

        # 1. Total filtered spending
        cursor.execute(f"SELECT COALESCE(SUM(amount), 0.00) AS total FROM expenses WHERE {where_sql}", params)
        total_spending = float(cursor.fetchone()['total'])

        # 2. Monthly spending (matching filters)
        cursor.execute(f"""
            SELECT DATE_FORMAT(date, '%%Y-%%m') AS month_label,
                   COALESCE(SUM(amount), 0.00) AS total
            FROM expenses
            WHERE {where_sql}
            GROUP BY month_label
            ORDER BY month_label ASC
        """, params)
        monthly_rows = cursor.fetchall()
        monthly_labels = [r['month_label'] for r in monthly_rows]
        monthly_data = [float(r['total']) for r in monthly_rows]

        # 3. Average monthly spending
        active_months = len(monthly_rows)
        avg_monthly_spending = round(total_spending / active_months, 2) if active_months > 0 else 0.0

        # 4. Category breakdown (matching filters)
        cursor.execute(f"""
            SELECT category, COALESCE(SUM(amount), 0.00) AS total
            FROM expenses
            WHERE {where_sql}
            GROUP BY category
            ORDER BY total DESC
        """, params)
        category_rows = cursor.fetchall()
        category_labels = [r['category'] for r in category_rows]
        category_data = [float(r['total']) for r in category_rows]

        # 5. Group-wise spending comparison (matching filters)
        cursor.execute(f"""
            SELECT g.name, COALESCE(SUM(e.amount), 0.00) AS total
            FROM `groups` g
            LEFT JOIN expenses e ON g.id = e.group_id
            WHERE g.id IN ({format_p})
            GROUP BY g.id, g.name
            ORDER BY g.name ASC
        """, target_group_ids)
        group_rows = cursor.fetchall()

        # 6. Budget vs Spent per group
        cursor.execute(f"""
            SELECT g.name,
                   COALESCE(gb.monthly_budget, 0.00) AS budget,
                   COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) AS spent
            FROM `groups` g
            LEFT JOIN group_budgets gb ON g.id = gb.group_id
            WHERE g.id IN ({format_p})
            ORDER BY g.name ASC
        """, target_group_ids)
        budget_rows = cursor.fetchall()

    return jsonify({
        'monthly': {
            'labels': monthly_labels,
            'data': monthly_data
        },
        'categories': {
            'labels': category_labels,
            'data': category_data
        },
        'group_comparison': {
            'labels': [r['name'] for r in group_rows],
            'data': [float(r['total']) for r in group_rows]
        },
        'budget_comparison': {
            'labels': [r['name'] for r in budget_rows],
            'spent': [float(r['spent']) for r in budget_rows],
            'budget': [float(r['budget']) for r in budget_rows]
        },
        'total_spending': total_spending,
        'avg_monthly_spending': avg_monthly_spending,
        'active_months_count': active_months
    })
