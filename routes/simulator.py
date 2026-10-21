from decimal import Decimal, ROUND_HALF_UP
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from db import get_db
from routes.auth_utils import login_required, validate_csrf
from routes.groups import calculate_group_budget_status

simulator_bp = Blueprint('simulator', __name__, url_prefix='/simulator')

@simulator_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = session['user_id']
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT g.id, g.name
            FROM `groups` g
            JOIN group_members gm ON g.id = gm.group_id
            WHERE gm.user_id = %s
            ORDER BY g.name ASC
        """, (user_id,))
        user_groups = cursor.fetchall()

    return render_template('simulator.html', user_groups=user_groups)

@simulator_bp.route('/api/simulate', methods=['POST'])
@login_required
def simulate():
    """
    JSON API for running a simulation without saving any data.
    Returns projected shares, budget comparisons, and warning status.
    """
    user_id = session['user_id']
    data = request.get_json() or {}

    group_id = data.get('group_id')
    amount_val = data.get('amount')
    split_type = (data.get('split_type') or 'EQUAL').upper()
    participants = data.get('participants') or [] # list of {user_id, percentage, custom_amount}

    if not group_id or not amount_val or not participants:
        return jsonify({'error': 'Missing required fields for simulation.'}), 400

    try:
        amount = Decimal(str(amount_val)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than zero.'}), 400
    except Exception:
        return jsonify({'error': 'Invalid numeric amount.'}), 400

    db = get_db()
    with db.cursor() as cursor:
        # Check authorization
        cursor.execute("SELECT id FROM group_members WHERE group_id = %s AND user_id = %s", (group_id, user_id))
        if not cursor.fetchone():
            return jsonify({'error': 'Unauthorized for this group.'}), 403

        # Get group info, members, and budget
        cursor.execute("""
            SELECT g.id, g.name,
                   COALESCE(gb.monthly_budget, 0.00) AS monthly_budget,
                   COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) AS current_spent
            FROM `groups` g
            LEFT JOIN group_budgets gb ON g.id = gb.group_id
            WHERE g.id = %s
        """, (group_id,))
        group_data = cursor.fetchone()

        cursor.execute("""
            SELECT u.id, u.name
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = %s
        """, (group_id,))
        member_map = {m['id']: m['name'] for m in cursor.fetchall()}

    # Calculate splits
    simulated_shares = []
    num_p = len(participants)

    if split_type == 'EQUAL':
        base = (amount / Decimal(num_p)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        diff = amount - (base * num_p)
        for idx, p in enumerate(participants):
            pid = int(p['user_id'])
            share = base + (diff if idx == 0 else Decimal('0.00'))
            simulated_shares.append({
                'user_id': pid,
                'name': member_map.get(pid, f'User #{pid}'),
                'share': float(share),
                'percentage': round(100.0 / num_p, 1)
            })
    elif split_type == 'PERCENTAGE':
        total_pct = Decimal('0.00')
        for p in participants:
            total_pct += Decimal(str(p.get('percentage', 0)))
        if abs(total_pct - Decimal('100.00')) > Decimal('0.1'):
            return jsonify({'error': f'Total percentage must equal 100%. Current sum: {total_pct}%'}), 400

        acc = Decimal('0.00')
        for idx, p in enumerate(participants):
            pid = int(p['user_id'])
            pct = Decimal(str(p.get('percentage', 0)))
            if idx == num_p - 1:
                share = amount - acc
            else:
                share = (amount * (pct / Decimal('100.00'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                acc += share
            simulated_shares.append({
                'user_id': pid,
                'name': member_map.get(pid, f'User #{pid}'),
                'share': float(share),
                'percentage': float(pct)
            })
    elif split_type == 'CUSTOM':
        custom_total = Decimal('0.00')
        for p in participants:
            pid = int(p['user_id'])
            share = Decimal(str(p.get('custom_amount', 0))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            custom_total += share
            simulated_shares.append({
                'user_id': pid,
                'name': member_map.get(pid, f'User #{pid}'),
                'share': float(share),
                'percentage': round(float((share / amount) * 100), 1) if amount > 0 else 0
            })
        if custom_total != amount:
            return jsonify({'error': f'Custom shares sum (₹{custom_total:,.2f}) must match total amount (₹{amount:,.2f}).'}), 400

    # Budget projections
    current_spent = Decimal(str(group_data['current_spent']))
    budget = Decimal(str(group_data['monthly_budget']))
    projected_spent = current_spent + amount

    current_status = calculate_group_budget_status(budget, current_spent)
    projected_status = calculate_group_budget_status(budget, projected_spent)

    budget_exceeded = (projected_spent > budget) if budget > 0 else False

    return jsonify({
        'group_name': group_data['name'],
        'expense_amount': float(amount),
        'simulated_shares': simulated_shares,
        'current_spending': float(current_spent),
        'projected_spending': float(projected_spent),
        'monthly_budget': float(budget),
        'current_remaining': float(current_status['remaining']),
        'projected_remaining': float(projected_status['remaining']),
        'current_percent': current_status['percent'],
        'projected_percent': projected_status['percent'],
        'current_status': current_status['status'],
        'projected_status': projected_status['status'],
        'projected_badge': projected_status['badge_class'],
        'budget_exceeded': budget_exceeded
    })
