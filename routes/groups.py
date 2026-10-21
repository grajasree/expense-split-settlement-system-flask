from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db
from routes.auth_utils import login_required, validate_csrf

groups_bp = Blueprint('groups', __name__, url_prefix='/groups')

def calculate_group_budget_status(budget, spent):
    """
    Calculate budget percentage and status based on criteria:
    - Below 75%: Normal
    - 75% to below 90%: Warning
    - 90% to below 100%: High spending alert
    - 100% or above: Budget exceeded
    """
    budget = Decimal(str(budget or 0))
    spent = Decimal(str(spent or 0))

    if budget <= 0:
        return {
            'budget': Decimal('0.00'),
            'spent': spent,
            'remaining': Decimal('0.00'),
            'percent': 0,
            'status': 'Not Set',
            'badge_class': 'badge-secondary',
            'alert_class': 'info'
        }

    remaining = budget - spent
    percent = round((spent / budget) * 100, 1)

    if percent < 75:
        status = 'Normal'
        badge_class = 'badge-success'
        alert_class = 'success'
    elif percent < 90:
        status = 'Warning (Approaching Limit)'
        badge_class = 'badge-warning'
        alert_class = 'warning'
    elif percent < 100:
        status = 'High Spending Alert'
        badge_class = 'badge-orange'
        alert_class = 'danger'
    else:
        status = 'Budget Exceeded'
        badge_class = 'badge-danger'
        alert_class = 'danger'

    return {
        'budget': budget,
        'spent': spent,
        'remaining': remaining,
        'percent': min(float(percent), 100.0),
        'raw_percent': float(percent),
        'status': status,
        'badge_class': badge_class,
        'alert_class': alert_class
    }

@groups_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    db = get_db()
    with db.cursor() as cursor:
        # Get groups where logged-in user is a member
        cursor.execute("""
            SELECT g.id, g.name, g.description, g.created_at, gm.role,
                   u.name AS creator_name,
                   (SELECT COUNT(*) FROM group_members WHERE group_id = g.id) AS member_count,
                   COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) AS total_spent,
                   COALESCE(gb.monthly_budget, 0.00) AS monthly_budget
            FROM `groups` g
            JOIN group_members gm ON g.id = gm.group_id
            JOIN users u ON g.created_by = u.id
            LEFT JOIN group_budgets gb ON g.id = gb.group_id
            WHERE gm.user_id = %s
            ORDER BY g.created_at DESC
        """, (user_id,))
        groups_raw = cursor.fetchall()

    groups_list = []
    for g in groups_raw:
        budget_info = calculate_group_budget_status(g['monthly_budget'], g['total_spent'])
        groups_list.append({
            **g,
            'budget_info': budget_info
        })

    return render_template('groups.html', groups=groups_list)

@groups_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf(csrf_token):
            flash('Invalid security token.', 'danger')
            return redirect(url_for('groups.create'))

        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        monthly_budget_str = request.form.get('monthly_budget', '0').strip()

        if not name:
            flash('Group name is required.', 'danger')
            return render_template('groups.html')

        try:
            monthly_budget = Decimal(monthly_budget_str) if monthly_budget_str else Decimal('0.00')
            if monthly_budget < 0:
                flash('Budget amount cannot be negative.', 'danger')
                return redirect(url_for('groups.index'))
        except Exception:
            flash('Please enter a valid numeric budget.', 'danger')
            return redirect(url_for('groups.index'))

        user_id = session['user_id']
        db = get_db()
        try:
            with db.cursor() as cursor:
                # 1. Insert group
                cursor.execute(
                    "INSERT INTO `groups` (name, description, created_by) VALUES (%s, %s, %s)",
                    (name, description, user_id)
                )
                group_id = cursor.lastrowid

                # 2. Add creator as member
                cursor.execute(
                    "INSERT INTO group_members (group_id, user_id, role) VALUES (%s, %s, 'creator')",
                    (group_id, user_id)
                )

                # 3. Add budget if specified
                if monthly_budget > 0:
                    cursor.execute(
                        "INSERT INTO group_budgets (group_id, monthly_budget) VALUES (%s, %s)",
                        (group_id, monthly_budget)
                    )

            db.commit()
            flash(f"Group '{name}' created successfully!", 'success')
            return redirect(url_for('groups.details', group_id=group_id))
        except Exception as e:
            db.rollback()
            flash(f'Failed to create group: {str(e)}', 'danger')
            return redirect(url_for('groups.index'))

    return redirect(url_for('groups.index'))

@groups_bp.route('/<int:group_id>')
@login_required
def details(group_id):
    user_id = session['user_id']
    db = get_db()
    with db.cursor() as cursor:
        # Check authorization: user must belong to group
        cursor.execute("SELECT role FROM group_members WHERE group_id = %s AND user_id = %s", (group_id, user_id))
        membership = cursor.fetchone()
        if not membership:
            flash('You do not have access to view this group.', 'danger')
            return redirect(url_for('groups.index'))

        # Fetch group basic info
        cursor.execute("""
            SELECT g.id, g.name, g.description, g.created_by, g.created_at,
                   u.name AS creator_name,
                   COALESCE(gb.monthly_budget, 0.00) AS monthly_budget
            FROM `groups` g
            JOIN users u ON g.created_by = u.id
            LEFT JOIN group_budgets gb ON g.id = gb.group_id
            WHERE g.id = %s
        """, (group_id,))
        group = cursor.fetchone()

        # Fetch group members
        cursor.execute("""
            SELECT gm.id, gm.role, gm.joined_at, u.id AS user_id, u.name, u.email
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = %s
            ORDER BY (gm.role = 'creator') DESC, u.name ASC
        """, (group_id,))
        members = cursor.fetchall()

        # Fetch group expenses
        cursor.execute("""
            SELECT e.id, e.description, e.amount, e.category, e.date, e.split_type, e.paid_by,
                   u.name AS payer_name,
                   (SELECT COUNT(*) FROM expense_splits WHERE expense_id = e.id) AS participant_count
            FROM expenses e
            JOIN users u ON e.paid_by = u.id
            WHERE e.group_id = %s
            ORDER BY e.date DESC, e.id DESC
        """, (group_id,))
        expenses = cursor.fetchall()

        # Calculate total spending
        cursor.execute("SELECT COALESCE(SUM(amount), 0.00) AS total FROM expenses WHERE group_id = %s", (group_id,))
        total_spent = cursor.fetchone()['total']

        # Calculate simplified settlement for this group
        # 1. Total paid by each user in this group
        cursor.execute("""
            SELECT paid_by AS user_id, SUM(amount) AS total_paid
            FROM expenses
            WHERE group_id = %s
            GROUP BY paid_by
        """, (group_id,))
        paid_rows = {row['user_id']: Decimal(str(row['total_paid'])) for row in cursor.fetchall()}

        # 2. Total share owed by each user in this group
        cursor.execute("""
            SELECT es.user_id, SUM(es.share_amount) AS total_share
            FROM expense_splits es
            JOIN expenses e ON es.expense_id = e.id
            WHERE e.group_id = %s
            GROUP BY es.user_id
        """, (group_id,))
        share_rows = {row['user_id']: Decimal(str(row['total_share'])) for row in cursor.fetchall()}

    # Compute member balances in this group
    member_balances = []
    member_dict = {m['user_id']: m['name'] for m in members}
    net_balances = {}

    for m in members:
        uid = m['user_id']
        p = paid_rows.get(uid, Decimal('0.00'))
        s = share_rows.get(uid, Decimal('0.00'))
        net = p - s
        net_balances[uid] = net
        member_balances.append({
            'user_id': uid,
            'name': m['name'],
            'email': m['email'],
            'role': m['role'],
            'paid': p,
            'share': s,
            'net': net
        })

    # Settlement suggestions algorithm
    settlements = simplify_debts(net_balances, member_dict)

    budget_info = calculate_group_budget_status(group['monthly_budget'], total_spent)

    return render_template(
        'group_details.html',
        group=group,
        members=members,
        expenses=expenses,
        budget_info=budget_info,
        member_balances=member_balances,
        settlements=settlements,
        user_role=membership['role']
    )

@groups_bp.route('/<int:group_id>/add-member', methods=['POST'])
@login_required
def add_member(group_id):
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf(csrf_token):
        flash('Invalid security token.', 'danger')
        return redirect(url_for('groups.details', group_id=group_id))

    user_id = session['user_id']
    email = request.form.get('email', '').strip().lower()

    if not email:
        flash('Please provide an email address.', 'warning')
        return redirect(url_for('groups.details', group_id=group_id))

    db = get_db()
    try:
        with db.cursor() as cursor:
            # Check authorization: user must belong to group
            cursor.execute("SELECT id FROM group_members WHERE group_id = %s AND user_id = %s", (group_id, user_id))
            if not cursor.fetchone():
                flash('You are not authorized to add members to this group.', 'danger')
                return redirect(url_for('groups.index'))

            # Check if user with this email exists
            cursor.execute("SELECT id, name FROM users WHERE email = %s", (email,))
            target_user = cursor.fetchone()

            if not target_user:
                flash(f"No registered user found with email '{email}'. Please ask them to register on the site first.", 'warning')
                return redirect(url_for('groups.details', group_id=group_id))

            # Check if already a member
            cursor.execute("SELECT id FROM group_members WHERE group_id = %s AND user_id = %s", (group_id, target_user['id']))
            if cursor.fetchone():
                flash(f"{target_user['name']} is already a member of this group.", 'info')
                return redirect(url_for('groups.details', group_id=group_id))

            # Insert into group_members
            cursor.execute(
                "INSERT INTO group_members (group_id, user_id, role) VALUES (%s, %s, 'member')",
                (group_id, target_user['id'])
            )
        db.commit()
        flash(f"Successfully added {target_user['name']} ({email}) to the group!", 'success')
    except Exception as e:
        db.rollback()
        flash(f"Error adding member: {str(e)}", 'danger')

    return redirect(url_for('groups.details', group_id=group_id))

@groups_bp.route('/<int:group_id>/set-budget', methods=['POST'])
@login_required
def set_budget(group_id):
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf(csrf_token):
        flash('Invalid security token.', 'danger')
        return redirect(url_for('groups.details', group_id=group_id))

    user_id = session['user_id']
    budget_str = request.form.get('monthly_budget', '0').strip()

    try:
        budget = Decimal(budget_str)
        if budget < 0:
            flash('Budget cannot be negative.', 'danger')
            return redirect(url_for('groups.details', group_id=group_id))
    except Exception:
        flash('Please enter a valid numeric amount.', 'danger')
        return redirect(url_for('groups.details', group_id=group_id))

    db = get_db()
    try:
        with db.cursor() as cursor:
            # Check user membership
            cursor.execute("SELECT role FROM group_members WHERE group_id = %s AND user_id = %s", (group_id, user_id))
            membership = cursor.fetchone()
            if not membership:
                flash('Unauthorized to set budget for this group.', 'danger')
                return redirect(url_for('groups.index'))

            cursor.execute("""
                INSERT INTO group_budgets (group_id, monthly_budget)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE monthly_budget = %s
            """, (group_id, budget, budget))
        db.commit()
        flash(f"Monthly budget updated to ₹{budget:,.2f} successfully!", 'success')
    except Exception as e:
        db.rollback()
        flash(f"Error updating budget: {str(e)}", 'danger')

    return redirect(url_for('groups.details', group_id=group_id))


def simplify_debts(net_balances, member_dict):
    """
    Greedy debt simplification algorithm (Who Owes Whom).
    Pairs largest debtor with largest creditor until all balances are settled.
    """
    debtors = []   # net < 0 (owes money)
    creditors = [] # net > 0 (gets back money)

    for uid, net in net_balances.items():
        # Round to 2 decimal places to avoid floating point imprecision
        amount = round(Decimal(str(net)), 2)
        if amount < Decimal('-0.01'):
            debtors.append({'user_id': uid, 'name': member_dict.get(uid, f'User #{uid}'), 'amount': -amount})
        elif amount > Decimal('0.01'):
            creditors.append({'user_id': uid, 'name': member_dict.get(uid, f'User #{uid}'), 'amount': amount})

    settlements = []
    d_idx = 0
    c_idx = 0

    while d_idx < len(debtors) and c_idx < len(creditors):
        debtor = debtors[d_idx]
        creditor = creditors[c_idx]

        settled_amount = min(debtor['amount'], creditor['amount'])
        if settled_amount > Decimal('0.01'):
            settlements.append({
                'debtor_id': debtor['user_id'],
                'debtor_name': debtor['name'],
                'creditor_id': creditor['user_id'],
                'creditor_name': creditor['name'],
                'amount': settled_amount
            })

        debtor['amount'] -= settled_amount
        creditor['amount'] -= settled_amount

        if debtor['amount'] <= Decimal('0.01'):
            d_idx += 1
        if creditor['amount'] <= Decimal('0.01'):
            c_idx += 1

    return settlements
