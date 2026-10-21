"""
Expense Split and Settlement System - Streamlit Web Edition
Modern Purple & White Theme • Full MySQL Support with Cloud Fallback • Interactive Visualizations
"""

import os
import re
from decimal import Decimal, ROUND_HALF_UP
import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load environment configuration if available
from dotenv import load_dotenv
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SplitSettlement - Expense Split & Settlement",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Purple-and-White Theme Styling
st.markdown("""
<style>
    :root {
        --primary-color: #6c5ce7;
        --secondary-color: #a29bfe;
        --bg-color: #f8f9fa;
        --card-bg: #ffffff;
    }
    .main {
        background-color: #f8f9fa;
    }
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(108, 92, 231, 0.06);
        border-left: 4px solid #6c5ce7;
    }
    /* Primary Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #6c5ce7 0%, #8e44ad 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        opacity: 0.92;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
    }
    /* Headers */
    h1, h2, h3 {
        color: #2d3436;
        font-family: 'Segoe UI', -apple-system, sans-serif;
    }
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-normal { background-color: #e6f9f4; color: #00b894; border: 1px solid #00b894; }
    .badge-warning { background-color: #fff9e6; color: #d35400; border: 1px solid #fdcb6e; }
    .badge-alert { background-color: #fdeee9; color: #e17055; border: 1px solid #e17055; }
    .badge-exceeded { background-color: #fdeaea; color: #d63031; border: 1px solid #d63031; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATABASE ABSTRACTION (MySQL with SQLite Cloud Fallback)
# ==============================================================================
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Mysql@1234')
DB_NAME = os.getenv('DB_NAME', 'expense_settlement_db')

# Override with Streamlit secrets if hosted on Streamlit Cloud
if hasattr(st, 'secrets') and 'DB_PASSWORD' in st.secrets:
    DB_PASSWORD = st.secrets['DB_PASSWORD']
    DB_HOST = st.secrets.get('DB_HOST', DB_HOST)
    DB_USER = st.secrets.get('DB_USER', DB_USER)
    DB_NAME = st.secrets.get('DB_NAME', DB_NAME)

@st.cache_resource
def init_connection():
    """Attempt MySQL connection; fallback to SQLite if hosted remotely without MySQL access."""
    try:
        import pymysql
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return 'mysql', conn
    except Exception as e:
        # Fallback to local SQLite instance for standalone Streamlit Cloud preview
        import sqlite3
        sqlite_path = os.path.join(os.path.dirname(__file__), 'cloud_demo.db')
        conn = sqlite3.connect(sqlite_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        setup_sqlite_schema(conn)
        return 'sqlite', conn

def setup_sqlite_schema(conn):
    """Create equivalent SQLite schema and populate demo records if empty."""
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT DEFAULT 'member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS group_budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL UNIQUE,
            monthly_budget REAL NOT NULL DEFAULT 0.00
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            paid_by INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            split_type TEXT DEFAULT 'EQUAL'
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expense_splits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            share_amount REAL NOT NULL,
            share_percentage REAL
        );
    """)
    conn.commit()

    # Seed demo users if empty
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users (name, email, password_hash) VALUES ('Rahul Sharma', 'rahul@example.com', 'demo')")
        cur.execute("INSERT INTO users (name, email, password_hash) VALUES ('Priya Patel', 'priya@example.com', 'demo')")
        cur.execute("INSERT INTO users (name, email, password_hash) VALUES ('Amit Kumar', 'amit@example.com', 'demo')")
        cur.execute("INSERT INTO users (name, email, password_hash) VALUES ('Sneha Rao', 'sneha@example.com', 'demo')")
        
        cur.execute("INSERT INTO groups_table (name, description, created_by) VALUES ('Apartment 402 - Flatmates', 'Flat rent and groceries', 1)")
        cur.execute("INSERT INTO groups_table (name, description, created_by) VALUES ('Weekend Goa Trip', 'Beach vacation and dining', 2)")
        
        cur.execute("INSERT INTO group_budgets (group_id, monthly_budget) VALUES (1, 20000.00)")
        cur.execute("INSERT INTO group_budgets (group_id, monthly_budget) VALUES (2, 15000.00)")

        for uid in [1, 2, 3]:
            cur.execute("INSERT INTO group_members (group_id, user_id, role) VALUES (1, ?, 'member')", (uid,))
        for uid in [1, 2, 3, 4]:
            cur.execute("INSERT INTO group_members (group_id, user_id, role) VALUES (2, ?, 'member')", (uid,))

        # Expenses
        cur.execute("INSERT INTO expenses (group_id, paid_by, description, amount, category, date, split_type) VALUES (1, 1, 'Monthly Supermarket Groceries', 3000.0, 'Groceries', '2026-10-05', 'EQUAL')")
        for uid in [1, 2, 3]:
            cur.execute("INSERT INTO expense_splits (expense_id, user_id, share_amount, share_percentage) VALUES (1, ?, 1000.0, 33.33)", (uid,))

        cur.execute("INSERT INTO expenses (group_id, paid_by, description, amount, category, date, split_type) VALUES (1, 2, 'Electricity & WiFi Bill', 1800.0, 'Utilities & Bills', '2026-10-08', 'EQUAL')")
        for uid in [1, 2, 3]:
            cur.execute("INSERT INTO expense_splits (expense_id, user_id, share_amount, share_percentage) VALUES (2, ?, 600.0, 33.33)", (uid,))

        cur.execute("INSERT INTO expenses (group_id, paid_by, description, amount, category, date, split_type) VALUES (2, 2, 'Beachside Villa Booking', 9000.0, 'Travel', '2026-10-15', 'CUSTOM')")
        cur.execute("INSERT INTO expense_splits (expense_id, user_id, share_amount) VALUES (3, 1, 2500.0)")
        cur.execute("INSERT INTO expense_splits (expense_id, user_id, share_amount) VALUES (3, 2, 2500.0)")
        cur.execute("INSERT INTO expense_splits (expense_id, user_id, share_amount) VALUES (3, 3, 2000.0)")
        cur.execute("INSERT INTO expense_splits (expense_id, user_id, share_amount) VALUES (3, 4, 2000.0)")

        cur.execute("INSERT INTO expenses (group_id, paid_by, description, amount, category, date, split_type) VALUES (2, 4, 'Fisherman Wharf Seafood Dinner', 3600.0, 'Food & Dining', '2026-10-17', 'EQUAL')")
        for uid in [1, 2, 3, 4]:
            cur.execute("INSERT INTO expense_splits (expense_id, user_id, share_amount, share_percentage) VALUES (4, ?, 900.0, 25.0)", (uid,))

        conn.commit()

db_type, db_conn = init_connection()

def run_query(sql, params=None):
    """Execute SQL query safely across MySQL or SQLite."""
    # Handle table name difference: MySQL `groups`, SQLite groups_table
    if db_type == 'sqlite':
        sql = sql.replace('`groups`', 'groups_table').replace('groups g', 'groups_table g')
        cur = db_conn.cursor()
        if params:
            cur.execute(sql.replace('%s', '?'), params)
        else:
            cur.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        return rows
    else:
        # MySQL
        import pymysql
        try:
            db_conn.ping(reconnect=True)
        except Exception:
            pass
        with db_conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()

def execute_cmd(sql, params=None):
    """Execute insert/update/delete."""
    if db_type == 'sqlite':
        sql = sql.replace('`groups`', 'groups_table').replace('groups g', 'groups_table g')
        cur = db_conn.cursor()
        if params:
            cur.execute(sql.replace('%s', '?'), params)
        else:
            cur.execute(sql)
        db_conn.commit()
        return cur.lastrowid
    else:
        try:
            db_conn.ping(reconnect=True)
        except Exception:
            pass
        with db_conn.cursor() as cur:
            cur.execute(sql, params or ())
            db_conn.commit()
            return cur.lastrowid

# ==============================================================================
# DEBT SIMPLIFICATION ALGORITHM (Who Owes Whom)
# ==============================================================================
def simplify_debts(net_balances, member_dict):
    debtors = []   # net < 0 (owes money)
    creditors = [] # net > 0 (gets back money)

    for uid, net in net_balances.items():
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

        settled = min(debtor['amount'], creditor['amount'])
        if settled > Decimal('0.01'):
            settlements.append({
                'debtor_id': debtor['user_id'],
                'debtor_name': debtor['name'],
                'creditor_id': creditor['user_id'],
                'creditor_name': creditor['name'],
                'amount': float(settled)
            })

        debtor['amount'] -= settled
        creditor['amount'] -= settled

        if debtor['amount'] <= Decimal('0.01'):
            d_idx += 1
        if creditor['amount'] <= Decimal('0.01'):
            c_idx += 1

    return settlements

# ==============================================================================
# SIDEBAR: USER & NAVIGATION
# ==============================================================================
st.sidebar.markdown("### 💳 SplitSettlement")
st.sidebar.caption(f"Connected to: **{db_type.upper()}** ({DB_NAME if db_type=='mysql' else 'Local Cloud Engine'})")

# Language Selector
lang = st.sidebar.selectbox("Language / ಭಾಷೆ / భాష / भाषा", ["English", "ಕನ್ನಡ (Kannada)", "తెలుగు (Telugu)", "हिन्दी (Hindi)"])

# User Selection (Active Session)
all_users = run_query("SELECT id, name, email FROM users ORDER BY name ASC")
if not all_users:
    st.error("No registered users found. Please register an account.")
    st.stop()

user_map = {f"{u['name']} ({u['email']})": u['id'] for u in all_users}
selected_user_label = st.sidebar.selectbox("👤 Active User Account:", list(user_map.keys()))
current_user_id = user_map[selected_user_label]
current_user_name = selected_user_label.split(' (')[0]

menu = st.sidebar.radio(
    "Navigation Menu:",
    [
        "📊 Dashboard & Analytics",
        "👥 Groups & Members",
        "🧾 Expenses & Splits",
        "⚖️ Balances (Who Owes Whom)",
        "🐷 Group Budgets",
        "🧪 What-If Simulator"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Expense Split and Settlement System • Academic Project Edition")

# ==============================================================================
# 1. DASHBOARD & ANALYTICS
# ==============================================================================
if menu == "📊 Dashboard & Analytics":
    st.title("Financial Overview")
    st.caption("Track group expenses, individual balances, and real-time budget usage.")

    # Fetch user groups
    user_groups = run_query("""
        SELECT g.id, g.name,
               COALESCE(gb.monthly_budget, 0.00) AS monthly_budget,
               COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) AS total_spent
        FROM `groups` g
        JOIN group_members gm ON g.id = gm.group_id
        LEFT JOIN group_budgets gb ON g.id = gb.group_id
        WHERE gm.user_id = %s
    """, (current_user_id,))

    if not user_groups:
        st.info("You are not part of any group yet. Navigate to 'Groups & Members' to create or join one!")
    else:
        group_ids = [g['id'] for g in user_groups]
        format_p = ','.join(['%s'] * len(group_ids))

        # Metrics
        total_group_exp = run_query(f"SELECT COALESCE(SUM(amount), 0.00) as val FROM expenses WHERE group_id IN ({format_p})", group_ids)[0]['val']
        total_paid = run_query(f"SELECT COALESCE(SUM(amount), 0.00) as val FROM expenses WHERE paid_by = %s AND group_id IN ({format_p})", [current_user_id] + group_ids)[0]['val']
        my_share = run_query(f"""
            SELECT COALESCE(SUM(es.share_amount), 0.00) as val
            FROM expense_splits es
            JOIN expenses e ON es.expense_id = e.id
            WHERE es.user_id = %s AND e.group_id IN ({format_p})
        """, [current_user_id] + group_ids)[0]['val']

        # Simplified debts across groups
        user_owes = 0.0
        others_owe = 0.0

        for g in user_groups:
            gid = g['id']
            members = run_query("SELECT u.id, u.name FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s", (gid,))
            m_dict = {m['id']: m['name'] for m in members}
            paid_rows = {r['user_id']: float(r['val']) for r in run_query("SELECT paid_by as user_id, SUM(amount) as val FROM expenses WHERE group_id = %s GROUP BY paid_by", (gid,))}
            share_rows = {r['user_id']: float(r['val']) for r in run_query("SELECT es.user_id, SUM(es.share_amount) as val FROM expense_splits es JOIN expenses e ON es.expense_id = e.id WHERE e.group_id = %s GROUP BY es.user_id", (gid,))}
            net_map = {m['id']: paid_rows.get(m['id'], 0.0) - share_rows.get(m['id'], 0.0) for m in members}
            settlements = simplify_debts(net_map, m_dict)
            for s in settlements:
                if s['debtor_id'] == current_user_id:
                    user_owes += s['amount']
                elif s['creditor_id'] == current_user_id:
                    others_owe += s['amount']

        # Check Budget Warnings
        alerts = []
        for g in user_groups:
            b = float(g['monthly_budget'])
            s = float(g['total_spent'])
            if b > 0:
                pct = (s / b) * 100
                if pct >= 100:
                    alerts.append(f"🚨 **{g['name']}** has **EXCEEDED** its monthly budget! Spent ₹{s:,.2f} of ₹{b:,.2f} ({pct:.1f}%)")
                elif pct >= 90:
                    alerts.append(f"⚠️ **High Alert**: **{g['name']}** has used **{pct:.1f}%** of its budget (Spent: ₹{s:,.2f} / ₹{b:,.2f})")
                elif pct >= 75:
                    alerts.append(f"ℹ️ **Warning**: **{g['name']}** is approaching its budget limit at **{pct:.1f}%** usage.")

        for alert in alerts:
            st.warning(alert)

        # 5 Top Metric Cards
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Group Expenses", f"₹{float(total_group_exp):,.2f}")
        c2.metric("Total You Paid", f"₹{float(total_paid):,.2f}")
        c3.metric("You Are Owed", f"₹{others_owe:,.2f}")
        c4.metric("You Owe", f"₹{user_owes:,.2f}")
        c5.metric("Active Groups", len(user_groups))

        st.markdown("---")

        # Interactive Charts Row
        col_left, col_right = st.columns(2)

        # 1. Monthly Spending Trend
        with col_left:
            st.subheader("📈 Monthly Spending Trend")
            month_rows = run_query(f"""
                SELECT substr(date, 1, 7) as month_label, SUM(amount) as total
                FROM expenses
                WHERE group_id IN ({format_p})
                GROUP BY month_label ORDER BY month_label ASC
            """, group_ids)
            if month_rows:
                df_month = pd.DataFrame(month_rows)
                fig_month = px.area(df_month, x='month_label', y='total', labels={'month_label': 'Month', 'total': 'Spent (₹)'}, color_discrete_sequence=['#6c5ce7'])
                fig_month.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
                st.plotly_chart(fig_month, use_container_width=True)
            else:
                st.info("No monthly data recorded yet.")

        # 2. Expense Category Breakdown
        with col_right:
            st.subheader("🍩 Expense Category Breakdown")
            cat_rows = run_query(f"""
                SELECT category, SUM(amount) as total
                FROM expenses
                WHERE group_id IN ({format_p})
                GROUP BY category ORDER BY total DESC
            """, group_ids)
            if cat_rows:
                df_cat = pd.DataFrame(cat_rows)
                fig_cat = px.pie(df_cat, names='category', values='total', hole=0.45, color_discrete_sequence=px.colors.sequential.Purples_r)
                fig_cat.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("No categories recorded yet.")

        col_b1, col_b2 = st.columns(2)
        # 3. Group-wise Spending Comparison
        with col_b1:
            st.subheader("📊 Group-wise Spending")
            df_grp = pd.DataFrame([{'Group': g['name'], 'Spent': float(g['total_spent'])} for g in user_groups])
            fig_grp = px.bar(df_grp, x='Group', y='Spent', color='Group', color_discrete_sequence=['#6c5ce7', '#00b894', '#0984e3'])
            fig_grp.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300, showlegend=False)
            st.plotly_chart(fig_grp, use_container_width=True)

        # 4. Group Budget Usage
        with col_b2:
            st.subheader("⚖️ Budget vs Actual Spent")
            b_data = []
            for g in user_groups:
                b_data.append({'Group': g['name'], 'Type': 'Spent Amount', 'Amount': float(g['total_spent'])})
                b_data.append({'Group': g['name'], 'Type': 'Monthly Budget', 'Amount': float(g['monthly_budget'])})
            df_b = pd.DataFrame(b_data)
            fig_b = px.bar(df_b, x='Group', y='Amount', color='Type', barmode='group', color_discrete_map={'Spent Amount': '#e17055', 'Monthly Budget': '#00b894'})
            fig_b.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
            st.plotly_chart(fig_b, use_container_width=True)

        # Recent Transactions
        st.subheader("🕒 Recent Transactions")
        recent = run_query(f"""
            SELECT e.date as Date, e.description as Description, g.name as Group_Name, e.category as Category,
                   u.name as Paid_By, e.amount as Amount, COALESCE(es.share_amount, 0.0) as My_Share
            FROM expenses e
            JOIN `groups` g ON e.group_id = g.id
            JOIN users u ON e.paid_by = u.id
            LEFT JOIN expense_splits es ON e.id = es.expense_id AND es.user_id = %s
            WHERE e.group_id IN ({format_p})
            ORDER BY e.date DESC LIMIT 6
        """, [current_user_id] + group_ids)
        if recent:
            st.dataframe(pd.DataFrame(recent), use_container_width=True)

# ==============================================================================
# 2. GROUPS & MEMBERS
# ==============================================================================
elif menu == "👥 Groups & Members":
    st.title("Groups & Members Management")

    tab1, tab2 = st.tabs(["📋 View Your Groups", "➕ Create New Group"])

    with tab1:
        my_groups = run_query("""
            SELECT g.id, g.name, g.description,
                   COALESCE(gb.monthly_budget, 0.00) AS monthly_budget,
                   COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) AS total_spent
            FROM `groups` g
            JOIN group_members gm ON g.id = gm.group_id
            LEFT JOIN group_budgets gb ON g.id = gb.group_id
            WHERE gm.user_id = %s
        """, (current_user_id,))

        if not my_groups:
            st.info("You do not belong to any groups yet.")
        else:
            for g in my_groups:
                with st.expander(f"📁 {g['name']} (Spent: ₹{float(g['total_spent']):,.2f} / Budget: ₹{float(g['monthly_budget']):,.2f})", expanded=True):
                    st.write(f"**Description:** {g['description'] or 'No description'}")
                    
                    # Progress bar
                    b = float(g['monthly_budget'])
                    s = float(g['total_spent'])
                    if b > 0:
                        pct = min(s / b, 1.0)
                        st.progress(pct, text=f"Budget Usage: {(s/b)*100:.1f}%")
                    
                    # Member list
                    st.markdown("**Members:**")
                    members = run_query("SELECT u.name, u.email, gm.role FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s", (g['id'],))
                    st.table(pd.DataFrame(members))

                    # Add member by email
                    col_add_email, col_add_btn = st.columns([3, 1])
                    with col_add_email:
                        new_member_email = st.text_input(f"Add Member by Email (Group #{g['id']}):", key=f"email_{g['id']}")
                    with col_add_btn:
                        st.write("")
                        st.write("")
                        if st.button("Add to Group", key=f"btn_add_{g['id']}"):
                            target = run_query("SELECT id, name FROM users WHERE email = %s", (new_member_email.strip().lower(),))
                            if not target:
                                st.error("User not found with this email.")
                            else:
                                exists = run_query("SELECT id FROM group_members WHERE group_id = %s AND user_id = %s", (g['id'], target[0]['id']))
                                if exists:
                                    st.warning("User is already in this group.")
                                else:
                                    execute_cmd("INSERT INTO group_members (group_id, user_id, role) VALUES (%s, %s, 'member')", (g['id'], target[0]['id']))
                                    st.success(f"Added {target[0]['name']} to {g['name']}!")
                                    st.rerun()

    with tab2:
        st.subheader("Create a New Expense Group")
        with st.form("new_group_form"):
            g_name = st.text_input("Group Name *", placeholder="e.g. Manali Road Trip, Apartment 101")
            g_desc = st.text_area("Description (Optional)", placeholder="Shared bills and outing expenses")
            g_budget = st.number_input("Monthly Spending Budget (₹, Optional)", min_value=0.0, step=500.0, value=10000.0)
            submitted = st.form_submit_button("Create Group")

            if submitted:
                if not g_name.strip():
                    st.error("Group name is required.")
                else:
                    new_gid = execute_cmd("INSERT INTO `groups` (name, description, created_by) VALUES (%s, %s, %s)", (g_name.strip(), g_desc.strip(), current_user_id))
                    execute_cmd("INSERT INTO group_members (group_id, user_id, role) VALUES (%s, %s, 'creator')", (new_gid, current_user_id))
                    if g_budget > 0:
                        execute_cmd("INSERT INTO group_budgets (group_id, monthly_budget) VALUES (%s, %s)", (new_gid, g_budget))
                    st.success(f"Group '{g_name}' created successfully!")
                    st.rerun()

# ==============================================================================
# 3. EXPENSES & SPLITS
# ==============================================================================
elif menu == "🧾 Expenses & Splits":
    st.title("Expense Management & Bill Splitting")

    tab1, tab2 = st.tabs(["➕ Add New Expense", "📜 Expense History"])

    user_groups = run_query("""
        SELECT g.id, g.name FROM `groups` g
        JOIN group_members gm ON g.id = gm.group_id WHERE gm.user_id = %s
    """, (current_user_id,))

    CATEGORIES = ['Food & Dining', 'Transportation', 'Shopping', 'Utilities & Bills', 'Entertainment', 'Housing & Rent', 'Healthcare', 'Groceries', 'Travel', 'Other']

    with tab1:
        if not user_groups:
            st.warning("Please join or create a group first.")
        else:
            g_options = {g['name']: g['id'] for g in user_groups}
            chosen_group_name = st.selectbox("Select Group:", list(g_options.keys()))
            chosen_group_id = g_options[chosen_group_name]

            # Load members
            group_members = run_query("SELECT u.id, u.name, u.email FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s", (chosen_group_id,))
            member_dict = {f"{m['name']} ({m['email']})": m['id'] for m in group_members}

            col1, col2 = st.columns(2)
            with col1:
                exp_desc = st.text_input("Expense Description *", placeholder="e.g. Dinner, Grocery run, Cab")
                exp_amt = st.number_input("Total Amount (₹) *", min_value=0.01, step=50.0, value=1200.0)
            with col2:
                exp_cat = st.selectbox("Category:", CATEGORIES)
                exp_date = st.date_input("Date:", value=datetime.date.today())

            payer_name = st.selectbox("Paid By:", list(member_dict.keys()))
            payer_id = member_dict[payer_name]

            split_type = st.radio("Split Method:", ["Equal Split", "Percentage Split", "Custom Split"], horizontal=True)

            # Selected participants
            st.markdown("#### Select Participants Sharing This Expense:")
            selected_participants = []
            splits_data = []

            if split_type == "Equal Split":
                for m_label, m_id in member_dict.items():
                    if st.checkbox(m_label, value=True, key=f"part_eq_{m_id}"):
                        selected_participants.append(m_id)
                if selected_participants:
                    share_per_person = round(exp_amt / len(selected_participants), 2)
                    st.info(f"Each participant owes: **₹{share_per_person:,.2f}**")
                    for pid in selected_participants:
                        splits_data.append((pid, share_per_person, round(100.0/len(selected_participants), 2)))

            elif split_type == "Percentage Split":
                total_pct = 0.0
                pct_inputs = {}
                cols = st.columns(len(member_dict))
                for idx, (m_label, m_id) in enumerate(member_dict.items()):
                    with cols[idx % len(cols)]:
                        p = st.number_input(f"{m_label.split(' ')[0]} (%)", min_value=0.0, max_value=100.0, value=round(100.0/len(member_dict), 1), step=5.0, key=f"pct_{m_id}")
                        pct_inputs[m_id] = p
                        total_pct += p
                st.caption(f"Total percentage allocated: **{total_pct:.1f}%**")
                if abs(total_pct - 100.0) < 0.1:
                    for pid, pct in pct_inputs.items():
                        if pct > 0:
                            share = round(exp_amt * (pct / 100.0), 2)
                            splits_data.append((pid, share, pct))
                else:
                    st.error("Percentages must sum to exactly 100%.")

            elif split_type == "Custom Split":
                total_cust = 0.0
                cust_inputs = {}
                cols = st.columns(len(member_dict))
                for idx, (m_label, m_id) in enumerate(member_dict.items()):
                    with cols[idx % len(cols)]:
                        amt = st.number_input(f"{m_label.split(' ')[0]} (₹)", min_value=0.0, value=round(exp_amt/len(member_dict), 2), step=50.0, key=f"amt_{m_id}")
                        cust_inputs[m_id] = amt
                        total_cust += amt
                st.caption(f"Total allocated: **₹{total_cust:,.2f}** / **₹{exp_amt:,.2f}**")
                if abs(total_cust - exp_amt) < 0.01:
                    for pid, amt in cust_inputs.items():
                        if amt > 0:
                            splits_data.append((pid, amt, None))
                else:
                    st.error(f"Custom shares sum (₹{total_cust:,.2f}) must match total amount (₹{exp_amt:,.2f}).")

            if st.button("💾 Record Expense", type="primary"):
                if not exp_desc.strip():
                    st.error("Please enter a description.")
                elif not splits_data:
                    st.error("Valid split configuration is required.")
                else:
                    st_val = 'EQUAL' if split_type == 'Equal Split' else ('PERCENTAGE' if split_type == 'Percentage Split' else 'CUSTOM')
                    eid = execute_cmd("""
                        INSERT INTO expenses (group_id, paid_by, description, amount, category, date, split_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (chosen_group_id, payer_id, exp_desc.strip(), exp_amt, exp_cat, str(exp_date), st_val))

                    for pid, sh_amt, sh_pct in splits_data:
                        execute_cmd("""
                            INSERT INTO expense_splits (expense_id, user_id, share_amount, share_percentage)
                            VALUES (%s, %s, %s, %s)
                        """, (eid, pid, sh_amt, sh_pct))

                    st.success(f"Expense '{exp_desc}' recorded successfully!")
                    st.rerun()

    with tab2:
        st.subheader("All Expenses")
        if user_groups:
            group_ids = [g['id'] for g in user_groups]
            format_p = ','.join(['%s'] * len(group_ids))
            all_exp = run_query(f"""
                SELECT e.id, e.date as Date, e.description as Description, g.name as Group_Name,
                       e.category as Category, u.name as Paid_By, e.amount as Amount, e.split_type as Split_Type
                FROM expenses e
                JOIN `groups` g ON e.group_id = g.id
                JOIN users u ON e.paid_by = u.id
                WHERE e.group_id IN ({format_p})
                ORDER BY e.date DESC
            """, group_ids)
            if all_exp:
                st.dataframe(pd.DataFrame(all_exp), use_container_width=True)
            else:
                st.info("No recorded expenses found.")

# ==============================================================================
# 4. BALANCES (WHO OWES WHOM)
# ==============================================================================
elif menu == "⚖️ Balances (Who Owes Whom)":
    st.title("Simplified Debt Settlement")
    st.caption("Calculate optimal minimum cash-flow transactions to settle all peer debts.")

    user_groups = run_query("""
        SELECT g.id, g.name FROM `groups` g
        JOIN group_members gm ON g.id = gm.group_id WHERE gm.user_id = %s
    """, (current_user_id,))

    if not user_groups:
        st.info("No group activity recorded.")
    else:
        for g in user_groups:
            gid = g['id']
            st.markdown(f"### 👥 {g['name']}")

            members = run_query("SELECT u.id, u.name, u.email FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s", (gid,))
            m_dict = {m['id']: m['name'] for m in members}

            paid_rows = {r['user_id']: float(r['val']) for r in run_query("SELECT paid_by as user_id, SUM(amount) as val FROM expenses WHERE group_id = %s GROUP BY paid_by", (gid,))}
            share_rows = {r['user_id']: float(r['val']) for r in run_query("SELECT es.user_id, SUM(es.share_amount) as val FROM expense_splits es JOIN expenses e ON es.expense_id = e.id WHERE e.group_id = %s GROUP BY es.user_id", (gid,))}

            # Net Balance table
            bal_list = []
            net_map = {}
            for m in members:
                uid = m['id']
                p = paid_rows.get(uid, 0.0)
                s = share_rows.get(uid, 0.0)
                net = p - s
                net_map[uid] = net
                status = "Gets Back" if net > 0.01 else ("Owes" if net < -0.01 else "Settled")
                bal_list.append({
                    'Member': m['name'],
                    'Total Paid': f"₹{p:,.2f}",
                    'Total Share': f"₹{s:,.2f}",
                    'Net Balance': f"{'+' if net > 0 else ''}₹{net:,.2f}",
                    'Status': status
                })

            st.dataframe(pd.DataFrame(bal_list), use_container_width=True)

            # Settlement Suggestions
            settlements = simplify_debts(net_map, m_dict)
            st.markdown("**💡 Optimal Settlement Payments:**")
            if not settlements:
                st.success("✅ Everyone is settled up! No payments required.")
            else:
                for s in settlements:
                    st.info(f"👉 **{s['debtor_name']}** pays **{s['creditor_name']}** : **₹{s['amount']:,.2f}**")
            st.markdown("---")

# ==============================================================================
# 5. GROUP BUDGETS
# ==============================================================================
elif menu == "🐷 Group Budgets":
    st.title("Group Spending Budgets")
    st.caption("Manage monthly budgets and monitor automated warning thresholds.")

    budgets = run_query("""
        SELECT g.id, g.name, g.description,
               COALESCE(gb.monthly_budget, 0.00) as budget,
               COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) as spent
        FROM `groups` g
        JOIN group_members gm ON g.id = gm.group_id
        LEFT JOIN group_budgets gb ON g.id = gb.group_id
        WHERE gm.user_id = %s
    """, (current_user_id,))

    for b_item in budgets:
        with st.container():
            c1, c2 = st.columns([3, 1])
            b = float(b_item['budget'])
            s = float(b_item['spent'])
            pct = (s / b * 100) if b > 0 else 0

            with c1:
                st.subheader(f"📁 {b_item['name']}")
                st.write(f"Spent: **₹{s:,.2f}** of **₹{b:,.2f}** ({pct:.1f}%)")
                if b > 0:
                    st.progress(min(s/b, 1.0))
            with c2:
                status_color = "🟢 Normal" if pct < 75 else ("🟡 Warning" if pct < 90 else ("🟠 High Alert" if pct < 100 else "🔴 Exceeded"))
                st.markdown(f"**Status:** {status_color}")

            # Quick update budget
            new_b = st.number_input(f"Update Monthly Budget for {b_item['name']} (₹):", min_value=0.0, step=500.0, value=b, key=f"up_b_{b_item['id']}")
            if st.button(f"Save Budget", key=f"btn_b_{b_item['id']}"):
                execute_cmd("""
                    INSERT INTO group_budgets (group_id, monthly_budget) VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE monthly_budget = %s
                """ if db_type == 'mysql' else """
                    INSERT OR REPLACE INTO group_budgets (group_id, monthly_budget) VALUES (%s, %s)
                """, (b_item['id'], new_b, new_b) if db_type == 'mysql' else (b_item['id'], new_b))
                st.success("Budget updated!")
                st.rerun()
            st.markdown("---")

# ==============================================================================
# 6. WHAT-IF SIMULATOR
# ==============================================================================
elif menu == "🧪 What-If Simulator":
    st.title("What-If Expense Simulator")
    st.caption("Simulate hypothetical purchases without modifying real database records.")

    user_groups = run_query("SELECT g.id, g.name FROM `groups` g JOIN group_members gm ON g.id = gm.group_id WHERE gm.user_id = %s", (current_user_id,))
    if not user_groups:
        st.info("Please create a group first.")
    else:
        g_options = {g['name']: g['id'] for g in user_groups}
        sim_g_name = st.selectbox("Target Group:", list(g_options.keys()))
        sim_gid = g_options[sim_g_name]

        # Get group budget and current spent
        g_info = run_query("""
            SELECT g.name, COALESCE(gb.monthly_budget, 0.00) as budget,
                   COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) as spent
            FROM `groups` g LEFT JOIN group_budgets gb ON g.id = gb.group_id WHERE g.id = %s
        """, (sim_gid,))[0]

        curr_spent = float(g_info['spent'])
        budget = float(g_info['budget'])

        sim_desc = st.text_input("Proposed Purchase:", value="Weekend Group Villa Rental")
        sim_amt = st.number_input("Proposed Amount (₹):", min_value=1.0, value=5000.0, step=100.0)

        # Simulation comparison
        proj_spent = curr_spent + sim_amt
        curr_pct = (curr_spent / budget * 100) if budget > 0 else 0
        proj_pct = (proj_spent / budget * 100) if budget > 0 else 0

        st.markdown("### 📊 Live Impact Projection:")
        m1, m2, m3 = st.columns(3)
        m1.metric("Group Budget", f"₹{budget:,.2f}")
        m2.metric("Current Spending", f"₹{curr_spent:,.2f}", f"{curr_pct:.1f}% used")
        m3.metric("Projected Spending", f"₹{proj_spent:,.2f}", f"+₹{sim_amt:,.2f} ({proj_pct:.1f}%)")

        if budget > 0:
            if proj_spent > budget:
                st.error(f"🚨 **Warning**: This proposed expense will exceed the group budget by **₹{proj_spent - budget:,.2f}**!")
            elif proj_pct >= 90:
                st.warning(f"⚠️ **High Alert**: This expense will push spending to **{proj_pct:.1f}%** of the budget.")
            else:
                st.success(f"✅ Safe: Remaining budget after this expense will be **₹{budget - proj_spent:,.2f}**.")

        st.caption("ℹ️ This simulation is a preview only. Database records are unchanged.")
