from decimal import Decimal
from flask import Blueprint, render_template, session
from db import get_db
from routes.auth_utils import login_required
from routes.groups import simplify_debts

balances_bp = Blueprint('balances', __name__, url_prefix='/balances')

@balances_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    db = get_db()

    with db.cursor() as cursor:
        # Get all groups the user is in
        cursor.execute("""
            SELECT g.id, g.name
            FROM `groups` g
            JOIN group_members gm ON g.id = gm.group_id
            WHERE gm.user_id = %s
        """, (user_id,))
        user_groups = cursor.fetchall()
        group_ids = [g['id'] for g in user_groups]

        if not group_ids:
            return render_template(
                'balances.html',
                total_paid=Decimal('0.00'),
                total_share=Decimal('0.00'),
                net_balance=Decimal('0.00'),
                owed_to_others=Decimal('0.00'),
                receivable_from_others=Decimal('0.00'),
                user_status='Settled',
                group_settlements=[],
                direct_balances=[]
            )

        format_placeholders = ','.join(['%s'] * len(group_ids))

        # 1. Total paid by logged-in user across their groups
        cursor.execute(f"""
            SELECT COALESCE(SUM(amount), 0.00) AS total_paid
            FROM expenses
            WHERE paid_by = %s AND group_id IN ({format_placeholders})
        """, [user_id] + group_ids)
        total_paid = Decimal(str(cursor.fetchone()['total_paid']))

        # 2. Total share owed by logged-in user across their groups
        cursor.execute(f"""
            SELECT COALESCE(SUM(es.share_amount), 0.00) AS total_share
            FROM expense_splits es
            JOIN expenses e ON es.expense_id = e.id
            WHERE es.user_id = %s AND e.group_id IN ({format_placeholders})
        """, [user_id] + group_ids)
        total_share = Decimal(str(cursor.fetchone()['total_share']))

        net_balance = total_paid - total_share
        if net_balance > Decimal('0.01'):
            user_status = 'Gets Back'
        elif net_balance < Decimal('-0.01'):
            user_status = 'Owes'
        else:
            user_status = 'Settled'

        # Compute settlements per group
        group_settlements = []
        for g in user_groups:
            gid = g['id']
            # Fetch all members of this group
            cursor.execute("""
                SELECT u.id, u.name
                FROM group_members gm
                JOIN users u ON gm.user_id = u.id
                WHERE gm.group_id = %s
            """, (gid,))
            g_members = cursor.fetchall()
            member_dict = {m['id']: m['name'] for m in g_members}

            # Group payments
            cursor.execute("""
                SELECT paid_by AS user_id, SUM(amount) AS total
                FROM expenses
                WHERE group_id = %s
                GROUP BY paid_by
            """, (gid,))
            paid_map = {r['user_id']: Decimal(str(r['total'])) for r in cursor.fetchall()}

            # Group shares
            cursor.execute("""
                SELECT es.user_id, SUM(es.share_amount) AS total
                FROM expense_splits es
                JOIN expenses e ON es.expense_id = e.id
                WHERE e.group_id = %s
                GROUP BY es.user_id
            """, (gid,))
            share_map = {r['user_id']: Decimal(str(r['total'])) for r in cursor.fetchall()}

            net_map = {}
            for m in g_members:
                uid = m['id']
                p = paid_map.get(uid, Decimal('0.00'))
                s = share_map.get(uid, Decimal('0.00'))
                net_map[uid] = p - s

            settlements = simplify_debts(net_map, member_dict)
            group_settlements.append({
                'group_id': gid,
                'group_name': g['name'],
                'settlements': settlements,
                'my_net': net_map.get(user_id, Decimal('0.00'))
            })

    # Calculate overall receivable and payable for current user
    owed_to_others = Decimal('0.00')
    receivable_from_others = Decimal('0.00')

    for gs in group_settlements:
        for s in gs['settlements']:
            if s['debtor_id'] == user_id:
                owed_to_others += s['amount']
            elif s['creditor_id'] == user_id:
                receivable_from_others += s['amount']

    return render_template(
        'balances.html',
        total_paid=total_paid,
        total_share=total_share,
        net_balance=net_balance,
        owed_to_others=owed_to_others,
        receivable_from_others=receivable_from_others,
        user_status=user_status,
        group_settlements=group_settlements
    )
