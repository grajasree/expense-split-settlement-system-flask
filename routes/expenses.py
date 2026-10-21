from decimal import Decimal, ROUND_HALF_UP
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from db import get_db
from routes.auth_utils import login_required, validate_csrf

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

CATEGORIES = [
    'Food & Dining',
    'Transportation',
    'Shopping',
    'Utilities & Bills',
    'Entertainment',
    'Housing & Rent',
    'Healthcare',
    'Groceries',
    'Travel',
    'Other'
]

@expenses_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    selected_group_id = request.args.get('group_id', type=int)
    category_filter = request.args.get('category', '').strip()

    db = get_db()
    with db.cursor() as cursor:
        # Get all groups user belongs to (for filter dropdown)
        cursor.execute("""
            SELECT g.id, g.name
            FROM `groups` g
            JOIN group_members gm ON g.id = gm.group_id
            WHERE gm.user_id = %s
            ORDER BY g.name ASC
        """, (user_id,))
        user_groups = cursor.fetchall()
        user_group_ids = [g['id'] for g in user_groups]

        if not user_group_ids:
            return render_template(
                'expenses.html',
                expenses=[],
                user_groups=[],
                selected_group_id=None,
                category_filter='',
                categories=CATEGORIES
            )

        # Base query for expenses
        query = """
            SELECT e.id, e.description, e.amount, e.category, e.date, e.split_type,
                   e.group_id, g.name AS group_name,
                   e.paid_by, u.name AS payer_name,
                   COALESCE(es.share_amount, 0.00) AS my_share,
                   (SELECT COUNT(*) FROM expense_splits WHERE expense_id = e.id) AS participant_count
            FROM expenses e
            JOIN `groups` g ON e.group_id = g.id
            JOIN users u ON e.paid_by = u.id
            LEFT JOIN expense_splits es ON e.id = es.expense_id AND es.user_id = %s
            WHERE e.group_id IN ({})
        """.format(','.join(['%s'] * len(user_group_ids)))

        params = [user_id] + user_group_ids

        if selected_group_id and selected_group_id in user_group_ids:
            query += " AND e.group_id = %s"
            params.append(selected_group_id)

        if category_filter and category_filter in CATEGORIES:
            query += " AND e.category = %s"
            params.append(category_filter)

        query += " ORDER BY e.date DESC, e.id DESC"

        cursor.execute(query, tuple(params))
        expenses = cursor.fetchall()

    return render_template(
        'expenses.html',
        expenses=expenses,
        user_groups=user_groups,
        selected_group_id=selected_group_id,
        category_filter=category_filter,
        categories=CATEGORIES
    )

@expenses_bp.route('/api/group-members/<int:group_id>')
@login_required
def get_group_members(group_id):
    """
    JSON API for dynamic frontend selection of group participants.
    """
    user_id = session['user_id']
    db = get_db()
    with db.cursor() as cursor:
        # Check authorization
        cursor.execute("SELECT id FROM group_members WHERE group_id = %s AND user_id = %s", (group_id, user_id))
        if not cursor.fetchone():
            return jsonify({'error': 'Unauthorized'}), 403

        cursor.execute("""
            SELECT u.id, u.name, u.email
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = %s
            ORDER BY u.name ASC
        """, (group_id,))
        members = cursor.fetchall()

    return jsonify({'members': members})

@expenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    user_id = session['user_id']
    db = get_db()

    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf(csrf_token):
            flash('Invalid security token.', 'danger')
            return redirect(url_for('expenses.add'))

        group_id = request.form.get('group_id', type=int)
        description = request.form.get('description', '').strip()
        amount_str = request.form.get('amount', '').strip()
        category = request.form.get('category', 'Other')
        date = request.form.get('date', '').strip()
        paid_by = request.form.get('paid_by', type=int)
        split_type = request.form.get('split_type', 'EQUAL').upper()
        participant_ids = request.form.getlist('participants', type=int)

        # Basic validations
        if not group_id or not description or not amount_str or not date or not paid_by:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('expenses.add', group_id=group_id))

        if not participant_ids:
            flash('Please select at least one participant sharing this expense.', 'danger')
            return redirect(url_for('expenses.add', group_id=group_id))

        try:
            total_amount = Decimal(amount_str).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if total_amount <= Decimal('0.00'):
                flash('Expense amount must be greater than zero.', 'danger')
                return redirect(url_for('expenses.add', group_id=group_id))
        except Exception:
            flash('Please enter a valid numeric amount.', 'danger')
            return redirect(url_for('expenses.add', group_id=group_id))

        # Check membership of user, payer, and participants
        with db.cursor() as cursor:
            cursor.execute("SELECT user_id FROM group_members WHERE group_id = %s", (group_id,))
            valid_member_ids = {row['user_id'] for row in cursor.fetchall()}

        if user_id not in valid_member_ids:
            flash('You are not authorized to add expenses to this group.', 'danger')
            return redirect(url_for('groups.index'))

        if paid_by not in valid_member_ids:
            flash('Selected payer is not a member of the group.', 'danger')
            return redirect(url_for('expenses.add', group_id=group_id))

        for pid in participant_ids:
            if pid not in valid_member_ids:
                flash('One or more selected participants do not belong to the group.', 'danger')
                return redirect(url_for('expenses.add', group_id=group_id))

        # Calculate splits based on split method
        splits = [] # list of (user_id, share_amount, share_percentage)

        if split_type == 'EQUAL':
            num_participants = len(participant_ids)
            base_share = (total_amount / Decimal(num_participants)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            calculated_total = base_share * num_participants
            diff = total_amount - calculated_total

            for idx, pid in enumerate(participant_ids):
                # Adjust rounding cent/paisa on first participant
                share = base_share + (diff if idx == 0 else Decimal('0.00'))
                pct = round(100.0 / num_participants, 2)
                splits.append((pid, share, pct))

        elif split_type == 'PERCENTAGE':
            total_pct = Decimal('0.00')
            pct_dict = {}
            for pid in participant_ids:
                pct_str = request.form.get(f'percentage_{pid}', '0').strip()
                try:
                    pct = Decimal(pct_str)
                    if pct < 0:
                        raise ValueError()
                    pct_dict[pid] = pct
                    total_pct += pct
                except Exception:
                    flash(f'Please enter a valid percentage for all participants.', 'danger')
                    return redirect(url_for('expenses.add', group_id=group_id))

            if abs(total_pct - Decimal('100.00')) > Decimal('0.1'):
                flash(f'Total percentage must equal 100%. Current sum: {total_pct}%', 'danger')
                return redirect(url_for('expenses.add', group_id=group_id))

            # Compute shares
            accumulated = Decimal('0.00')
            for idx, pid in enumerate(participant_ids):
                pct = pct_dict[pid]
                if idx == len(participant_ids) - 1:
                    # Last person gets the remaining to guarantee exact sum match
                    share = total_amount - accumulated
                else:
                    share = (total_amount * (pct / Decimal('100.00'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    accumulated += share
                splits.append((pid, share, float(pct)))

        elif split_type == 'CUSTOM':
            custom_total = Decimal('0.00')
            for pid in participant_ids:
                amt_str = request.form.get(f'custom_amount_{pid}', '0').strip()
                try:
                    share = Decimal(amt_str).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    if share < 0:
                        raise ValueError()
                    splits.append((pid, share, None))
                    custom_total += share
                except Exception:
                    flash('Please enter a valid amount for all participants.', 'danger')
                    return redirect(url_for('expenses.add', group_id=group_id))

            if custom_total != total_amount:
                flash(f'Sum of custom amounts (₹{custom_total:,.2f}) must exactly match total expense (₹{total_amount:,.2f}).', 'danger')
                return redirect(url_for('expenses.add', group_id=group_id))
        else:
            flash('Invalid split type selected.', 'danger')
            return redirect(url_for('expenses.add', group_id=group_id))

        # Save to Database in a transaction
        try:
            with db.cursor() as cursor:
                # 1. Insert expense record
                cursor.execute("""
                    INSERT INTO expenses (group_id, paid_by, description, amount, category, date, split_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (group_id, paid_by, description, total_amount, category, date, split_type))
                expense_id = cursor.lastrowid

                # 2. Insert individual splits
                for pid, share_amt, share_pct in splits:
                    cursor.execute("""
                        INSERT INTO expense_splits (expense_id, user_id, share_amount, share_percentage)
                        VALUES (%s, %s, %s, %s)
                    """, (expense_id, pid, share_amt, share_pct))

                # 3. Check budget status and generate warning if needed
                cursor.execute("SELECT monthly_budget FROM group_budgets WHERE group_id = %s", (group_id,))
                budget_row = cursor.fetchone()
                if budget_row and budget_row['monthly_budget'] > 0:
                    budget = Decimal(str(budget_row['monthly_budget']))
                    cursor.execute("SELECT SUM(amount) AS total FROM expenses WHERE group_id = %s", (group_id,))
                    new_total = cursor.fetchone()['total'] or Decimal('0.00')
                    pct_used = (new_total / budget) * 100
                    if pct_used >= 100:
                        flash(f"⚠️ Budget Alert: Group spending (₹{new_total:,.2f}) has EXCEEDED the monthly budget (₹{budget:,.2f})!", 'danger')
                    elif pct_used >= 90:
                        flash(f"⚠️ High Spending Alert: Group has used {pct_used:.1f}% of its monthly budget!", 'warning')
                    elif pct_used >= 75:
                        flash(f"ℹ️ Budget Warning: Group has reached {pct_used:.1f}% of its monthly budget.", 'info')

            db.commit()
            flash(f"Expense '{description}' (₹{total_amount:,.2f}) added successfully!", 'success')
            return redirect(url_for('groups.details', group_id=group_id))
        except Exception as e:
            db.rollback()
            flash(f'Failed to record expense: {str(e)}', 'danger')
            return redirect(url_for('expenses.add', group_id=group_id))

    # GET Request: Prepare form data
    preset_group_id = request.args.get('group_id', type=int)
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT g.id, g.name
            FROM `groups` g
            JOIN group_members gm ON g.id = gm.group_id
            WHERE gm.user_id = %s
            ORDER BY g.name ASC
        """, (user_id,))
        user_groups = cursor.fetchall()

    return render_template(
        'add_expense.html',
        user_groups=user_groups,
        preset_group_id=preset_group_id,
        categories=CATEGORIES
    )

@expenses_bp.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit(expense_id):
    user_id = session['user_id']
    db = get_db()

    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM expenses WHERE id = %s", (expense_id,))
        expense = cursor.fetchone()
        if not expense:
            flash('Expense not found.', 'danger')
            return redirect(url_for('expenses.index'))

        group_id = expense['group_id']
        # Check authorization
        cursor.execute("SELECT id FROM group_members WHERE group_id = %s AND user_id = %s", (group_id, user_id))
        if not cursor.fetchone():
            flash('You do not have permission to edit this expense.', 'danger')
            return redirect(url_for('expenses.index'))

        cursor.execute("""
            SELECT u.id, u.name, u.email
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = %s
            ORDER BY u.name ASC
        """, (group_id,))
        group_members = cursor.fetchall()

        cursor.execute("SELECT * FROM expense_splits WHERE expense_id = %s", (expense_id,))
        existing_splits = {row['user_id']: row for row in cursor.fetchall()}

    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf(csrf_token):
            flash('Invalid security token.', 'danger')
            return redirect(url_for('expenses.edit', expense_id=expense_id))

        description = request.form.get('description', '').strip()
        amount_str = request.form.get('amount', '').strip()
        category = request.form.get('category', 'Other')
        date = request.form.get('date', '').strip()
        paid_by = request.form.get('paid_by', type=int)
        split_type = request.form.get('split_type', 'EQUAL').upper()
        participant_ids = request.form.getlist('participants', type=int)

        if not description or not amount_str or not date or not paid_by or not participant_ids:
            flash('Please fill in all required fields and select participants.', 'danger')
            return redirect(url_for('expenses.edit', expense_id=expense_id))

        try:
            total_amount = Decimal(amount_str).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if total_amount <= 0:
                flash('Amount must be positive.', 'danger')
                return redirect(url_for('expenses.edit', expense_id=expense_id))
        except Exception:
            flash('Invalid numeric amount.', 'danger')
            return redirect(url_for('expenses.edit', expense_id=expense_id))

        # Calculate new splits
        splits = []
        if split_type == 'EQUAL':
            num_participants = len(participant_ids)
            base_share = (total_amount / Decimal(num_participants)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            diff = total_amount - (base_share * num_participants)
            for idx, pid in enumerate(participant_ids):
                share = base_share + (diff if idx == 0 else Decimal('0.00'))
                splits.append((pid, share, round(100.0 / num_participants, 2)))
        elif split_type == 'PERCENTAGE':
            total_pct = Decimal('0.00')
            pct_dict = {}
            for pid in participant_ids:
                p_str = request.form.get(f'percentage_{pid}', '0').strip()
                try:
                    p = Decimal(p_str)
                    pct_dict[pid] = p
                    total_pct += p
                except Exception:
                    flash('Invalid percentage values.', 'danger')
                    return redirect(url_for('expenses.edit', expense_id=expense_id))
            if abs(total_pct - Decimal('100.00')) > Decimal('0.1'):
                flash(f'Total percentage must equal 100%. Currently: {total_pct}%', 'danger')
                return redirect(url_for('expenses.edit', expense_id=expense_id))
            accumulated = Decimal('0.00')
            for idx, pid in enumerate(participant_ids):
                if idx == len(participant_ids) - 1:
                    share = total_amount - accumulated
                else:
                    share = (total_amount * (pct_dict[pid] / Decimal('100.00'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    accumulated += share
                splits.append((pid, share, float(pct_dict[pid])))
        elif split_type == 'CUSTOM':
            custom_total = Decimal('0.00')
            for pid in participant_ids:
                c_str = request.form.get(f'custom_amount_{pid}', '0').strip()
                try:
                    share = Decimal(c_str).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    splits.append((pid, share, None))
                    custom_total += share
                except Exception:
                    flash('Invalid custom amounts.', 'danger')
                    return redirect(url_for('expenses.edit', expense_id=expense_id))
            if custom_total != total_amount:
                flash(f'Sum of custom amounts must equal total expense.', 'danger')
                return redirect(url_for('expenses.edit', expense_id=expense_id))

        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    UPDATE expenses
                    SET description = %s, amount = %s, category = %s, date = %s, paid_by = %s, split_type = %s
                    WHERE id = %s
                """, (description, total_amount, category, date, paid_by, split_type, expense_id))

                cursor.execute("DELETE FROM expense_splits WHERE expense_id = %s", (expense_id,))

                for pid, share_amt, share_pct in splits:
                    cursor.execute("""
                        INSERT INTO expense_splits (expense_id, user_id, share_amount, share_percentage)
                        VALUES (%s, %s, %s, %s)
                    """, (expense_id, pid, share_amt, share_pct))
            db.commit()
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('groups.details', group_id=group_id))
        except Exception as e:
            db.rollback()
            flash(f'Update failed: {str(e)}', 'danger')

    return render_template(
        'edit_expense.html',
        expense=expense,
        group_members=group_members,
        existing_splits=existing_splits,
        categories=CATEGORIES
    )

@expenses_bp.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete(expense_id):
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf(csrf_token):
        flash('Invalid security token.', 'danger')
        return redirect(url_for('expenses.index'))

    user_id = session['user_id']
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT group_id FROM expenses WHERE id = %s", (expense_id,))
            expense = cursor.fetchone()
            if not expense:
                flash('Expense not found.', 'danger')
                return redirect(url_for('expenses.index'))

            group_id = expense['group_id']
            # Check user belongs to group
            cursor.execute("SELECT id FROM group_members WHERE group_id = %s AND user_id = %s", (group_id, user_id))
            if not cursor.fetchone():
                flash('Unauthorized to delete this expense.', 'danger')
                return redirect(url_for('expenses.index'))

            cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        db.commit()
        flash('Expense deleted successfully.', 'info')
        return redirect(url_for('groups.details', group_id=group_id))
    except Exception as e:
        db.rollback()
        flash(f'Failed to delete expense: {str(e)}', 'danger')
        return redirect(url_for('expenses.index'))
