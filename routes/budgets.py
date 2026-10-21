from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db
from routes.auth_utils import login_required, validate_csrf
from routes.groups import calculate_group_budget_status

budgets_bp = Blueprint('budgets', __name__, url_prefix='/budgets')

@budgets_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    db = get_db()

    with db.cursor() as cursor:
        cursor.execute("""
            SELECT g.id, g.name, g.description, gm.role,
                   COALESCE(gb.monthly_budget, 0.00) AS monthly_budget,
                   COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) AS total_spent
            FROM `groups` g
            JOIN group_members gm ON g.id = gm.group_id
            LEFT JOIN group_budgets gb ON g.id = gb.group_id
            WHERE gm.user_id = %s
            ORDER BY g.name ASC
        """, (user_id,))
        groups_raw = cursor.fetchall()

    group_budgets = []
    for g in groups_raw:
        budget_info = calculate_group_budget_status(g['monthly_budget'], g['total_spent'])
        group_budgets.append({
            'group_id': g['id'],
            'group_name': g['name'],
            'description': g['description'],
            'role': g['role'],
            **budget_info
        })

    return render_template('budgets.html', group_budgets=group_budgets)

@budgets_bp.route('/update', methods=['POST'])
@login_required
def update():
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf(csrf_token):
        flash('Invalid security token.', 'danger')
        return redirect(url_for('budgets.index'))

    user_id = session['user_id']
    group_id = request.form.get('group_id', type=int)
    monthly_budget_str = request.form.get('monthly_budget', '0').strip()

    if not group_id:
        flash('Invalid group selected.', 'danger')
        return redirect(url_for('budgets.index'))

    try:
        monthly_budget = Decimal(monthly_budget_str)
        if monthly_budget < 0:
            flash('Budget amount cannot be negative.', 'danger')
            return redirect(url_for('budgets.index'))
    except Exception:
        flash('Please enter a valid numeric budget.', 'danger')
        return redirect(url_for('budgets.index'))

    db = get_db()
    try:
        with db.cursor() as cursor:
            # Check user is member of this group
            cursor.execute("SELECT id FROM group_members WHERE group_id = %s AND user_id = %s", (group_id, user_id))
            if not cursor.fetchone():
                flash('You do not have permission to manage this group budget.', 'danger')
                return redirect(url_for('budgets.index'))

            cursor.execute("""
                INSERT INTO group_budgets (group_id, monthly_budget)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE monthly_budget = %s
            """, (group_id, monthly_budget, monthly_budget))
        db.commit()
        flash('Group budget updated successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Failed to update budget: {str(e)}', 'danger')

    return redirect(url_for('budgets.index'))
