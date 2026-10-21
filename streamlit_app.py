"""
Expense Split and Settlement System - Streamlit Web Edition
Theme: Vibrant Purple & White • Responsive Cards • Interactive Visualizations • Cloud Fallback
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

# Enforce Bright Purple-and-White Theme via CSS Injection
st.markdown("""
<style>
    /* Global App Background */
    .stApp {
        background-color: #f8f9fa !important;
        color: #2d3436 !important;
        font-family: 'Segoe UI', -apple-system, Roboto, sans-serif !important;
    }
    
    /* Force Header & Toolbar Background */
    header[data-testid="stHeader"] {
        background-color: #f8f9fa !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e9ecef !important;
        box-shadow: 2px 0 10px rgba(108, 92, 231, 0.04) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #2d3436 !important;
    }
    
    /* Purple Gradient Brand Header Card */
    .brand-hero {
        background: linear-gradient(135deg, #4b38b3 0%, #6c5ce7 50%, #8e44ad 100%);
        color: #ffffff !important;
        padding: 1.75rem 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(108, 92, 231, 0.25);
        margin-bottom: 2rem;
    }
    .brand-hero h1, .brand-hero p, .brand-hero span {
        color: #ffffff !important;
    }

    /* White Content Cards with Subtle Shadows */
    .white-card {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 16px rgba(108, 92, 231, 0.06);
        margin-bottom: 1.5rem;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e9ecef !important;
        padding: 1.25rem !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 16px rgba(108, 92, 231, 0.08) !important;
        border-left: 5px solid #6c5ce7 !important;
        transition: transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }
    div[data-testid="stMetricValue"] {
        color: #2d3436 !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #636e72 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.8rem !important;
        letter-spacing: 0.5px;
    }

    /* Primary Purple Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #6c5ce7 0%, #8e44ad 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.55rem 1.4rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(108, 92, 231, 0.25) !important;
    }
    .stButton>button:hover {
        opacity: 0.92 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(108, 92, 231, 0.35) !important;
    }

    /* Secondary Inputs & Forms */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: #ffffff !important;
        color: #2d3436 !important;
        border: 1px solid #e9ecef !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #6c5ce7 !important;
        box-shadow: 0 0 0 2px rgba(108, 92, 231, 0.15) !important;
    }

    /* Settlement Highlights */
    .settlement-box {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-left: 5px solid #6c5ce7;
        padding: 1rem 1.25rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(108, 92, 231, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Alerts */
    .budget-banner {
        background-color: #fff9e6;
        color: #d35400;
        border: 1px solid #fdcb6e;
        border-left: 5px solid #e17055;
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATABASE ABSTRACTION (MySQL with Cloud Demo Engine)
# ==============================================================================
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Mysql@1234')
DB_NAME = os.getenv('DB_NAME', 'expense_settlement_db')

if hasattr(st, 'secrets') and 'DB_PASSWORD' in st.secrets:
    DB_PASSWORD = st.secrets['DB_PASSWORD']
    DB_HOST = st.secrets.get('DB_HOST', DB_HOST)
    DB_USER = st.secrets.get('DB_USER', DB_USER)
    DB_NAME = st.secrets.get('DB_NAME', DB_NAME)

@st.cache_resource
def init_connection():
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
    except Exception:
        import sqlite3
        sqlite_path = os.path.join(os.path.dirname(__file__), 'cloud_demo.db')
        conn = sqlite3.connect(sqlite_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        setup_sqlite_schema(conn)
        return 'sqlite', conn

def setup_sqlite_schema(conn):
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
    if db_type == 'sqlite':
        sql = sql.replace('`groups`', 'groups_table').replace('groups g', 'groups_table g')
        cur = db_conn.cursor()
        if params:
            cur.execute(sql.replace('%s', '?'), params)
        else:
            cur.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        return [dict(zip(cols, r)) for r in cur.fetchall()]
    else:
        try:
            db_conn.ping(reconnect=True)
        except Exception:
            pass
        with db_conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()

def execute_cmd(sql, params=None):
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
# SIDEBAR
# ==============================================================================
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 1.5rem;">
    <div style="width: 52px; height: 52px; background: #eceafe; color: #6c5ce7; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 1.6rem; margin-bottom: 0.5rem;">
        💳
    </div>
    <h2 style="font-size: 1.3rem; margin: 0; color: #2d3436;">SplitSettlement</h2>
    <small style="color: #636e72;">Purple & White Edition</small>
</div>
""", unsafe_allow_html=True)

lang = st.sidebar.selectbox("🌐 Interface Language:", ["English", "ಕನ್ನಡ (Kannada)", "తెలుగు (Telugu)", "हिन्दी (Hindi)"])

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
st.sidebar.caption(f"Engine: **{db_type.upper()}** &bull; Status: **Online**")

# ==============================================================================
# 1. DASHBOARD & ANALYTICS
# ==============================================================================
if menu == "📊 Dashboard & Analytics":
    # Top Purple Banner Hero
    st.markdown(f"""
    <div class="brand-hero">
        <h1 style="font-size: 1.9rem; font-weight: 700; margin-bottom: 0.35rem;">Financial Overview</h1>
        <p style="font-size: 1rem; opacity: 0.95; margin: 0;">Welcome back, <strong>{current_user_name}</strong>! Track shared expenses, balances, and real-time budget health.</p>
    </div>
    """, unsafe_allow_html=True)

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
        st.info("You do not belong to any groups yet. Navigate to 'Groups & Members' to create or join one!")
    else:
        group_ids = [g['id'] for g in user_groups]
        format_p = ','.join(['%s'] * len(group_ids))

        total_group_exp = run_query(f"SELECT COALESCE(SUM(amount), 0.00) as val FROM expenses WHERE group_id IN ({format_p})", group_ids)[0]['val']
        total_paid = run_query(f"SELECT COALESCE(SUM(amount), 0.00) as val FROM expenses WHERE paid_by = %s AND group_id IN ({format_p})", [current_user_id] + group_ids)[0]['val']
        
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

        # Budget Warnings Banner
        for g in user_groups:
            b = float(g['monthly_budget'])
            s = float(g['total_spent'])
            if b > 0:
                pct = (s / b) * 100
                if pct >= 100:
                    st.markdown(f"""<div class="budget-banner" style="background:#fdeaea; color:#c0392b; border-color:#e74c3c;">🚨 <strong>Budget Exceeded Alert:</strong> <strong>{g['name']}</strong> has crossed 100% of its budget (Spent ₹{s:,.2f} of ₹{b:,.2f})!</div>""", unsafe_allow_html=True)
                elif pct >= 90:
                    st.markdown(f"""<div class="budget-banner" style="background:#fdeee9; color:#e17055; border-color:#e17055;">⚠️ <strong>High Spending Alert:</strong> <strong>{g['name']}</strong> has used <strong>{pct:.1f}%</strong> of its monthly budget!</div>""", unsafe_allow_html=True)
                elif pct >= 75:
                    st.markdown(f"""<div class="budget-banner">ℹ️ <strong>Budget Warning:</strong> <strong>{g['name']}</strong> has reached <strong>{pct:.1f}%</strong> of its spending cap.</div>""", unsafe_allow_html=True)

        # 5 White Metric Cards
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Group Expenses", f"₹{float(total_group_exp):,.2f}")
        c2.metric("Total You Paid", f"₹{float(total_paid):,.2f}")
        c3.metric("You Are Owed", f"₹{others_owe:,.2f}")
        c4.metric("You Owe", f"₹{user_owes:,.2f}")
        c5.metric("Active Groups", len(user_groups))

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts Section
        col_c1, col_c2 = st.columns(2)

        # 1. Monthly Spending Trend
        with col_c1:
            st.markdown("""<div class="white-card"><h3 style="font-size:1.15rem; margin-bottom:1rem; color:#2d3436;">📈 Monthly Spending Trend</h3>""", unsafe_allow_html=True)
            month_rows = run_query(f"""
                SELECT substr(date, 1, 7) as month_label, SUM(amount) as total
                FROM expenses WHERE group_id IN ({format_p})
                GROUP BY month_label ORDER BY month_label ASC
            """, group_ids)
            if month_rows:
                df_month = pd.DataFrame(month_rows)
                fig_month = px.area(df_month, x='month_label', y='total', labels={'month_label': 'Month', 'total': 'Spent (₹)'}, color_discrete_sequence=['#6c5ce7'])
                fig_month.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', font_color='#2d3436', margin=dict(l=20, r=20, t=10, b=20), height=280)
                fig_month.update_xaxes(showgrid=True, gridcolor='#f1f2f6')
                fig_month.update_yaxes(showgrid=True, gridcolor='#f1f2f6')
                st.plotly_chart(fig_month, use_container_width=True)
            else:
                st.info("No expense data recorded yet.")
            st.markdown("</div>", unsafe_allow_html=True)

        # 2. Category Breakdown Donut Chart
        with col_c2:
            st.markdown("""<div class="white-card"><h3 style="font-size:1.15rem; margin-bottom:1rem; color:#2d3436;">🍩 Expense Category Breakdown</h3>""", unsafe_allow_html=True)
            cat_rows = run_query(f"""
                SELECT category, SUM(amount) as total
                FROM expenses WHERE group_id IN ({format_p})
                GROUP BY category ORDER BY total DESC
            """, group_ids)
            if cat_rows:
                df_cat = pd.DataFrame(cat_rows)
                fig_cat = px.pie(df_cat, names='category', values='total', hole=0.5, color_discrete_sequence=['#6c5ce7', '#00b894', '#0984e3', '#fdcb6e', '#e17055', '#a29bfe', '#00cec9'])
                fig_cat.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', font_color='#2d3436', margin=dict(l=20, r=20, t=10, b=20), height=280)
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("No category data yet.")
            st.markdown("</div>", unsafe_allow_html=True)

        col_b1, col_b2 = st.columns(2)
        # 3. Group Spending
        with col_b1:
            st.markdown("""<div class="white-card"><h3 style="font-size:1.15rem; margin-bottom:1rem; color:#2d3436;">📊 Group-wise Spending Comparison</h3>""", unsafe_allow_html=True)
            df_grp = pd.DataFrame([{'Group': g['name'], 'Spent': float(g['total_spent'])} for g in user_groups])
            fig_grp = px.bar(df_grp, x='Group', y='Spent', color='Group', color_discrete_sequence=['#6c5ce7', '#a29bfe', '#00b894'])
            fig_grp.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', font_color='#2d3436', margin=dict(l=20, r=20, t=10, b=20), height=280, showlegend=False)
            st.plotly_chart(fig_grp, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # 4. Budget vs Spent
        with col_b2:
            st.markdown("""<div class="white-card"><h3 style="font-size:1.15rem; margin-bottom:1rem; color:#2d3436;">⚖️ Budget vs Actual Spent</h3>""", unsafe_allow_html=True)
            b_data = []
            for g in user_groups:
                b_data.append({'Group': g['name'], 'Type': 'Spent Amount', 'Amount': float(g['total_spent'])})
                b_data.append({'Group': g['name'], 'Type': 'Monthly Budget', 'Amount': float(g['monthly_budget'])})
            df_b = pd.DataFrame(b_data)
            fig_b = px.bar(df_b, x='Group', y='Amount', color='Type', barmode='group', color_discrete_map={'Spent Amount': '#e17055', 'Monthly Budget': '#00b894'})
            fig_b.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', font_color='#2d3436', margin=dict(l=20, r=20, t=10, b=20), height=280)
            st.plotly_chart(fig_b, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Recent Transactions
        st.markdown("""<div class="white-card"><h3 style="font-size:1.15rem; margin-bottom:1rem; color:#2d3436;">🕒 Recent Transactions</h3>""", unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 2. GROUPS & MEMBERS
# ==============================================================================
elif menu == "👥 Groups & Members":
    st.markdown("""<div class="brand-hero"><h1>Group Management</h1><p>Organize roommates, trips, and friends circles.</p></div>""", unsafe_allow_html=True)
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
                    b = float(g['monthly_budget'])
                    s = float(g['total_spent'])
                    if b > 0:
                        pct = min(s / b, 1.0)
                        st.progress(pct, text=f"Budget Usage: {(s/b)*100:.1f}%")
                    
                    st.markdown("**Members:**")
                    members = run_query("SELECT u.name, u.email, gm.role FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s", (g['id'],))
                    st.table(pd.DataFrame(members))

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
        with st.form("new_group_form"):
            g_name = st.text_input("Group Name *", placeholder="e.g. Manali Road Trip, Flat 101")
            g_desc = st.text_area("Description (Optional)")
            g_budget = st.number_input("Monthly Spending Budget (₹, Optional)", min_value=0.0, step=500.0, value=15000.0)
            if st.form_submit_button("Create Group"):
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
    st.markdown("""<div class="brand-hero"><h1>Expense Tracking</h1><p>Record bills and split with Equal, Percentage, or Custom shares.</p></div>""", unsafe_allow_html=True)
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

            selected_participants = []
            splits_data = []

            if split_type == "Equal Split":
                for m_label, m_id in member_dict.items():
                    if st.checkbox(m_label, value=True, key=f"part_eq_{m_id}"):
                        selected_participants.append(m_id)
                if selected_participants:
                    share_per_person = round(exp_amt / len(selected_participants), 2)
                    st.info(f"Each person pays: **₹{share_per_person:,.2f}**")
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
                if abs(total_pct - 100.0) < 0.1:
                    for pid, pct in pct_inputs.items():
                        if pct > 0:
                            share = round(exp_amt * (pct / 100.0), 2)
                            splits_data.append((pid, share, pct))
                else:
                    st.error(f"Percentages must sum to 100% (currently {total_pct:.1f}%).")

            elif split_type == "Custom Split":
                total_cust = 0.0
                cust_inputs = {}
                cols = st.columns(len(member_dict))
                for idx, (m_label, m_id) in enumerate(member_dict.items()):
                    with cols[idx % len(cols)]:
                        amt = st.number_input(f"{m_label.split(' ')[0]} (₹)", min_value=0.0, value=round(exp_amt/len(member_dict), 2), step=50.0, key=f"amt_{m_id}")
                        cust_inputs[m_id] = amt
                        total_cust += amt
                if abs(total_cust - exp_amt) < 0.01:
                    for pid, amt in cust_inputs.items():
                        if amt > 0:
                            splits_data.append((pid, amt, None))
                else:
                    st.error(f"Custom sum (₹{total_cust:,.2f}) must match total (₹{exp_amt:,.2f}).")

            if st.button("💾 Record Expense", type="primary"):
                if not exp_desc.strip() or not splits_data:
                    st.error("Please fill all required fields.")
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
                    st.success(f"Expense '{exp_desc}' recorded!")
                    st.rerun()

    with tab2:
        if user_groups:
            group_ids = [g['id'] for g in user_groups]
            format_p = ','.join(['%s'] * len(group_ids))
            all_exp = run_query(f"""
                SELECT e.date as Date, e.description as Description, g.name as Group_Name,
                       e.category as Category, u.name as Paid_By, e.amount as Amount, e.split_type as Split_Type
                FROM expenses e
                JOIN `groups` g ON e.group_id = g.id
                JOIN users u ON e.paid_by = u.id
                WHERE e.group_id IN ({format_p})
                ORDER BY e.date DESC
            """, group_ids)
            if all_exp:
                st.dataframe(pd.DataFrame(all_exp), use_container_width=True)

# ==============================================================================
# 4. BALANCES (WHO OWES WHOM)
# ==============================================================================
elif menu == "⚖️ Balances (Who Owes Whom)":
    st.markdown("""<div class="brand-hero"><h1>Who Owes Whom</h1><p>Optimal minimum cash-flow debt simplification algorithm.</p></div>""", unsafe_allow_html=True)
    user_groups = run_query("SELECT g.id, g.name FROM `groups` g JOIN group_members gm ON g.id = gm.group_id WHERE gm.user_id = %s", (current_user_id,))
    if not user_groups:
        st.info("No balances available.")
    else:
        for g in user_groups:
            gid = g['id']
            st.markdown(f"""<div class="white-card"><h3 style="color:#2d3436; margin-bottom:1rem;">👥 {g['name']}</h3>""", unsafe_allow_html=True)
            members = run_query("SELECT u.id, u.name, u.email FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s", (gid,))
            m_dict = {m['id']: m['name'] for m in members}

            paid_rows = {r['user_id']: float(r['val']) for r in run_query("SELECT paid_by as user_id, SUM(amount) as val FROM expenses WHERE group_id = %s GROUP BY paid_by", (gid,))}
            share_rows = {r['user_id']: float(r['val']) for r in run_query("SELECT es.user_id, SUM(es.share_amount) as val FROM expense_splits es JOIN expenses e ON es.expense_id = e.id WHERE e.group_id = %s GROUP BY es.user_id", (gid,))}

            bal_list = []
            net_map = {}
            for m in members:
                uid = m['id']
                p = paid_rows.get(uid, 0.0)
                s = share_rows.get(uid, 0.0)
                net = p - s
                net_map[uid] = net
                status = "Gets Back" if net > 0.01 else ("Owes" if net < -0.01 else "Settled")
                bal_list.append({'Member': m['name'], 'Paid': f"₹{p:,.2f}", 'Share': f"₹{s:,.2f}", 'Net': f"{'+' if net > 0 else ''}₹{net:,.2f}", 'Status': status})

            st.dataframe(pd.DataFrame(bal_list), use_container_width=True)

            settlements = simplify_debts(net_map, m_dict)
            st.markdown("<h4 style='color:#6c5ce7; margin-top:1rem;'>💡 Settlement Instructions:</h4>", unsafe_allow_html=True)
            if not settlements:
                st.success("✅ Everyone is settled up in this group!")
            else:
                for s in settlements:
                    st.markdown(f"""
                    <div class="settlement-box">
                        <div><strong style="color:#d63031;">{s['debtor_name']}</strong> pays <strong style="color:#00b894;">{s['creditor_name']}</strong></div>
                        <strong style="color:#6c5ce7; font-size:1.1rem;">₹{s['amount']:,.2f}</strong>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 5. GROUP BUDGETS
# ==============================================================================
elif menu == "🐷 Group Budgets":
    st.markdown("""<div class="brand-hero"><h1>Group Budgets</h1><p>Set spending caps and monitor 4-tier automated alerts.</p></div>""", unsafe_allow_html=True)
    budgets = run_query("""
        SELECT g.id, g.name, g.description,
               COALESCE(gb.monthly_budget, 0.00) as budget,
               COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) as spent
        FROM `groups` g JOIN group_members gm ON g.id = gm.group_id
        LEFT JOIN group_budgets gb ON g.id = gb.group_id WHERE gm.user_id = %s
    """, (current_user_id,))

    for b_item in budgets:
        st.markdown(f"""<div class="white-card"><h3 style="color:#2d3436; margin-bottom:0.75rem;">📁 {b_item['name']}</h3>""", unsafe_allow_html=True)
        b = float(b_item['budget'])
        s = float(b_item['spent'])
        pct = (s / b * 100) if b > 0 else 0
        st.write(f"Spent: **₹{s:,.2f}** of **₹{b:,.2f}** ({pct:.1f}%)")
        if b > 0:
            st.progress(min(s/b, 1.0))
        new_b = st.number_input(f"Monthly Budget (₹) for {b_item['name']}:", min_value=0.0, step=500.0, value=b, key=f"b_{b_item['id']}")
        if st.button("Save Budget", key=f"btn_sb_{b_item['id']}"):
            execute_cmd("""
                INSERT INTO group_budgets (group_id, monthly_budget) VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE monthly_budget = %s
            """ if db_type == 'mysql' else """
                INSERT OR REPLACE INTO group_budgets (group_id, monthly_budget) VALUES (%s, %s)
            """, (b_item['id'], new_b, new_b) if db_type == 'mysql' else (b_item['id'], new_b))
            st.success("Budget updated!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 6. WHAT-IF SIMULATOR
# ==============================================================================
elif menu == "🧪 What-If Simulator":
    st.markdown("""<div class="brand-hero"><h1>What-If Expense Simulator</h1><p>Test hypothetical expenses without saving to database.</p></div>""", unsafe_allow_html=True)
    user_groups = run_query("SELECT g.id, g.name FROM `groups` g JOIN group_members gm ON g.id = gm.group_id WHERE gm.user_id = %s", (current_user_id,))
    if not user_groups:
        st.info("Please create a group first.")
    else:
        g_options = {g['name']: g['id'] for g in user_groups}
        sim_g_name = st.selectbox("Target Group:", list(g_options.keys()))
        sim_gid = g_options[sim_g_name]

        g_info = run_query("""
            SELECT g.name, COALESCE(gb.monthly_budget, 0.00) as budget,
                   COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) as spent
            FROM `groups` g LEFT JOIN group_budgets gb ON g.id = gb.group_id WHERE g.id = %s
        """, (sim_gid,))[0]

        curr_spent = float(g_info['spent'])
        budget = float(g_info['budget'])

        sim_desc = st.text_input("Proposed Purchase:", value="Weekend Group Villa Rental")
        sim_amt = st.number_input("Proposed Amount (₹):", min_value=1.0, value=5000.0, step=100.0)

        proj_spent = curr_spent + sim_amt
        curr_pct = (curr_spent / budget * 100) if budget > 0 else 0
        proj_pct = (proj_spent / budget * 100) if budget > 0 else 0

        st.markdown("""<div class="white-card"><h3>Live Impact Projection</h3>""", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Group Budget", f"₹{budget:,.2f}")
        m2.metric("Current Spending", f"₹{curr_spent:,.2f}", f"{curr_pct:.1f}% used")
        m3.metric("Projected Spending", f"₹{proj_spent:,.2f}", f"+₹{sim_amt:,.2f} ({proj_pct:.1f}%)")

        if budget > 0:
            if proj_spent > budget:
                st.error(f"🚨 **Budget Alert**: This proposed expense will exceed the group budget by **₹{proj_spent - budget:,.2f}**!")
            elif proj_pct >= 90:
                st.warning(f"⚠️ **High Alert**: This expense will push spending to **{proj_pct:.1f}%** of the budget.")
            else:
                st.success(f"✅ Safe: Remaining budget after this expense will be **₹{budget - proj_spent:,.2f}**.")
        st.markdown("</div>", unsafe_allow_html=True)
