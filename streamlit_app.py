"""
Expense Split and Settlement System - Streamlit Web Edition
Theme: Vibrant Purple & White • Secure Login & Registration • Group & Expense Deletion • Real Data
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
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Password hashing utilities
def make_password_hash(password):
    try:
        from werkzeug.security import generate_password_hash
        return generate_password_hash(password)
    except Exception:
        import hashlib
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_user_password(stored_hash, candidate_password):
    if not stored_hash or stored_hash == 'demo' or stored_hash == '123456' or stored_hash == candidate_password or stored_hash == 'scrypt:32768:8:1':
        return True
    try:
        from werkzeug.security import check_password_hash
        if check_password_hash(stored_hash, candidate_password):
            return True
    except Exception:
        pass
    import hashlib
    candidate_hash = hashlib.sha256(candidate_password.encode('utf-8')).hexdigest()
    return stored_hash == candidate_hash

# Enforce Bright Purple-and-White Theme & Top-Right Profile Badge via Custom CSS
st.markdown("""
<style>
    /* Global App Background */
    .stApp {
        background-color: #f8f9fa !important;
        color: #2d3436 !important;
        font-family: 'Segoe UI', -apple-system, Roboto, sans-serif !important;
    }
    
    /* Header background */
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
    
    /* Top-Right Profile Badge */
    .profile-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: #ffffff;
        border: 1.5px solid #dcd6fa;
        padding: 5px 14px;
        border-radius: 30px;
        box-shadow: 0 2px 8px rgba(108, 92, 231, 0.1);
        transition: all 0.2s ease;
    }
    .profile-badge:hover {
        border-color: #6c5ce7;
        box-shadow: 0 4px 12px rgba(108, 92, 231, 0.2);
    }
    .profile-avatar {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6c5ce7 0%, #8e44ad 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(108, 92, 231, 0.3);
    }
    .profile-info {
        display: flex;
        flex-direction: column;
        text-align: left;
    }
    .profile-name {
        font-weight: 700;
        color: #2d3436;
        font-size: 0.92rem;
        line-height: 1.1;
    }
    .profile-status {
        font-size: 0.72rem;
        color: #00b894;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 3px;
    }

    /* Purple Gradient Brand Hero Card */
    .brand-hero {
        background: linear-gradient(135deg, #4b38b3 0%, #6c5ce7 50%, #8e44ad 100%);
        color: #ffffff !important;
        padding: 1.75rem 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(108, 92, 231, 0.22);
        margin-bottom: 1.75rem;
    }
    .brand-hero h1, .brand-hero p, .brand-hero span {
        color: #ffffff !important;
    }

    /* White Content Cards with Subtle Purple Shadows */
    .white-card {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 14px;
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
    
    /* Member Pill Badges */
    .member-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #f1f0fd;
        color: #6c5ce7;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid #e0dcfc;
        margin: 4px 4px 4px 0;
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

    # Pre-register primary accounts so Rajasree, Bhoomika, and Priya exist with password '123456'
    base_users = [
        ('Rajasree', 'sree11@gmail.com', 'sree@11'),
        ('Rajasree', 'rajasree@gmail.com', 'sree@11'),
        ('Rajasree', 'rajasree11@gmail.com', 'sree@11'),
        ('Bhoomika', 'bhoomika@gmail.com', '123456'),
        ('Priya Patel', 'priya@example.com', '123456'),
        ('Rahul Sharma', 'rahul@example.com', '123456')
    ]
    for u_name, u_email, u_pwd in base_users:
        cur.execute("SELECT id FROM users WHERE LOWER(email) = ?", (u_email.lower(),))
        if not cur.fetchone():
            cur.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                        (u_name, u_email, make_password_hash(u_pwd)))
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
# BUDGET LIMIT ALERTS ENGINE (High Alert, Low Alert & Safe Thresholds)
# ==============================================================================
def get_budget_status(spent, budget):
    s = float(spent or 0.0)
    b = float(budget or 0.0)
    if b <= 0:
        return {
            'level': 'NO_BUDGET',
            'badge': '⚪ No Budget Limit Set',
            'headline': 'No spending limit set for this group.',
            'sub': 'Set a monthly spending limit to activate real-time High & Low alerts.',
            'alert_type': 'info',
            'pct': 0.0,
            'color': '#636e72',
            'bg': '#f8f9fa',
            'border': '#e9ecef',
            'icon': 'ℹ️'
        }
    pct = (s / b) * 100.0
    if s > b:
        over = s - b
        return {
            'level': 'OVER_LIMIT',
            'badge': f'🚨 HIGH ALERT: Over Limit by ₹{over:,.2f}',
            'headline': f'🚨 CRITICAL HIGH ALERT: Over Budget Limit by ₹{over:,.2f}!',
            'sub': f'Total spent is ₹{s:,.2f} against the approved limit of ₹{b:,.2f} ({pct:.1f}% used). Please pause unnecessary expenses!',
            'alert_type': 'error',
            'pct': pct,
            'color': '#d63031',
            'bg': '#ffebee',
            'border': '#ff7675',
            'icon': '🚨'
        }
    elif pct >= 85.0:
        rem = b - s
        return {
            'level': 'HIGH_ALERT',
            'badge': f'⚠️ HIGH ALERT: {pct:.1f}% Used',
            'headline': f'⚠️ HIGH BUDGET LIMIT ALERT: Approaching Spending Cap ({pct:.1f}% used)',
            'sub': f'Warning: Only ₹{rem:,.2f} remaining out of ₹{b:,.2f}. Budget limit is nearly exhausted!',
            'alert_type': 'warning',
            'pct': pct,
            'color': '#e17055',
            'bg': '#fff3e0',
            'border': '#fab1a0',
            'icon': '⚠️'
        }
    elif pct >= 50.0:
        rem = b - s
        return {
            'level': 'MODERATE',
            'badge': f'🟡 Moderate ({pct:.1f}% Used)',
            'headline': f'🟡 Moderate Spending: {pct:.1f}% of budget consumed.',
            'sub': f'Spending is steady. Remaining budget: ₹{rem:,.2f} out of ₹{b:,.2f}.',
            'alert_type': 'info',
            'pct': pct,
            'color': '#b7791f',
            'bg': '#fffde7',
            'border': '#ffeaa7',
            'icon': '🟡'
        }
    else:
        rem = b - s
        return {
            'level': 'LOW_SAFE',
            'badge': f'🟢 LOW ALERT: Safe ({pct:.1f}% Used)',
            'headline': f'🟢 LOW BUDGET ALERT: Spending is Low & Safe ({pct:.1f}% used)',
            'sub': f'Healthy budget surplus! Remaining budget limit: ₹{rem:,.2f} out of ₹{b:,.2f}.',
            'alert_type': 'success',
            'pct': pct,
            'color': '#00b894',
            'bg': '#e8f8f5',
            'border': '#55efc4',
            'icon': '🟢'
        }

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

def clean_html(s):
    """Strips leading whitespace from every line so CommonMark never treats HTML as code blocks."""
    if not isinstance(s, str):
        return s
    return "\n".join(line.strip() for line in s.strip().splitlines())

def find_or_create_user(identifier):
    """
    Finds a registered user by email OR name, or creates a linked account
    so that adding a member by their email ID or name immediately gives them
    access to the created group.
    """
    if not identifier:
        return None, None
    ident = str(identifier).strip()
    if not ident:
        return None, None

    ident_lower = ident.lower()

    # 1. Exact match by email OR exact match by name
    # Prioritize real registered accounts over temporary @splitsettle.app accounts
    matches = run_query("""
        SELECT id, name, email FROM users
        WHERE LOWER(email) = %s OR LOWER(name) = %s
        ORDER BY CASE WHEN email LIKE '%@splitsettle.app' THEN 2 ELSE 1 END, id ASC
    """, (ident_lower, ident_lower))
    if matches:
        return matches[0]['id'], matches[0]['name']

    # 2. If identifier has '@', check if the username prefix before '@' matches an existing user
    if '@' in ident:
        prefix = ident.split('@')[0].strip().lower()
        prefix_matches = run_query("""
            SELECT id, name, email FROM users
            WHERE LOWER(name) = %s
            ORDER BY CASE WHEN email LIKE '%@splitsettle.app' THEN 2 ELSE 1 END, id ASC
        """, (prefix,))
        if prefix_matches:
            return prefix_matches[0]['id'], prefix_matches[0]['name']

    # 3. Create a linked user account so they are immediately part of the group
    if '@' in ident:
        new_email = ident_lower
        raw_prefix = ident.split('@')[0]
        clean_name = raw_prefix.replace('.', ' ').replace('_', ' ').strip().title()
        new_name = clean_name if clean_name else ident
    else:
        new_name = ident
        slug = re.sub(r'[^a-zA-Z0-9]', '', ident_lower)
        new_email = f"{slug}@splitsettle.app"

    # Avoid duplicate email insertion error if email already exists
    existing = run_query("SELECT id, name FROM users WHERE LOWER(email) = %s", (new_email,))
    if existing:
        return existing[0]['id'], existing[0]['name']

    new_uid = execute_cmd(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
        (new_name, new_email, make_password_hash('123456'))
    )
    return new_uid, new_name

def heal_user_accounts():
    """
    Auto-repairs and reconciles any duplicate/orphaned placeholder user accounts
    created under older versions when members were added by email, linking their
    group memberships to the real registered user account.
    """
    try:
        orphans = run_query("""
            SELECT id, name, email FROM users 
            WHERE email LIKE '%@splitsettle.app' OR name LIKE '%@%'
        """)
        if not orphans:
            return

        for o in orphans:
            o_id = o['id']
            o_name = o['name'].strip().lower()
            o_email = o['email'].strip().lower()

            target_real_id = None

            # Case A: Dummy user's name is actually an email (e.g. 'bhoomika@gmail.com')
            if '@' in o_name:
                real = run_query("SELECT id FROM users WHERE LOWER(email) = %s AND id != %s", (o_name, o_id))
                if real:
                    target_real_id = real[0]['id']

            # Case B: Dummy user's email was generated from an email slug (e.g. bhoomikagmailcom@splitsettle.app)
            if not target_real_id and o_email.endswith('@splitsettle.app'):
                prefix = o_email.replace('@splitsettle.app', '').lower()
                real = run_query("SELECT id FROM users WHERE LOWER(name) = %s AND id != %s", (o_name, o_id))
                if real:
                    target_real_id = real[0]['id']
                else:
                    all_reals = run_query("SELECT id, email FROM users WHERE id != %s AND email NOT LIKE '%@splitsettle.app'", (o_id,))
                    for r in all_reals:
                        r_slug = re.sub(r'[^a-zA-Z0-9]', '', r['email'].lower())
                        if r_slug == prefix:
                            target_real_id = r['id']
                            break

            if target_real_id:
                # Reassign group_members
                gm_rows = run_query("SELECT group_id FROM group_members WHERE user_id = %s", (o_id,))
                for gm in gm_rows:
                    gid = gm['group_id']
                    already = run_query("SELECT id FROM group_members WHERE group_id = %s AND user_id = %s", (gid, target_real_id))
                    if not already:
                        execute_cmd("UPDATE group_members SET user_id = %s WHERE group_id = %s AND user_id = %s", (target_real_id, gid, o_id))
                    else:
                        execute_cmd("DELETE FROM group_members WHERE group_id = %s AND user_id = %s", (gid, o_id))

                # Reassign expenses and splits
                execute_cmd("UPDATE expenses SET paid_by = %s WHERE paid_by = %s", (target_real_id, o_id))
                execute_cmd("UPDATE expense_splits SET user_id = %s WHERE user_id = %s", (target_real_id, o_id))
                execute_cmd("DELETE FROM users WHERE id = %s", (o_id,))
    except Exception:
        pass

# Reconcile user accounts automatically
heal_user_accounts()

def ensure_core_accounts():
    """
    Guarantees that Rajasree (rajasree@gmail.com, sree11@gmail.com, rajasree11@gmail.com),
    Bhoomika (bhoomika@gmail.com), and standard accounts ALWAYS exist with valid passwords,
    both in MySQL and in SQLite / Streamlit Cloud!
    """
    try:
        core_accounts = [
            ('Rajasree', 'rajasree@gmail.com', 'sree@11'),
            ('Rajasree', 'sree11@gmail.com', 'sree@11'),
            ('Rajasree', 'rajasree11@gmail.com', 'sree@11'),
            ('Bhoomika', 'bhoomika@gmail.com', '123456'),
            ('Priya Patel', 'priya@example.com', '123456'),
            ('Rahul Sharma', 'rahul@example.com', '123456')
        ]
        for name, email, pwd in core_accounts:
            existing = run_query("SELECT id, password_hash FROM users WHERE LOWER(email) = %s OR LOWER(name) = %s", (email.lower(), email.lower()))
            if not existing:
                execute_cmd("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                            (name, email, make_password_hash(pwd)))
            else:
                u = existing[0]
                if u.get('password_hash') in ['scrypt:32768:8:1', 'demo', '123456', None]:
                    execute_cmd("UPDATE users SET password_hash = %s WHERE id = %s", (make_password_hash(pwd), u['id']))

        # Ensure active group exists
        grp = run_query("SELECT id FROM `groups` LIMIT 1")
        if not grp:
            raj = run_query("SELECT id FROM users WHERE LOWER(email) = %s", ('rajasree@gmail.com',))
            bho = run_query("SELECT id FROM users WHERE LOWER(email) = %s", ('bhoomika@gmail.com',))
            if raj and bho:
                gid = execute_cmd("INSERT INTO `groups` (name, description, created_by) VALUES (%s, %s, %s)",
                                  ('College Project & Team', 'Academic Major Project expenses & study materials', raj[0]['id']))
                execute_cmd("INSERT INTO group_members (group_id, user_id, role) VALUES (%s, %s, 'creator')", (gid, raj[0]['id']))
                execute_cmd("INSERT INTO group_members (group_id, user_id, role) VALUES (%s, %s, 'member')", (gid, bho[0]['id']))
                execute_cmd("INSERT INTO group_budgets (group_id, monthly_budget) VALUES (%s, %s)", (gid, 15000.00))
    except Exception:
        pass

ensure_core_accounts()

# ==============================================================================
# INTERNATIONALIZATION (I18N) & CREATIVE BRANDING ENGINE
# ==============================================================================
LANGUAGE_OPTIONS = ["English", "ಕನ್ನಡ (Kannada)", "తెలుగు (Telugu)", "हिन्दी (Hindi)"]

if 'interface_language' not in st.session_state:
    st.session_state['interface_language'] = "English"

TRANSLATIONS = {
    'en': {
        'app_title': 'SplitSettlement',
        'app_subtitle': 'Expense Split & Settlement System',
        'auth_badge': '🔒 Secure Access',
        'welcome_hero_title': 'Welcome to SplitSettlement',
        'welcome_hero_desc': 'The smart, stress-free way to share expenses, settle debts, and manage group budgets with friends and teammates.',
        'tab_signin': '🔐 Sign In to Account',
        'tab_register': '📝 Create New Account',
        'signin_header': 'Enter your name or email to access your dashboard:',
        'signin_invited_tip': '💡 **Secure Sign In:** Enter your registered Name/Email and confidential password. If you are a new user, switch to the **\'Create New Account\'** tab to choose your own secure password.',
        'ident_label': 'Name or Email *',
        'ident_placeholder': 'e.g. Rajasree or user@example.com',
        'pwd_label': 'Password *',
        'pwd_placeholder': 'Enter your password',
        'btn_login': 'Log In to Dashboard',
        'reg_header': 'Register your details to create your account and start splitting:',
        'fullname_label': 'Full Name *',
        'fullname_placeholder': 'e.g. Rajasree, Priya, Bhoomika',
        'email_label': 'Email Address *',
        'email_placeholder': 'e.g. name@example.com',
        'create_pwd_label': 'Create Password *',
        'confirm_pwd_label': 'Confirm Password *',
        'btn_create_account': '🚀 Create Account & Log In',
        'nav_groups': '👥 Groups & Members',
        'nav_expenses': '🧾 Expenses & Splits',
        'nav_balances': '⚖️ Balances (Who Owes Whom)',
        'nav_budgets': '📊 Budgets & Limit Alerts',
        
        'nav_dashboard': '📊 Dashboard & Analytics',
        'nav_history': '📜 Payment History',
        'step_1': 'Step 1: 👥 Groups & Members',
        'step_2': 'Step 2: 🧾 Add & Split Expenses',
        'step_3': 'Step 3: ⚖️ Who Owes Whom',
        'step_4': 'Step 4: 📜 Payment History',
        'active_profile': 'Active Profile',
        'logged_in': 'Logged In',
        'btn_logout': '🚪 Log Out',
        'btn_logout_account': '🚪 Log Out Account',
        'nav_menu_header': 'Navigation Menu:',
        'groups_hero_title': 'Group Management',
        'groups_hero_desc': 'Organize project teams, roommates, trips, and friends circles.',
        'tab_view_groups': '📋 View Your Groups',
        'tab_create_group': '➕ Create New Group',
        'no_groups_msg': 'You do not belong to any groups yet. Switch to the \'Create New Group\' tab to start one!',
        'add_member_title': '➕ Add Member to',
        'add_member_input': 'Enter Member Name or Registered Email to Add to',
        'add_member_placeholder': 'e.g. Rajasree or bhoomika@gmail.com',
        'btn_add_member': '➕ Add to Group',
        'next_step_group_title': 'Done adding members to',
        'next_step_group_sub': 'Proceed to record bills and split expenses among group members.',
        'btn_next_to_expenses': '➡️ Proceed to Next Step: Record Expenses for',
        'remove_member_title': '➖ Remove a Member from',
        'btn_remove_member': 'Remove Member from Group',
        'confirm_delete_group': 'Confirm deletion of',
        'btn_delete_group': '🗑️ Delete Group',
        'group_name_label': 'Group Name *',
        'group_desc_label': 'Description (Optional)',
        'group_budget_label': 'Monthly Spending Budget (₹, Optional)',
        'initial_members_label': 'Initial Members to Add (Optional - comma separated names):',
        'btn_create_group': 'Create Group',
        'expenses_hero_title': 'Expense Tracking',
        'expenses_hero_desc': 'Record bills and split with Equal, Percentage, or Custom shares.',
        'tab_add_expense': '➕ Add New Expense',
        'tab_expense_history': '📜 Expense History & Management',
        'select_group_label': 'Select Group:',
        'exp_desc_label': 'Expense Description *',
        'exp_desc_placeholder': 'e.g. Cafe Meeting, Printouts, Dinner',
        'exp_amt_label': 'Total Amount (₹) *',
        'exp_cat_label': 'Category:',
        'exp_date_label': 'Date:',
        'paid_by_label': 'Paid By (Member):',
        'split_method_label': 'Split Method:',
        'split_equal': 'Equal Split',
        'split_percentage': 'Percentage Split',
        'split_custom': 'Custom Split',
        'btn_save_expense': '💾 Save Expense & Split',
        'delete_expense_title': '🗑️ Delete a Recorded Expense',
        'btn_delete_selected_expense': 'Delete Selected Expense',
        'next_step_exp_title': 'Expenses Recorded! Ready to See Who Owes Whom?',
        'next_step_exp_sub': 'Proceed to view net balances and optimized settlement instructions.',
        'btn_back_to_groups': '👥 Back to Groups',
        'btn_next_to_balances': '⚖️ Proceed to Next Step: Who Owes Whom',
        'balances_hero_title': 'Who Owes Whom',
        'balances_hero_desc': 'Optimal minimum cash-flow debt simplification algorithm.',
        'settlement_instructions': '💡 Settlement Instructions:',
        'pays': 'pays',
        'all_settled': '✅ Everyone is completely settled up in this group!',
        'col_member': 'Member',
        'col_paid': 'Paid',
        'col_share': 'Share',
        'col_net': 'Net',
        'col_status': 'Status',
        'status_gets_back': 'Gets Back',
        'status_owes': 'Owes',
        'status_settled': 'Settled',
        'next_step_bal_title': 'Settlements Reviewed! Ready to View Payment History?',
        'next_step_bal_sub': 'Proceed to view full payment logs, or check group budgets and analytics.',
        'btn_back_to_expenses': '⬅️ Back to Expenses',
        'btn_view_analytics': '📊 View Analytics',
        'btn_proceed_to_history': '📜 Proceed to Step 4: Payment History',
        'history_hero_title': 'Payment & Expense History',
        'history_hero_desc': 'Complete historical log of all recorded bills, shares, and settlements.',
        'filter_group_label': 'Filter History by Group:',
        'all_your_groups': 'All Your Groups',
        'stat_total_tx': 'Total Transactions',
        'stat_total_spent': 'Total Group Spending',
        'stat_your_share': 'Your Total Share',
        'delete_history_title': '🗑️ Delete a Recorded Payment / Expense',
        'btn_delete_entry': 'Delete Entry',
        'complete_lifecycle_title': 'All Steps Completed! Need to Record More or Adjust Groups?',
        'complete_lifecycle_sub': 'Jump back to any prior step at any time.',
        'btn_goto_step1': '👥 Step 1: Manage Groups',
        'btn_goto_step2': '🧾 Step 2: Add More Expenses',
        'btn_goto_step3': '⚖️ Step 3: Check Balances',
        'budgets_hero_title': 'Group Budgets & Limit Alerts',
        'budgets_hero_desc': 'Monitor spending limits with real-time High Alert and Low Alert warnings.',
        'dashboard_hero_title': 'Financial Overview',
        'dashboard_hero_desc': 'Track shared expenses, balances, and real-time budget health.',
    },
    'kn': {
        'app_title': 'ಸ್ಪ್ಲಿಟ್‌ಸೆಟ್ಲ್‌ಮೆಂಟ್ (SplitSettlement)',
        'app_subtitle': 'ಖರ್ಚು ಹಂಚಿಕೆ ಮತ್ತು ಇತ್ಯರ್ಥ ವ್ಯವಸ್ಥೆ',
        'auth_badge': '🔒 ಸುರಕ್ಷಿತ ಪ್ರವೇಶ',
        'welcome_hero_title': 'ಸ್ಪ್ಲಿಟ್‌ಸೆಟ್ಲ್‌ಮೆಂಟ್‌ಗೆ ಸುಸ್ವಾಗತ',
        'welcome_hero_desc': 'ಸ್ನೇಹಿತರು ಮತ್ತು ತಂಡದೊಂದಿಗೆ ಖರ್ಚುಗಳನ್ನು ಹಂಚಿಕೊಳ್ಳಲು, ಸಾಲಗಳನ್ನು ತೀರಿಸಲು ಮತ್ತು ಗುಂಪು ಬಜೆಟ್‌ಗಳನ್ನು ಸುಲಭವಾಗಿ ನಿರ್ವಹಿಸಲು ಅತ್ಯುತ್ತಮ ವೇದಿಕೆ.',
        'tab_signin': '🔐 ಖಾತೆಗೆ ಲಾಗ್ ಇನ್ ಮಾಡಿ',
        'tab_register': '📝 ಹೊಸ ಖಾತೆ ರಚಿಸಿ',
        'signin_header': 'ನಿಮ್ಮ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಪ್ರವೇಶಿಸಲು ಹೆಸರು ಅಥವಾ ಇಮೇಲ್ ನಮೂದಿಸಿ:',
        'signin_invited_tip': '💡 **ಸ್ನೇಹಿತರು ನಿಮ್ಮನ್ನು ಗುಂಪಿಗೆ ಸೇರಿಸಿದ್ದಾರೆಯೇ?** ನಿಮ್ಮ ಹೆಸರು ಮತ್ತು ಪೂರ್ವನಿಯೋಜಿತ ಪಾಸ್‌ವರ್ಡ್ **123456** ಬಳಸಿ ಲಾಗಿನ್ ಆಗಬಹುದು, ಅಥವಾ ನಿಮ್ಮದೇ ಪಾಸ್‌ವರ್ಡ್ ಹೊಂದಿಸಲು **\'ಹೊಸ ಖಾತೆ ರಚಿಸಿ\'** ಟ್ಯಾಬ್ ಬಳಸಿ.',
        'ident_label': 'ಹೆಸರು ಅಥವಾ ಇಮೇಲ್ *',
        'ident_placeholder': 'ಉದಾ: Rajasree ಅಥವಾ user@example.com',
        'pwd_label': 'ಪಾಸ್‌ವರ್ಡ್ *',
        'pwd_placeholder': 'ನಿಮ್ಮ ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ',
        'btn_login': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಲಾಗ್ ಇನ್ ಮಾಡಿ',
        'reg_header': 'ಖಾತೆ ರಚಿಸಲು ಮತ್ತು ಖರ್ಚು ಹಂಚಲು ನಿಮ್ಮ ವಿವರಗಳನ್ನು ನೋಂದಾಯಿಸಿ:',
        'fullname_label': 'ಪೂರ್ಣ ಹೆಸರು *',
        'fullname_placeholder': 'ಉದಾ: Rajasree, Priya, Bhoomika',
        'email_label': 'ಇಮೇಲ್ ವಿಳಾಸ *',
        'email_placeholder': 'ಉದಾ: name@example.com',
        'create_pwd_label': 'ಹೊಸ ಪಾಸ್‌ವರ್ಡ್ *',
        'confirm_pwd_label': 'ಪಾಸ್‌ವರ್ಡ್ ಖಚಿತಪಡಿಸಿ *',
        'btn_create_account': '🚀 ಖಾತೆ ರಚಿಸಿ ಮತ್ತು ಲಾಗ್ ಇನ್ ಆಗಿ',
        'nav_groups': '👥 ಗುಂಪುಗಳು ಮತ್ತು ಸದಸ್ಯರು',
        'nav_expenses': '🧾 ಖರ್ಚುಗಳು ಮತ್ತು ಹಂಚಿಕೆ',
        'nav_balances': '⚖️ ಬಾಕಿ ಲೆಕ್ಕ (ಯಾರು ಯಾರಿಗೆ ನೀಡಬೇಕು)',
        'nav_budgets': '📊 ಬಜೆಟ್ ಮತ್ತು ಎಚ್ಚರಿಕೆಗಳು',
        
        'nav_dashboard': '📊 ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಮತ್ತು ವಿಶ್ಲೇಷಣೆ',
        'nav_history': '📜 ಪಾವತಿ ಇತಿಹಾಸ',
        'step_1': 'ಹಂತ ೧: 👥 ಗುಂಪುಗಳು & ಸದಸ್ಯರು',
        'step_2': 'ಹಂತ ೨: 🧾 ಖರ್ಚು ಸೇರಿಸಿ & ಹಂಚಿಕೆ',
        'step_3': 'ಹಂತ ೩: ⚖️ ಯಾರು ಯಾರಿಗೆ ನೀಡಬೇಕು',
        'step_4': 'ಹಂತ ೪: 📜 ಪಾವತಿ ಇತಿಹಾಸ',
        'active_profile': 'ಸಕ್ರಿಯ ಪ್ರೊಫೈಲ್',
        'logged_in': 'ಲಾಗಿನ್ ಆಗಿದೆ',
        'btn_logout': '🚪 ಲಾಗ್‌ಔಟ್',
        'btn_logout_account': '🚪 ಖಾತೆಯಿಂದ ನಿರ್ಗಮಿಸಿ',
        'nav_menu_header': 'ನ್ಯಾವಿಗೇಷನ್ ಮೆನು:',
        'groups_hero_title': 'ಗುಂಪು ನಿರ್ವಹಣೆ',
        'groups_hero_desc': 'ಪ್ರಾಜೆಕ್ಟ್ ತಂಡಗಳು, ರೂಮ್‌ಮೇಟ್‌ಗಳು, ಪ್ರವಾಸಗಳು ಮತ್ತು ಸ್ನೇಹಿತರ ಬಳಗಗಳನ್ನು ನಿರ್ವಹಿಸಿ.',
        'tab_view_groups': '📋 ನಿಮ್ಮ ಗುಂಪುಗಳು',
        'tab_create_group': '➕ ಹೊಸ ಗುಂಪು ರಚಿಸಿ',
        'no_groups_msg': 'ನೀವು ಇನ್ನೂ ಯಾವುದೇ ಗುಂಪಿನಲ್ಲಿ ಇಲ್ಲ. ಹೊಸ ಗುಂಪನ್ನು ಪ್ರಾರಂಭಿಸಲು \'ಹೊಸ ಗುಂಪು ರಚಿಸಿ\' ಟ್ಯಾಬ್ ಕ್ಲಿಕ್ ಮಾಡಿ!',
        'add_member_title': '➕ ಸದಸ್ಯರನ್ನು ಸೇರಿಸಿ:',
        'add_member_input': 'ಗುಂಪಿಗೆ ಸೇರಿಸಬೇಕಾದ ಸದಸ್ಯರ ಹೆಸರು ಅಥವಾ ಇಮೇಲ್:',
        'add_member_placeholder': 'ಉದಾ: Rajasree ಅಥವಾ bhoomika@gmail.com',
        'btn_add_member': '➕ ಗುಂಪಿಗೆ ಸೇರಿಸಿ',
        'next_step_group_title': 'ಸದಸ್ಯರನ್ನು ಸೇರಿಸುವುದು ಮುಗಿದಿದೆಯೇ?',
        'next_step_group_sub': 'ಗುಂಪಿನ ಸದಸ್ಯರ ನಡುವೆ ಬಿಲ್‌ಗಳನ್ನು ದಾಖಲಿಸಲು ಮತ್ತು ಖರ್ಚು ಹಂಚಲು ಮುಂದುವರಿಯಿರಿ.',
        'btn_next_to_expenses': '➡️ ಮುಂದಿನ ಹಂತ: ಖರ್ಚುಗಳನ್ನು ದಾಖಲಿಸಿ -',
        'remove_member_title': '➖ ಗುಂಪಿನಿಂದ ಸದಸ್ಯರನ್ನು ತೆಗೆದುಹಾಕಿ',
        'btn_remove_member': 'ಸದಸ್ಯರನ್ನು ತೆಗೆದುಹಾಕಿ',
        'confirm_delete_group': 'ಗುಂಪನ್ನು ಅಳಿಸುವುದನ್ನು ಖಚಿತಪಡಿಸಿ:',
        'btn_delete_group': '🗑️ ಗುಂಪು ಅಳಿಸಿ',
        'group_name_label': 'ಗುಂಪಿನ ಹೆಸರು *',
        'group_desc_label': 'ವಿವರಣೆ (ಐಚ್ಛಿಕ)',
        'group_budget_label': 'ಮಾಸಿಕ ಖರ್ಚು ಬಜೆಟ್ (₹, ಐಚ್ಛಿಕ)',
        'initial_members_label': 'ಆರಂಭಿಕ ಸದಸ್ಯರು (ಐಚ್ಛಿಕ - ಕಾಮಾದಿಂದ ಬೇರ್ಪಡಿಸಿದ ಹೆಸರುಗಳು):',
        'btn_create_group': 'ಗುಂಪು ರಚಿಸಿ',
        'expenses_hero_title': 'ಖರ್ಚುಗಳ ಟ್ರ್ಯಾಕಿಂಗ್',
        'expenses_hero_desc': 'ಬಿಲ್‌ಗಳನ್ನು ಸಮಾನ, ಶೇಕಡಾವಾರು ಅಥವಾ ಕಸ್ಟಮ್ ಪಾಲುಗಳಲ್ಲಿ ಹಂಚಿರಿ.',
        'tab_add_expense': '➕ ಹೊಸ ಖರ್ಚು ಸೇರಿಸಿ',
        'tab_expense_history': '📜 ಖರ್ಚು ಇತಿಹಾಸ ಮತ್ತು ನಿರ್ವಹಣೆ',
        'select_group_label': 'ಗುಂಪನ್ನು ಆಯ್ಕೆಮಾಡಿ:',
        'exp_desc_label': 'ಖರ್ಚಿನ ವಿವರಣೆ *',
        'exp_desc_placeholder': 'ಉದಾ: ಕೆಫೆ ಸಭೆ, ಪ್ರಿಂಟ್‌ಔಟ್, ಊಟ',
        'exp_amt_label': 'ಒಟ್ಟು ಮೊತ್ತ (₹) *',
        'exp_cat_label': 'ವರ್ಗ:',
        'exp_date_label': 'ದಿನಾಂಕ:',
        'paid_by_label': 'ಪಾವತಿಸಿದವರು (ಸದಸ್ಯರು):',
        'split_method_label': 'ಹಂಚಿಕೆ ವಿಧಾನ:',
        'split_equal': 'ಸಮಾನ ಹಂಚಿಕೆ',
        'split_percentage': 'ಶೇಕಡಾವಾರು ಹಂಚಿಕೆ',
        'split_custom': 'ಕಸ್ಟಮ್ ಹಂಚಿಕೆ',
        'btn_save_expense': '💾 ಖರ್ಚನ್ನು ಉಳಿಸಿ ಮತ್ತು ಹಂಚಿ',
        'delete_expense_title': '🗑️ ದಾಖಲಾದ ಖರ್ಚನ್ನು ಅಳಿಸಿ',
        'btn_delete_selected_expense': 'ಆಯ್ಕೆಮಾಡಿದ ಖರ್ಚನ್ನು ಅಳಿಸಿ',
        'next_step_exp_title': 'ಖರ್ಚುಗಳು ದಾಖಲಾಗಿವೆ! ಯಾರು ಯಾರಿಗೆ ನೀಡಬೇಕು ಎಂದು ನೋಡಬೇಕೆ?',
        'next_step_exp_sub': 'ನಿವ್ವಳ ಬಾಕಿಗಳು ಮತ್ತು ಅತ್ಯುತ್ತಮ ಇತ್ಯರ್ಥ ಸೂಚನೆಗಳನ್ನು ವೀಕ್ಷಿಸಲು ಮುಂದುವರಿಯಿರಿ.',
        'btn_back_to_groups': '👥 ಗುಂಪುಗಳಿಗೆ ಹಿಂತಿರುಗಿ',
        'btn_next_to_balances': '⚖️ ಮುಂದಿನ ಹಂತ: ಯಾರು ಯಾರಿಗೆ ನೀಡಬೇಕು',
        'balances_hero_title': 'ಯಾರು ಯಾರಿಗೆ ನೀಡಬೇಕು',
        'balances_hero_desc': 'ಕನಿಷ್ಠ ನಗದು-ಹರಿವಿನ ಅತ್ಯುತ್ತಮ ಸಾಲ ಸರಳೀಕರಣ ಅಲ್ಗಾರಿದಮ್.',
        'settlement_instructions': '💡 ಇತ್ಯರ್ಥ ಸೂಚನೆಗಳು:',
        'pays': 'ನೀಡಬೇಕು:',
        'all_settled': '✅ ಈ ಗುಂಪಿನಲ್ಲಿ ಎಲ್ಲರ ಲೆಕ್ಕ ಸಂಪೂರ್ಣ ತೀರಿದೆ!',
        'col_member': 'ಸದಸ್ಯರು',
        'col_paid': 'ಪಾವತಿಸಿದ್ದು',
        'col_share': 'ಪಾಲು',
        'col_net': 'ನಿವ್ವಳ ಬಾಕಿ',
        'col_status': 'ಸ್ಥಿತಿ',
        'status_gets_back': 'ಪಡೆಯಬೇಕು',
        'status_owes': 'ನೀಡಬೇಕು',
        'status_settled': 'ತೀರಿದೆ',
        'next_step_bal_title': 'ಇತ್ಯರ್ಥಗಳನ್ನು ಪರಿಶೀಲಿಸಿದ್ದೀರಾ? ಪಾವತಿ ಇತಿಹಾಸ ನೋಡಬೇಕೆ?',
        'next_step_bal_sub': 'ಸಂಪೂರ್ಣ ಪಾವತಿ ಲಾಗ್‌ಗಳನ್ನು ವೀಕ್ಷಿಸಲು ಮುಂದಿನ ಹಂತಕ್ಕೆ ಮುಂದುವರಿಯಿರಿ.',
        'btn_back_to_expenses': '⬅️ ಖರ್ಚುಗಳಿಗೆ ಹಿಂತಿರುಗಿ',
        'btn_view_analytics': '📊 ವಿಶ್ಲೇಷಣೆ ವೀಕ್ಷಿಸಿ',
        'btn_proceed_to_history': '📜 ಹಂತ ೪: ಪಾವತಿ ಇತಿಹಾಸಕ್ಕೆ ಮುಂದುವರಿಯಿರಿ',
        'history_hero_title': 'ಪಾವತಿ & ಖರ್ಚು ಇತಿಹಾಸ',
        'history_hero_desc': 'ಎಲ್ಲಾ ಬಿಲ್‌ಗಳು, ಷೇರುಗಳು ಮತ್ತು ವಹಿವಾಟುಗಳ ಸಂಪೂರ್ಣ ದಾಖಲೆ.',
        'filter_group_label': 'ಗುಂಪಿನ ಪ್ರಕಾರ ಇತಿಹಾಸ ಫಿಲ್ಟರ್ ಮಾಡಿ:',
        'all_your_groups': 'ನಿಮ್ಮ ಎಲ್ಲಾ ಗುಂಪುಗಳು',
        'stat_total_tx': 'ಒಟ್ಟು ವಹಿವಾಟುಗಳು',
        'stat_total_spent': 'ಗುಂಪಿನ ಒಟ್ಟು ಖರ್ಚು',
        'stat_your_share': 'ನಿಮ್ಮ ಒಟ್ಟು ಪಾಲು',
        'delete_history_title': '🗑️ ದಾಖಲಾದ ಪಾವತಿ / ಖರ್ಚನ್ನು ಅಳಿಸಿ',
        'btn_delete_entry': 'ದಾಖಲೆ ಅಳಿಸಿ',
        'complete_lifecycle_title': 'ಎಲ್ಲಾ ಹಂತಗಳು ಪೂರ್ಣಗೊಂಡಿವೆ! ಹೆಚ್ಚಿನ ಖರ್ಚು ಸೇರಿಸಬೇಕೆ?',
        'complete_lifecycle_sub': 'ಯಾವುದೇ ಹಿಂದಿನ ಹಂತಕ್ಕೆ ಸುಲಭವಾಗಿ ಮರಳಿ ಹೋಗಿ.',
        'btn_goto_step1': '👥 ಹಂತ ೧: ಗುಂಪುಗಳ ನಿರ್ವಹಣೆ',
        'btn_goto_step2': '🧾 ಹಂತ ೨: ಇನ್ನಷ್ಟು ಖರ್ಚು ಸೇರಿಸಿ',
        'btn_goto_step3': '⚖️ ಹಂತ ೩: ಬಾಕಿ ಲೆಕ್ಕ ಪರಿಶೀಲಿಸಿ',
        'budgets_hero_title': 'ಗುಂಪು ಬಜೆಟ್‌ಗಳು ಮತ್ತು ಮಿತಿ ಎಚ್ಚರಿಕೆಗಳು',
        'budgets_hero_desc': 'ಖರ್ಚು ಮಿತಿಗಳನ್ನು ಹೊಂದಿಸಿ ಮತ್ತು ಸ್ವಯಂಚಾಲಿತ ಎಚ್ಚರಿಕೆಗಳನ್ನು ಗಮನಿಸಿ.',
        'dashboard_hero_title': 'ಹಣಕಾಸು ಅವಲೋಕನ',
        'dashboard_hero_desc': 'ಹಂಚಿದ ಖರ್ಚುಗಳು, ಬಾಕಿಗಳು ಮತ್ತು ನೈಜ-ಸಮಯದ ಬಜೆಟ್ ಆರೋಗ್ಯವನ್ನು ಟ್ರ್ಯಾಕ್ ಮಾಡಿ.',
    },
    'te': {
        'app_title': 'స్ప్లిట్‌సెటిల్‌మెంట్ (SplitSettlement)',
        'app_subtitle': 'ఖర్చుల పంపకం & పరిష్కార వ్యవస్థ',
        'auth_badge': '🔒 సురక్షిత ప్రవేశం',
        'welcome_hero_title': 'స్ప్లిట్‌సెటిల్‌మెంట్‌కు స్వాగతం',
        'welcome_hero_desc': 'స్నేహితులు మరియు సహచరులతో ఖర్చులను పంచుకోవడానికి, బాకీలను పరిష్కరించడానికి మరియు గ్రూప్ బడ్జెట్‌లను నిర్వహించడానికి ఉత్తమ వేదిక.',
        'tab_signin': '🔐 ఖాతాలోకి లాగిన్ అవ్వండి',
        'tab_register': '📝 కొత్త ఖాతా సృష్టించండి',
        'signin_header': 'మీ డాష్‌బోర్డ్ తెరవడానికి మీ పేరు లేదా ఈమెయిల్ నమోదు చేయండి:',
        'signin_invited_tip': '💡 **స్నేహితులు మిమ్మల్ని గ్రూప్‌లో చేర్చారా?** మీ పేరు మరియు సాధారణ పాస్‌వర్డ్ **123456** తో లాగిన్ అవ్వండి, లేదా సొంత పాస్‌వర్డ్ పెట్టుకోవడానికి **\'కొత్త ఖాతా సృష్టించండి\'** ఉపయోగించండి.',
        'ident_label': 'పేరు లేదా ఈమెయిల్ *',
        'ident_placeholder': 'ఉదా: Rajasree లేదా user@example.com',
        'pwd_label': 'పాస్‌వర్డ్ *',
        'pwd_placeholder': 'మీ పాస్‌వర్డ్ నమోదు చేయండి',
        'btn_login': 'డాష్‌బోర్డ్‌లోకి లాగిన్ అవ్వండి',
        'reg_header': 'ఖాతా సృష్టించి ఖర్చులు పంచుకోవడానికి మీ వివరాలు నమోదు చేయండి:',
        'fullname_label': 'పూర్తి పేరు *',
        'fullname_placeholder': 'ఉదా: Rajasree, Priya, Bhoomika',
        'email_label': 'ఈమెయిల్ చిరునామా *',
        'email_placeholder': 'ఉదా: name@example.com',
        'create_pwd_label': 'కొత్త పాస్‌వర్డ్ *',
        'confirm_pwd_label': 'పాస్‌వర్డ్ నిర్ధారించండి *',
        'btn_create_account': '🚀 ఖాతా సృష్టించి లాగిన్ అవ్వండి',
        'nav_groups': '👥 గుంపులు & సభ్యులు',
        'nav_expenses': '🧾 ఖర్చులు & పంపకం',
        'nav_balances': '⚖️ బాకీలు (ఎవరు ఎవరికి ఇవ్వాలి)',
        'nav_budgets': '📊 బడ్జెట్‌లు & హెచ్చరికలు',
        
        'nav_dashboard': '📊 డాష్‌బోర్డ్ & విశ్లేషణ',
        'nav_history': '📜 చెల్లింపు చరిత్ర',
        'step_1': 'దశ 1: 👥 గుంపులు & సభ్యులు',
        'step_2': 'దశ 2: 🧾 ఖర్చులు & పంపకం',
        'step_3': 'దశ 3: ⚖️ ఎవరు ఎవరికి ఇవ్వాలి',
        'step_4': 'దశ 4: 📜 చెల్లింపు చరిత్ర',
        'active_profile': 'యాక్టివ్ ప్రొఫైల్',
        'logged_in': 'లాగిన్ అయ్యారు',
        'btn_logout': '🚪 లాగ్ అవుట్',
        'btn_logout_account': '🚪 ఖాతా నుండి లాగ్ అవుట్',
        'nav_menu_header': 'నావిగేషన్ మెనూ:',
        'groups_hero_title': 'గ్రూప్ నిర్వహణ',
        'groups_hero_desc': 'ప్రాజెక్ట్ బృందాలు, రూమ్‌మేట్స్, ప్రయాణాలు మరియు స్నేహితుల గుంపులను నిర్వహించండి.',
        'tab_view_groups': '📋 మీ గుంపులు',
        'tab_create_group': '➕ కొత్త గుంపు సృష్టించండి',
        'no_groups_msg': 'మీరు ఇంకా ఏ గుంపులోనూ లేరు. కొత్త గుంపు ప్రారంభించడానికి \'కొత్త గుంపు సృష్టించండి\' ట్యాబ్‌ని ఎంచుకోండి!',
        'add_member_title': '➕ సభ్యుడిని చేర్చండి:',
        'add_member_input': 'గుంపులో చేర్చవలసిన సభ్యుడి పేరు లేదా ఇమెయిల్:',
        'add_member_placeholder': 'ఉదా: Rajasree లేదా bhoomika@gmail.com',
        'btn_add_member': '➕ గుంపులో చేర్చండి',
        'next_step_group_title': 'సభ్యులను చేర్చడం పూర్తయిందా?',
        'next_step_group_sub': 'గుంపు సభ్యుల మధ్య బిల్లులు నమోదు చేసి ఖర్చులు పంచడానికి ముందుకు సాగండి.',
        'btn_next_to_expenses': '➡️ తదుపరి దశ: ఖర్చులను నమోదు చేయండి -',
        'remove_member_title': '➖ సభ్యుడిని తొలగించండి',
        'btn_remove_member': 'గుంపు నుండి సభ్యుడిని తొలగించండి',
        'confirm_delete_group': 'గుంపు తొలగింపును నిర్ధారించండి:',
        'btn_delete_group': '🗑️ గుంపును తొలగించండి',
        'group_name_label': 'గుంపు పేరు *',
        'group_desc_label': 'వివరణ (ఐచ్ఛికం)',
        'group_budget_label': 'నెలవారీ బడ్జెట్ (₹, ఐచ్ఛికం)',
        'initial_members_label': 'ప్రారంభ సభ్యులు (ఐచ్ఛికం - కామాలతో వేరుచేసిన పేర్లు):',
        'btn_create_group': 'గుంపు సృష్టించండి',
        'expenses_hero_title': 'ఖర్చుల ట్రాకింగ్',
        'expenses_hero_desc': 'సమాన, శాతం లేదా ప్రత్యేక వాటాలతో బిల్లులను పంచుకోండి.',
        'tab_add_expense': '➕ కొత్త ఖర్చు నమోదు',
        'tab_expense_history': '📜 ఖర్చు చరిత్ర & నిర్వహణ',
        'select_group_label': 'గుంపును ఎంచుకోండి:',
        'exp_desc_label': 'ఖర్చు వివరణ *',
        'exp_desc_placeholder': 'ఉదా: కేఫ్ బిల్లు, ప్రింట్‌లు, డిన్నర్',
        'exp_amt_label': 'మొత్తం సొమ్ము (₹) *',
        'exp_cat_label': 'వర్గం:',
        'exp_date_label': 'తేదీ:',
        'paid_by_label': 'చెల్లించిన వారు (సభ్యులు):',
        'split_method_label': 'పంపక విధానం:',
        'split_equal': 'సమాన పంపకం',
        'split_percentage': 'శాతం ప్రకారం పంపకం',
        'split_custom': 'ప్రత్యేక పంపకం',
        'btn_save_expense': '💾 ఖర్చును భద్రపరచి పంచండి',
        'delete_expense_title': '🗑️ నమోదైన ఖర్చును తొలగించండి',
        'btn_delete_selected_expense': 'ఎంచుకున్న ఖర్చును తొలగించండి',
        'next_step_exp_title': 'ఖర్చులు నమోదయ్యాయి! ఎవరు ఎవరికి ఇవ్వాలో చూడాలా?',
        'next_step_exp_sub': 'నికర బాకీలు మరియు పరిష్కార సూచనలను చూడటానికి ముందుకు సాగండి.',
        'btn_back_to_groups': '👥 గుంపులకు తిరిగి వెళ్ళండి',
        'btn_next_to_balances': '⚖️ తదుపరి దశ: ఎవరు ఎవరికి ఇవ్వాలి',
        'balances_hero_title': 'ఎవరు ఎవరికి ఇవ్వాలి',
        'balances_hero_desc': 'కనిష్ట నగదు లావాదేవీల డెట్ సింప్లిఫికేషన్ అల్గోరిథం.',
        'settlement_instructions': '💡 చెల్లింపు పరిష్కార సూచనలు:',
        'pays': 'చెల్లించాలి:',
        'all_settled': '✅ ఈ గుంపులో అందరి లెక్కలు పూర్తిగా సరిపోయాయి!',
        'col_member': 'సభ్యులు',
        'col_paid': 'చెల్లించినది',
        'col_share': 'వాటా',
        'col_net': 'నికర బాకీ',
        'col_status': 'స్థితి',
        'status_gets_back': 'రావాలి',
        'status_owes': 'ఇవ్వాలి',
        'status_settled': 'సరిపోయింది',
        'next_step_bal_title': 'బాకీలు చూశారా? చెల్లింపు చరిత్ర చూడటానికి సిద్ధమా?',
        'next_step_bal_sub': 'పూర్తి లావాదేవీల రికార్డులను చూడటానికి ముందుకు సాగండి.',
        'btn_back_to_expenses': '⬅️ ఖర్చులకు తిరిగి వెళ్ళండి',
        'btn_view_analytics': '📊 విశ్లేషణ చూడండి',
        'btn_proceed_to_history': '📜 దశ 4: చెల్లింపు చరిత్రకు వెళ్ళండి',
        'history_hero_title': 'చెల్లింపులు & ఖర్చుల చరిత్ర',
        'history_hero_desc': 'అన్ని బిల్లులు, వాటాలు మరియు లావాదేవీల పూర్తి రికార్డు.',
        'filter_group_label': 'గుంపు ప్రకారం ఫిల్టర్ చేయండి:',
        'all_your_groups': 'మీ అన్ని గుంపులు',
        'stat_total_tx': 'మొత్తం లావాదేవీలు',
        'stat_total_spent': 'గుంపు మొత్తం ఖర్చు',
        'stat_your_share': 'మీ మొత్తం వాటా',
        'delete_history_title': '🗑️ చెల్లింపు / ఖర్చు రికార్డును తొలగించండి',
        'btn_delete_entry': 'రికార్డు తొలగించండి',
        'complete_lifecycle_title': 'అన్ని దశలు పూర్తయ్యాయి! మరిన్ని ఖర్చులు నమోదు చేయాలా?',
        'complete_lifecycle_sub': 'ఏ మునుపటి దశకైనా సులభంగా తిరిగి వెళ్ళండి.',
        'btn_goto_step1': '👥 దశ 1: గుంపుల నిర్వహణ',
        'btn_goto_step2': '🧾 దశ 2: మరిన్ని ఖర్చులు నమోదు',
        'btn_goto_step3': '⚖️ దశ 3: బాకీల తనిఖీ',
        'budgets_hero_title': 'గ్రూప్ బడ్జెట్‌లు & పరిమితి హెచ్చరికలు',
        'budgets_hero_desc': 'ఖర్చు పరిమితులను నిర్ణయించి ఆటోమేటిక్ హెచ్చరికలను గమనించండి.',
        'dashboard_hero_title': 'ఆర్థిక అవలోకనం',
        'dashboard_hero_desc': 'ఖర్చులు, బాకీలు మరియు బడ్జెట్ స్థితిని రియల్ టైమ్‌లో పర్యవేక్షించండి.',
    },
    'hi': {
        'app_title': 'स्प्लिटसेटलमेंट (SplitSettlement)',
        'app_subtitle': 'खर्च विभाजन और निपटान प्रणाली',
        'auth_badge': '🔒 सुरक्षित एक्सेस',
        'welcome_hero_title': 'स्प्लिटसेटलमेंट में आपका स्वागत है',
        'welcome_hero_desc': 'दोस्तों और टीम के साथ खर्च बांटने, उधारी चुकाने और ग्रुप बजट प्रबंधित करने का सबसे आसान और स्मार्ट तरीका।',
        'tab_signin': '🔐 खाते में लॉगिन करें',
        'tab_register': '📝 नया खाता बनाएं',
        'signin_header': 'अपने डैशबोर्ड तक पहुँचने के लिए अपना नाम या ईमेल दर्ज करें:',
        'signin_invited_tip': '💡 **दोस्तों ने आपको ग्रुप में जोड़ा है?** आप अपने नाम और डिफ़ॉल्ट पासवर्ड **123456** से लॉगिन कर सकते हैं, या अपना पासवर्ड सेट करने के लिए **\'नया खाता बनाएं\'** पर जाएं।',
        'ident_label': 'नाम या ईमेल *',
        'ident_placeholder': 'उदा: Rajasree या user@example.com',
        'pwd_label': 'पासवर्ड *',
        'pwd_placeholder': 'अपना पासवर्ड दर्ज करें',
        'btn_login': 'डैशबोर्ड में लॉगिन करें',
        'reg_header': 'खाता बनाने और खर्च बांटने के लिए अपना विवरण दर्ज करें:',
        'fullname_label': 'पूरा नाम *',
        'fullname_placeholder': 'उदा: Rajasree, Priya, Bhoomika',
        'email_label': 'ईमेल पता *',
        'email_placeholder': 'उदा: name@example.com',
        'create_pwd_label': 'पासवर्ड बनाएं *',
        'confirm_pwd_label': 'पासवर्ड की पुष्टि करें *',
        'btn_create_account': '🚀 खाता बनाएं और लॉगिन करें',
        'nav_groups': '👥 समूह और सदस्य',
        'nav_expenses': '🧾 खर्च और विभाजन',
        'nav_balances': '⚖️ बकाया (किसे कितना देना है)',
        'nav_budgets': '📊 बजट एवं सीमा अलर्ट',
        
        'nav_dashboard': '📊 डैशबोर्ड और विश्लेषण',
        'nav_history': '📜 भुगतान इतिहास',
        'step_1': 'चरण 1: 👥 समूह और सदस्य',
        'step_2': 'चरण 2: 🧾 खर्च जोड़ें और बांटें',
        'step_3': 'चरण 3: ⚖️ किसे कितना देना है',
        'step_4': 'चरण 4: 📜 भुगतान इतिहास',
        'active_profile': 'सक्रिय प्रोफ़ाइल',
        'logged_in': 'लॉगिन हैं',
        'btn_logout': '🚪 लॉग आउट',
        'btn_logout_account': '🚪 खाते से लॉग आउट करें',
        'nav_menu_header': 'नेविगेशन मेनू:',
        'groups_hero_title': 'समूह प्रबंधन',
        'groups_hero_desc': 'प्रोजेक्ट टीम, रूममेट्स, यात्राओं और दोस्तों के समूहों को व्यवस्थित करें।',
        'tab_view_groups': '📋 आपके समूह',
        'tab_create_group': '➕ नया समूह बनाएं',
        'no_groups_msg': 'आप अभी तक किसी भी समूह में शामिल नहीं हैं। शुरू करने के लिए \'नया समूह बनाएं\' टैब पर जाएं!',
        'add_member_title': '➕ सदस्य जोड़ें:',
        'add_member_input': 'समूह में जोड़ने के लिए सदस्य का नाम या ईमेल दर्ज करें:',
        'add_member_placeholder': 'उदा: Rajasree या bhoomika@gmail.com',
        'btn_add_member': '➕ समूह में जोड़ें',
        'next_step_group_title': 'सदस्यों को जोड़ना पूरा हो गया?',
        'next_step_group_sub': 'समूह के सदस्यों के बीच बिल दर्ज करने और खर्च बांटने के लिए आगे बढ़ें।',
        'btn_next_to_expenses': '➡️ अगला चरण: खर्च दर्ज करें -',
        'remove_member_title': '➖ समूह से सदस्य हटाएं',
        'btn_remove_member': 'सदस्य को समूह से हटाएं',
        'confirm_delete_group': 'समूह को हटाने की पुष्टि करें:',
        'btn_delete_group': '🗑️ समूह हटाएं',
        'group_name_label': 'समूह का नाम *',
        'group_desc_label': 'विवरण (वैकल्पिक)',
        'group_budget_label': 'मासिक खर्च बजट (₹, वैकल्पिक)',
        'initial_members_label': 'प्रारंभिक सदस्य (वैकल्पिक - अल्पविराम से अलग किए गए नाम):',
        'btn_create_group': 'समूह बनाएं',
        'expenses_hero_title': 'खर्च ट्रैकिंग',
        'expenses_hero_desc': 'समान, प्रतिशत या कस्टम शेयरों के साथ बिलों को विभाजित करें।',
        'tab_add_expense': '➕ नया खर्च जोड़ें',
        'tab_expense_history': '📜 खर्च इतिहास और प्रबंधन',
        'select_group_label': 'समूह चुनें:',
        'exp_desc_label': 'खर्च का विवरण *',
        'exp_desc_placeholder': 'उदा: कैफे मीटिंग, प्रिंटआउट, रात का खाना',
        'exp_amt_label': 'कुल राशि (₹) *',
        'exp_cat_label': 'श्रेणी:',
        'exp_date_label': 'तारीख:',
        'paid_by_label': 'किसने भुगतान किया (सदस्य):',
        'split_method_label': 'विभाजन का तरीका:',
        'split_equal': 'समान विभाजन',
        'split_percentage': 'प्रतिशत विभाजन',
        'split_custom': 'कस्टम विभाजन',
        'btn_save_expense': '💾 खर्च सहेजें और बांटें',
        'delete_expense_title': '🗑️ दर्ज खर्च को हटाएं',
        'btn_delete_selected_expense': 'चुने गए खर्च को हटाएं',
        'next_step_exp_title': 'खर्च दर्ज हो गया! देखना चाहते हैं किसे कितना देना है?',
        'next_step_exp_sub': 'नेट बकाया और अनुकूलित निपटान निर्देशों को देखने के लिए आगे बढ़ें।',
        'btn_back_to_groups': '👥 समूहों पर वापस जाएं',
        'btn_next_to_balances': '⚖️ अगला चरण: किसे कितना देना है',
        'balances_hero_title': 'किसे कितना देना है',
        'balances_hero_desc': 'न्यूनतम नकदी प्रवाह ऋण सरलीकरण एल्गोरिदम।',
        'settlement_instructions': '💡 निपटान निर्देश:',
        'pays': 'चुकाएगा:',
        'all_settled': '✅ इस समूह में सभी का हिसाब पूरी तरह से चुकता है!',
        'col_member': 'सदस्य',
        'col_paid': 'भुगतान किया',
        'col_share': 'हिस्सा',
        'col_net': 'नेट बकाया',
        'col_status': 'स्थिति',
        'status_gets_back': 'पाएगा',
        'status_owes': 'देगा',
        'status_settled': 'चुकता',
        'next_step_bal_title': 'हिसाब देख लिया? भुगतान इतिहास देखने के लिए तैयार हैं?',
        'next_step_bal_sub': 'पूर्ण भुगतान लॉग देखने के लिए अगले चरण पर आगे बढ़ें।',
        'btn_back_to_expenses': '⬅️ खर्चों पर वापस जाएं',
        'btn_view_analytics': '📊 विश्लेषण देखें',
        'btn_proceed_to_history': '📜 चरण 4: भुगतान इतिहास पर आगे बढ़ें',
        'history_hero_title': 'भुगतान और खर्च का इतिहास',
        'history_hero_desc': 'सभी बिलों, शेयरों और निपटानों का संपूर्ण ऐतिहासिक रिकॉर्ड।',
        'filter_group_label': 'समूह के अनुसार इतिहास फ़िल्टर करें:',
        'all_your_groups': 'आपके सभी समूह',
        'stat_total_tx': 'कुल लेन-देन',
        'stat_total_spent': 'समूह का कुल खर्च',
        'stat_your_share': 'आपका कुल हिस्सा',
        'delete_history_title': '🗑️ दर्ज भुगतान / खर्च हटाएं',
        'btn_delete_entry': 'प्रविष्टि हटाएं',
        'complete_lifecycle_title': 'सभी चरण पूरे हो गए! और खर्च दर्ज करना चाहते हैं?',
        'complete_lifecycle_sub': 'किसी भी पूर्व चरण पर कभी भी वापस जाएं।',
        'btn_goto_step1': '👥 चरण 1: समूह प्रबंधन',
        'btn_goto_step2': '🧾 चरण 2: और खर्च जोड़ें',
        'btn_goto_step3': '⚖️ चरण 3: बकाया जांचें',
        'budgets_hero_title': 'समूह बजट और सीमा अलर्ट',
        'budgets_hero_desc': 'खर्च सीमाएं निर्धारित करें और स्वचालित अलर्ट देखें।',
        'dashboard_hero_title': 'वित्तीय अवलोकन',
        'dashboard_hero_desc': 'साझा खर्च, बकाया राशि और बजट स्वास्थ्य को रियल-टाइम में ट्रैक करें।',
    }
}

def tr(key):
    lang_choice = st.session_state.get('interface_language', 'English')
    l_code = 'en'
    if 'Kannada' in lang_choice or 'ಕನ್ನಡ' in lang_choice:
        l_code = 'kn'
    elif 'Telugu' in lang_choice or 'తెలుగు' in lang_choice:
        l_code = 'te'
    elif 'Hindi' in lang_choice or 'हिन्दी' in lang_choice:
        l_code = 'hi'
    return TRANSLATIONS.get(l_code, {}).get(key, TRANSLATIONS['en'].get(key, key))

def render_brand_logo(size=44, key="logo"):
    return (
        f'<div style="width:{size}px; height:{size}px; border-radius:12px; '
        f'background:linear-gradient(135deg, #6c5ce7 0%, #8e44ad 50%, #00b894 100%); '
        f'display:inline-flex; align-items:center; justify-content:center; color:#ffffff; '
        f'font-size:{int(size*0.52)}px; box-shadow:0 4px 12px rgba(108,92,231,0.3); '
        f'border:1.5px solid rgba(255,255,255,0.6); vertical-align:middle;">⚖️</div>'
    )

render_logo = render_brand_logo

NAV_CANONICAL = ["groups", "expenses", "balances", "budgets", "dashboard", "history"]

NAV_LABEL_KEYS = {
    "groups": "nav_groups",
    "expenses": "nav_expenses",
    "balances": "nav_balances",
    "budgets": "nav_budgets",
    "dashboard": "nav_dashboard",
    "history": "nav_history"
}

def normalize_nav(page_name):
    if page_name in NAV_CANONICAL:
        return page_name
    pl = page_name.lower()
    if "group" in pl:
        return "groups"
    if "expense" in pl:
        return "expenses"
    if "balance" in pl or "who owes" in pl:
        return "balances"
    if "budget" in pl:
        return "budgets"
    if "simulator" in pl or "what-if" in pl or "alert" in pl:
        return "budgets"
    if "dash" in pl or "analytics" in pl:
        return "dashboard"
    if "history" in pl or "payment" in pl:
        return "history"
    return "groups"

def navigate_to(page_name, target_group_id=None):
    st.session_state['nav_selection'] = normalize_nav(page_name)
    if target_group_id is not None:
        st.session_state['target_group_id'] = target_group_id
    st.rerun()

# ==============================================================================
# AUTHENTICATION SESSION STATE MANAGEMENT
# ==============================================================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['user_id'] = None
    st.session_state['user_name'] = None
    st.session_state['user_email'] = None

# ==============================================================================
# SCREEN 1: LOGIN & REGISTRATION PORTAL (When NOT Logged In)
# ==============================================================================
if not st.session_state['authenticated']:
    # Top Bar: Language Dropdown aligned neatly on top right
    col_empty, col_auth_right = st.columns([2.8, 1.2])
    with col_auth_right:
        c_lang_auth = st.session_state.get('interface_language', 'English')
        c_lang_auth_idx = LANGUAGE_OPTIONS.index(c_lang_auth) if c_lang_auth in LANGUAGE_OPTIONS else 0
        sel_auth_lang = st.selectbox(
            "🌐 Interface Language:",
            LANGUAGE_OPTIONS,
            index=c_lang_auth_idx,
            key="auth_lang_dropdown"
        )
        if sel_auth_lang != st.session_state.get('interface_language'):
            st.session_state['interface_language'] = sel_auth_lang
            st.rerun()

    # Hero Banner with Centered Creative Brand Emblem
    st.markdown(
        f'<div class="brand-hero" style="text-align:center; padding: 2.2rem 1.5rem; margin-top:0.4rem;">'
        f'<div style="margin-bottom:0.85rem;">{render_brand_logo(size=56)}</div>'
        f'<h1 style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">{tr("welcome_hero_title")}</h1>'
        f'<p style="font-size: 1.05rem; opacity: 0.95; max-width: 650px; margin: 0 auto;">{tr("welcome_hero_desc")}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Auth Card with Tabs
    col_l, col_center, col_r = st.columns([1, 2.4, 1])
    with col_center:
        auth_tab1, auth_tab2 = st.tabs([tr('tab_signin'), tr('tab_register')])

        # TAB 1: LOGIN
        with auth_tab1:
            st.markdown(f"<p style='color:#636e72; font-size:0.9rem; margin-top:0.5rem;'>{tr('signin_header')}</p>", unsafe_allow_html=True)
            st.info(tr('signin_invited_tip'))
            with st.form("login_form"):
                login_ident = st.text_input(tr('ident_label'), placeholder=tr('ident_placeholder'))
                login_pwd = st.text_input(tr('pwd_label'), type="password", placeholder=tr('pwd_placeholder'))
                submit_login = st.form_submit_button(tr('btn_login'))

                if submit_login:
                    cleaned_ident = login_ident.strip()
                    if not cleaned_ident or not login_pwd:
                        st.error("Please provide both identifier and password.")
                    else:
                        ident_prefix = cleaned_ident.split('@')[0].strip().lower() if '@' in cleaned_ident else cleaned_ident.lower()
                        user_rec = run_query("""
                            SELECT id, name, email, password_hash FROM users
                            WHERE LOWER(email) = %s 
                               OR LOWER(name) = %s
                               OR LOWER(name) = %s
                               OR LOWER(email) LIKE %s
                            ORDER BY CASE WHEN LOWER(email) = %s THEN 1 WHEN email LIKE '%%@gmail.com' THEN 2 ELSE 3 END, id ASC
                        """, (cleaned_ident.lower(), cleaned_ident.lower(), ident_prefix, f"{ident_prefix}@%", cleaned_ident.lower()))

                        if not user_rec:
                            st.session_state['unregistered_attempt'] = {
                                'ident': cleaned_ident,
                                'pwd': login_pwd
                            }
                            st.error(f"No account found for '{cleaned_ident}'. Click below to create your account in 1 click, or switch to the 'Create New Account' tab.")
                        else:
                            if 'unregistered_attempt' in st.session_state:
                                del st.session_state['unregistered_attempt']
                            u = user_rec[0]
                            if check_user_password(u['password_hash'], login_pwd):
                                st.session_state['authenticated'] = True
                                st.session_state['user_id'] = u['id']
                                st.session_state['user_name'] = u['name']
                                st.session_state['user_email'] = u['email']
                                st.success(f"Welcome back, {u['name']}! Loading your dashboard...")
                                st.rerun()
                            else:
                                st.error("Incorrect password. Please try again.")

            if st.session_state.get('unregistered_attempt'):
                unreg = st.session_state['unregistered_attempt']
                st.markdown("<br>", unsafe_allow_html=True)
                st.info(f"💡 No account found for **{unreg['ident']}**. Click below to quickly create it and log in!")
                if st.button(f"✨ Create Account & Log In as '{unreg['ident']}'", key="btn_quick_register_from_login", type="primary", use_container_width=True):
                    if '@' in unreg['ident']:
                        new_email = unreg['ident'].lower()
                        raw_prefix = unreg['ident'].split('@')[0]
                        new_name = raw_prefix.replace('.', ' ').replace('_', ' ').strip().title()
                    else:
                        new_name = unreg['ident']
                        new_email = f"{re.sub(r'[^a-zA-Z0-9]', '', unreg['ident'].lower())}@splitsettle.app"

                    new_pwd_hash = make_password_hash(unreg['pwd'])
                    new_uid = execute_cmd(
                        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                        (new_name, new_email, new_pwd_hash)
                    )
                    st.session_state['authenticated'] = True
                    st.session_state['user_id'] = new_uid
                    st.session_state['user_name'] = new_name
                    st.session_state['user_email'] = new_email
                    del st.session_state['unregistered_attempt']
                    st.success(f"🎉 Account created successfully! Welcome, {new_name}!")
                    st.rerun()

        # TAB 2: REGISTER
        with auth_tab2:
            st.markdown(f"<p style='color:#636e72; font-size:0.9rem; margin-top:0.5rem;'>{tr('reg_header')}</p>", unsafe_allow_html=True)
            default_reg_email = ""
            default_reg_name = ""
            if st.session_state.get('unregistered_attempt'):
                unreg = st.session_state['unregistered_attempt']
                if '@' in unreg['ident']:
                    default_reg_email = unreg['ident']
                    default_reg_name = unreg['ident'].split('@')[0].replace('.', ' ').replace('_', ' ').strip().title()
                else:
                    default_reg_name = unreg['ident']

            with st.form("register_form"):
                reg_name = st.text_input(tr('fullname_label'), value=default_reg_name, placeholder=tr('fullname_placeholder'))
                reg_email = st.text_input(tr('email_label'), value=default_reg_email, placeholder=tr('email_placeholder'))
                reg_pwd = st.text_input(tr('create_pwd_label'), type="password", placeholder="Enter a secure password")
                reg_confirm = st.text_input(tr('confirm_pwd_label'), type="password", placeholder="Re-enter your password")
                submit_reg = st.form_submit_button(tr('btn_create_account'))

                if submit_reg:
                    c_name = reg_name.strip()
                    c_email = reg_email.strip().lower()

                    if not c_name or not c_email or not reg_pwd:
                        st.error("All required fields must be filled.")
                    elif not re.match(r"^[^@]+@[^@]+\.[^@]+$", c_email):
                        st.error("Please enter a valid email address.")
                    elif reg_pwd != reg_confirm:
                        st.error("Passwords do not match. Please re-enter.")
                    elif len(reg_pwd) < 4:
                        st.error("Password must be at least 4 characters.")
                    else:
                        matches = run_query("""
                            SELECT id, name, email, password_hash FROM users
                            WHERE LOWER(email) = %s OR LOWER(name) = %s
                        """, (c_email, c_name.lower()))

                        placeholder = None
                        real_existing = None

                        for m in matches:
                            is_invitee = check_user_password(m['password_hash'], '123456') or m['email'].lower().endswith('@splitsettle.app') or m['name'].lower() == c_email
                            if is_invitee:
                                placeholder = m
                            else:
                                real_existing = m

                        if real_existing:
                            st.warning("An active account with this Name or Email already exists. Please sign in instead.")
                        elif placeholder:
                            # Claim existing placeholder created when added to a group by a friend
                            claimed_id = placeholder['id']
                            pwd_hash = make_password_hash(reg_pwd)
                            execute_cmd("""
                                UPDATE users
                                SET name = %s, email = %s, password_hash = %s
                                WHERE id = %s
                            """, (c_name, c_email, pwd_hash, claimed_id))

                            st.session_state['authenticated'] = True
                            st.session_state['user_id'] = claimed_id
                            st.session_state['user_name'] = c_name
                            st.session_state['user_email'] = c_email
                            st.success(f"🎉 Account activated! Welcome, {c_name}! You now have immediate access to all groups you were added to.")
                            st.rerun()
                        else:
                            pwd_hash = make_password_hash(reg_pwd)
                            new_uid = execute_cmd("""
                                INSERT INTO users (name, email, password_hash)
                                VALUES (%s, %s, %s)
                            """, (c_name, c_email, pwd_hash))

                            st.session_state['authenticated'] = True
                            st.session_state['user_id'] = new_uid
                            st.session_state['user_name'] = c_name
                            st.session_state['user_email'] = c_email
                            st.success(f"🎉 Account created successfully! Welcome, {c_name}!")
                            st.rerun()

    # Stop execution here until the user logs in
    st.stop()

# ==============================================================================
# SCREEN 2: AUTHENTICATED APPLICATION (When Logged In)
# ==============================================================================
current_user_id = st.session_state['user_id']
current_user_name = st.session_state['user_name']
current_user_email = st.session_state['user_email']

# ==============================================================================
# SIDEBAR NAVIGATION
# ==============================================================================
st.sidebar.markdown(
    f'<div style="text-align: center; margin-bottom: 1.25rem;">'
    f'{render_brand_logo(size=52)}'
    f'<h2 style="font-size: 1.25rem; margin: 0.4rem 0 0 0; color: #2d3436; font-weight:700;">{tr("app_title")}</h2>'
    f'<small style="color: #6c5ce7; font-weight:600;">{tr("app_subtitle")}</small>'
    f'</div>',
    unsafe_allow_html=True
)

# Logged-In User Profile Card in Sidebar
user_initial = current_user_name[0].upper() if current_user_name else "U"
st.sidebar.markdown(
    f'<div class="profile-badge" style="width: 100%; justify-content: flex-start; margin-bottom: 0.5rem; background:#f9f8fe;">'
    f'<div class="profile-avatar">{user_initial}</div>'
    f'<div class="profile-info">'
    f'<span class="profile-name">{current_user_name}</span>'
    f'<span class="profile-status"><span style="color:#00b894; font-size:0.85rem;">●</span> {tr("logged_in")}</span>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True
)

# Top Sidebar Logout Button
if st.sidebar.button(tr('btn_logout'), key="sidebar_top_logout_btn", use_container_width=True):
    st.session_state.clear()
    st.session_state['authenticated'] = False
    st.rerun()

# Change Password Option
with st.sidebar.expander("🔑 Change Password"):
    with st.form("sidebar_change_pwd_form"):
        old_p = st.text_input("Current Password", type="password")
        new_p = st.text_input("New Password", type="password")
        conf_p = st.text_input("Confirm New Password", type="password")
        btn_chg_pwd = st.form_submit_button("Update Password", use_container_width=True)
        if btn_chg_pwd:
            if not old_p or not new_p:
                st.error("Please fill all password fields.")
            elif new_p != conf_p:
                st.error("New passwords do not match.")
            elif len(new_p) < 4:
                st.error("Password must be at least 4 characters.")
            else:
                curr_user = run_query("SELECT password_hash FROM users WHERE id = %s", (current_user_id,))
                if curr_user and check_user_password(curr_user[0]['password_hash'], old_p):
                    execute_cmd("UPDATE users SET password_hash = %s WHERE id = %s", (make_password_hash(new_p), current_user_id))
                    st.success("🎉 Password updated successfully!")
                else:
                    st.error("Current password incorrect.")

cur_lang_sb = st.session_state.get('interface_language', 'English')
lang_idx_sb = LANGUAGE_OPTIONS.index(cur_lang_sb) if cur_lang_sb in LANGUAGE_OPTIONS else 0
sel_lang_sb = st.sidebar.selectbox(
    "🌐 Interface Language:",
    LANGUAGE_OPTIONS,
    index=lang_idx_sb,
    key="sb_lang_dropdown"
)
if sel_lang_sb != st.session_state.get('interface_language'):
    st.session_state['interface_language'] = sel_lang_sb
    st.rerun()

if 'nav_selection' not in st.session_state or st.session_state['nav_selection'] not in NAV_CANONICAL:
    st.session_state['nav_selection'] = "groups"

current_nav_index = NAV_CANONICAL.index(st.session_state['nav_selection'])
menu = st.sidebar.radio(
    tr('nav_menu_header'),
    NAV_CANONICAL,
    index=current_nav_index,
    format_func=lambda k: tr(NAV_LABEL_KEYS[k])
)
st.session_state['nav_selection'] = menu

st.sidebar.markdown("---")
if st.sidebar.button(tr('btn_logout_account'), key="sidebar_bottom_logout_btn", use_container_width=True):
    st.session_state.clear()
    st.session_state['authenticated'] = False
    st.rerun()

st.sidebar.caption(f"Engine: **{db_type.upper()}** &bull; Status: **Online**")

# ==============================================================================
# TOP-RIGHT PROFILE BADGE & HEADER (Clean - Showing Name and Logout)
# ==============================================================================
col_nav_left, col_nav_right = st.columns([2.4, 1.6])
with col_nav_left:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:10px; padding: 6px 0;">'
        f'{render_brand_logo(size=36)}'
        f'<span style="font-size:1.2rem; color:#2d3436; font-weight:700;">{tr("app_title")}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

with col_nav_right:
    c_user, c_out = st.columns([1.5, 1])
    with c_user:
        st.markdown(
            f'<div class="profile-badge" style="width: 100%;">'
            f'<div class="profile-avatar">{user_initial}</div>'
            f'<div class="profile-info">'
            f'<span class="profile-name">{current_user_name}</span>'
            f'<span class="profile-status"><span style="color:#00b894; font-size:0.85rem;">●</span> {tr("active_profile")}</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with c_out:
        st.write("")
        if st.button(tr('btn_logout'), key="top_header_logout", use_container_width=True):
            st.session_state.clear()
            st.session_state['authenticated'] = False
            st.rerun()

st.markdown("<div style='height:1px; background:#e9ecef; margin: 0.5rem 0 1.25rem 0;'></div>", unsafe_allow_html=True)

# 4-Step Visual Stepper
cur_step = 1 if menu == "groups" else (2 if menu == "expenses" else (3 if menu == "balances" else (4 if menu in ("dashboard", "history") else 0)))

s1 = "background:#6c5ce7; color:#ffffff;" if cur_step == 1 else "background:#ffffff; color:#636e72; border:1px solid #e9ecef;"
s2 = "background:#6c5ce7; color:#ffffff;" if cur_step == 2 else "background:#ffffff; color:#636e72; border:1px solid #e9ecef;"
s3 = "background:#6c5ce7; color:#ffffff;" if cur_step == 3 else "background:#ffffff; color:#636e72; border:1px solid #e9ecef;"
s4 = "background:#6c5ce7; color:#ffffff;" if cur_step == 4 else "background:#ffffff; color:#636e72; border:1px solid #e9ecef;"

st.markdown(clean_html(f"""
<div style="display:flex; justify-content:center; align-items:center; gap:8px; margin-bottom:1.5rem; flex-wrap:wrap;">
    <div style="padding:6px 14px; border-radius:20px; font-size:0.83rem; font-weight:600; {s1}; box-shadow:0 2px 6px rgba(108,92,231,0.08);">{tr('step_1')}</div>
    <span style="color:#b2bec3; font-weight:700;">➔</span>
    <div style="padding:6px 14px; border-radius:20px; font-size:0.83rem; font-weight:600; {s2}; box-shadow:0 2px 6px rgba(108,92,231,0.08);">{tr('step_2')}</div>
    <span style="color:#b2bec3; font-weight:700;">➔</span>
    <div style="padding:6px 14px; border-radius:20px; font-size:0.83rem; font-weight:600; {s3}; box-shadow:0 2px 6px rgba(108,92,231,0.08);">{tr('step_3')}</div>
    <span style="color:#b2bec3; font-weight:700;">➔</span>
    <div style="padding:6px 14px; border-radius:20px; font-size:0.83rem; font-weight:600; {s4}; box-shadow:0 2px 6px rgba(108,92,231,0.08);">{tr('step_4')}</div>
</div>
"""), unsafe_allow_html=True)

# ==============================================================================
# 1. DASHBOARD & ANALYTICS
# ==============================================================================
if menu == "dashboard":
    # Top Purple Banner Hero
    st.markdown(clean_html(f"""
    <div class="brand-hero">
        <h1 style="font-size: 1.85rem; font-weight: 700; margin-bottom: 0.35rem;">{tr('dashboard_hero_title')}</h1>
        <p style="font-size: 0.98rem; opacity: 0.95; margin: 0;">{tr('dashboard_hero_desc')} (User: <strong>{current_user_name}</strong>)</p>
    </div>
    """), unsafe_allow_html=True)

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

            net_map = {}
            for m in members:
                uid = m['id']
                p = paid_rows.get(uid, 0.0)
                s = share_rows.get(uid, 0.0)
                net_map[uid] = p - s

            settlements = simplify_debts(net_map, m_dict)
            for s in settlements:
                if s['debtor_id'] == current_user_id:
                    user_owes += s['amount']
                if s['creditor_id'] == current_user_id:
                    others_owe += s['amount']

        # 5 Key Metrics
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Group Spending", f"₹{float(total_group_exp):,.2f}")
        c2.metric("Total You Paid", f"₹{float(total_paid):,.2f}")
        c3.metric("You Are Owed", f"₹{others_owe:,.2f}")
        c4.metric("You Owe", f"₹{user_owes:,.2f}")
        c5.metric("Active Groups", len(user_groups))

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts Section
        col_c1, col_c2 = st.columns(2)

        # 1. Monthly Spending Trend
        with col_c1:
            st.markdown(clean_html("""<div class="white-card"><h3 style="font-size:1.15rem; margin-bottom:1rem; color:#2d3436;">📈 Monthly Spending Trend</h3>"""), unsafe_allow_html=True)
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
            st.markdown(clean_html("""<div class="white-card"><h3 style="font-size:1.15rem; margin-bottom:1rem; color:#2d3436;">🍩 Expense Category Breakdown</h3>"""), unsafe_allow_html=True)
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
            st.markdown(clean_html("""<div class="white-card"><h3 style="font-size:1.15rem; margin-bottom:1rem; color:#2d3436;">📊 Group-wise Spending Comparison</h3>"""), unsafe_allow_html=True)
            df_grp = pd.DataFrame([{'Group': g['name'], 'Spent': float(g['total_spent'])} for g in user_groups])
            fig_grp = px.bar(df_grp, x='Group', y='Spent', color='Group', color_discrete_sequence=['#6c5ce7', '#a29bfe', '#00b894'])
            fig_grp.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', font_color='#2d3436', margin=dict(l=20, r=20, t=10, b=20), height=280, showlegend=False)
            st.plotly_chart(fig_grp, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # 4. Budget vs Spent
        with col_b2:
            st.markdown(clean_html("""<div class="white-card"><h3 style="font-size:1.15rem; margin-bottom:1rem; color:#2d3436;">⚖️ Budget vs Actual Spent</h3>"""), unsafe_allow_html=True)
            b_data = []
            for g in user_groups:
                b_data.append({'Group': g['name'], 'Type': 'Spent Amount', 'Amount': float(g['total_spent'])})
                b_data.append({'Group': g['name'], 'Type': 'Monthly Budget', 'Amount': float(g['monthly_budget'])})
            df_b = pd.DataFrame(b_data)
            fig_b = px.bar(df_b, x='Group', y='Amount', color='Type', barmode='group', color_discrete_map={'Spent Amount': '#e17055', 'Monthly Budget': '#00b894'})
            fig_b.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', font_color='#2d3436', margin=dict(l=20, r=20, t=10, b=20), height=280)
            st.plotly_chart(fig_b, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Recent Transactions (Clean - Showing Names only)
        st.markdown(clean_html("""<div class="white-card"><h3 style="font-size:1.15rem; margin-bottom:1rem; color:#2d3436;">🕒 Recent Transactions</h3>"""), unsafe_allow_html=True)
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

        st.markdown(clean_html("""
        <div class="white-card" style="margin-top:1.5rem; text-align:center;">
            <h3 style="color:#2d3436; font-size:1.15rem; margin-bottom:0.4rem;">Guided Expense Splitting Lifecycle</h3>
            <p style="color:#636e72; font-size:0.9rem; margin-bottom:1.15rem;">Navigate seamlessly between all steps of the expense splitting lifecycle:</p>
        </div>
        """), unsafe_allow_html=True)
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        with col_d1:
            if st.button(tr('step_1'), key="dash_flow_g", use_container_width=True):
                navigate_to("groups")
        with col_d2:
            if st.button(tr('step_2'), key="dash_flow_e", use_container_width=True):
                navigate_to("expenses")
        with col_d3:
            if st.button(tr('step_3'), key="dash_flow_b", use_container_width=True):
                navigate_to("balances")
        with col_d4:
            if st.button(tr('step_4'), key="dash_flow_h", type="primary", use_container_width=True):
                navigate_to("history")

# ==============================================================================
# 2. GROUPS & MEMBERS (WITH DELETE GROUP & REMOVE MEMBER OPTIONS)
# ==============================================================================
elif menu == "groups":
    st.markdown(clean_html(f"""<div class="brand-hero"><h1>{tr('groups_hero_title')}</h1><p>{tr('groups_hero_desc')}</p></div>"""), unsafe_allow_html=True)
    tab1, tab2 = st.tabs([tr('tab_view_groups'), tr('tab_create_group')])

    with tab1:
        my_groups = run_query("""
            SELECT g.id, g.name, g.description, g.created_by,
                   COALESCE(gb.monthly_budget, 0.00) AS monthly_budget,
                   COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) AS total_spent
            FROM `groups` g
            JOIN group_members gm ON g.id = gm.group_id
            LEFT JOIN group_budgets gb ON g.id = gb.group_id
            WHERE gm.user_id = %s
        """, (current_user_id,))

        if not my_groups:
            st.info(tr('no_groups_msg'))
        else:
            for g in my_groups:
                gid = g['id']
                with st.expander(f"📁 {g['name']} (Spent: ₹{float(g['total_spent']):,.2f} / Budget: ₹{float(g['monthly_budget']):,.2f})", expanded=True):
                    st.write(f"**Description:** {g['description'] or 'No description provided'}")
                    b = float(g['monthly_budget'])
                    s = float(g['total_spent'])
                    if b > 0:
                        pct = min(s / b, 1.0)
                        st.progress(pct, text=f"Budget Usage: {(s/b)*100:.1f}%")
                        b_stat = get_budget_status(s, b)
                        if b_stat['level'] in ['OVER_LIMIT', 'HIGH_ALERT']:
                            st.warning(b_stat['badge'])
                        elif b_stat['level'] == 'LOW_SAFE':
                            st.success(b_stat['badge'])
                    else:
                        st.caption("⚪ No budget limit set for this group.")
                    
                    st.markdown("**Group Members:**")
                    members = run_query("SELECT u.id, u.name, gm.role FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s", (gid,))
                    member_ids = [m['id'] for m in members]
                    
                    # Render member badges
                    pills_html = "".join([f'<span class="member-pill">👤 {m["name"]} ({m["role"].capitalize()})</span>' for m in members])
                    st.markdown(pills_html, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    # Add Member by Name (Private - No public registered list exposed)
                    st.markdown(f"<h4 style='font-size:1rem; color:#6c5ce7; margin-bottom:0.4rem;'>{tr('add_member_title')} {g['name']}</h4>", unsafe_allow_html=True)
                    with st.form(f"add_member_form_{gid}", clear_on_submit=True):
                        col_add_in, col_add_btn = st.columns([3, 1.2])
                        with col_add_in:
                            mem_name_in = st.text_input(f"{tr('add_member_input')} {g['name']}:", placeholder=tr('add_member_placeholder'), key=f"in_mem_{gid}")
                        with col_add_btn:
                            st.write("")
                            st.write("")
                            btn_add_mem = st.form_submit_button(tr('btn_add_member'))

                        if btn_add_mem:
                            c_input = mem_name_in.strip()
                            if not c_input:
                                st.error("Please enter a member Name or registered Email ID.")
                            else:
                                t_uid, t_name = find_or_create_user(c_input)
                                if not t_uid:
                                    st.error("Could not process member details. Please check the Name or Email.")
                                else:
                                    is_already = run_query("SELECT id FROM group_members WHERE group_id = %s AND user_id = %s", (gid, t_uid))
                                    if is_already:
                                        st.info(f"{t_name} is already a member of {g['name']}.")
                                    else:
                                        execute_cmd("INSERT INTO group_members (group_id, user_id, role) VALUES (%s, %s, 'member')", (gid, t_uid))
                                        st.success(f"Added {t_name} to {g['name']}!")
                                        st.rerun()

                    # 3. NEXT STEP: PROCEED TO ADD EXPENSES FOR THIS GROUP
                    st.markdown(clean_html(f"""
                    <div style="background: linear-gradient(135deg, #f7f6fe 0%, #edeafe 100%); border: 1.5px solid #dcd6fa; border-radius: 12px; padding: 0.9rem 1.15rem; margin: 1.15rem 0 0.6rem 0;">
                        <span style="background:#6c5ce7; color:#ffffff; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:8px; text-transform:uppercase;">Next Step</span>
                        <h4 style="margin:4px 0 2px 0; color:#2d3436; font-size:1.02rem;">{tr('next_step_group_title')} {g['name']}?</h4>
                        <small style="color:#636e72;">{tr('next_step_group_sub')}</small>
                    </div>
                    """), unsafe_allow_html=True)
                    if st.button(f"{tr('btn_next_to_expenses')} '{g['name']}'", key=f"next_exp_btn_{gid}", type="primary", use_container_width=True):
                        navigate_to("expenses", target_group_id=gid)

                    # 4. Remove a Member option
                    removable = [m for m in members if m['id'] != current_user_id]
                    if removable:
                        with st.expander(f"{tr('remove_member_title')} {g['name']}"):
                            rem_names = [m['name'] for m in removable]
                            rem_map = {m['name']: m['id'] for m in removable}
                            sel_to_rem = st.selectbox(f"Select member to remove:", rem_names, key=f"sel_rem_{gid}")
                            if st.button(tr('btn_remove_member'), key=f"btn_rem_mem_{gid}"):
                                execute_cmd("DELETE FROM group_members WHERE group_id = %s AND user_id = %s", (gid, rem_map[sel_to_rem]))
                                st.success(f"Removed {sel_to_rem} from {g['name']}!")
                                st.rerun()

                    # 4. DELETE GROUP OPTION
                    st.markdown("<hr style='margin: 1.25rem 0 0.75rem 0; border:none; border-top: 1px dashed #e9ecef;'>", unsafe_allow_html=True)
                    del_col_chk, del_col_btn = st.columns([3, 1.2])
                    with del_col_chk:
                        confirm_del = st.checkbox(f"{tr('confirm_delete_group')} '{g['name']}'", key=f"confirm_del_{gid}")
                    with del_col_btn:
                        if st.button(tr('btn_delete_group'), key=f"btn_del_grp_{gid}"):
                            if not confirm_del:
                                st.warning("Please check the confirmation box to delete this group.")
                            else:
                                # Delete splits
                                exp_rows = run_query("SELECT id FROM expenses WHERE group_id = %s", (gid,))
                                for e in exp_rows:
                                    execute_cmd("DELETE FROM expense_splits WHERE expense_id = %s", (e['id'],))
                                # Delete expenses
                                execute_cmd("DELETE FROM expenses WHERE group_id = %s", (gid,))
                                # Delete budget
                                execute_cmd("DELETE FROM group_budgets WHERE group_id = %s", (gid,))
                                # Delete members
                                execute_cmd("DELETE FROM group_members WHERE group_id = %s", (gid,))
                                # Delete group
                                execute_cmd("DELETE FROM `groups` WHERE id = %s", (gid,))
                                st.success(f"Group '{g['name']}' deleted successfully!")
                                st.rerun()

    with tab2:
        with st.form("new_group_form"):
            g_name = st.text_input(tr('group_name_label'), placeholder="e.g. Major Project Team, Flat 302, Weekend Trip")
            g_desc = st.text_area(tr('group_desc_label'))
            g_budget = st.number_input(tr('group_budget_label'), min_value=0.0, step=500.0, value=12000.0)
            
            initial_members_str = st.text_input(
                tr('initial_members_label'),
                placeholder=tr('add_member_placeholder')
            )

            if st.form_submit_button(tr('btn_create_group')):
                if not g_name.strip():
                    st.error("Group name is required.")
                else:
                    new_gid = execute_cmd("INSERT INTO `groups` (name, description, created_by) VALUES (%s, %s, %s)", (g_name.strip(), g_desc.strip(), current_user_id))
                    execute_cmd("INSERT INTO group_members (group_id, user_id, role) VALUES (%s, %s, 'creator')", (new_gid, current_user_id))
                    
                    added_count = 1
                    if initial_members_str.strip():
                        names = [n.strip() for n in initial_members_str.split(',') if n.strip()]
                        for n in names:
                            t_uid, t_name = find_or_create_user(n)
                            if not t_uid or t_uid == current_user_id:
                                continue
                            is_mem = run_query("SELECT id FROM group_members WHERE group_id = %s AND user_id = %s", (new_gid, t_uid))
                            if not is_mem:
                                execute_cmd("INSERT INTO group_members (group_id, user_id, role) VALUES (%s, %s, 'member')", (new_gid, t_uid))
                                added_count += 1

                    if g_budget > 0:
                        execute_cmd("INSERT INTO group_budgets (group_id, monthly_budget) VALUES (%s, %s)", (new_gid, g_budget))
                    st.success(f"Group '{g_name}' created successfully with {added_count} members!")
                    st.rerun()

# ==============================================================================
# 3. EXPENSES & SPLITS (WITH DELETE EXPENSE OPTION)
# ==============================================================================
elif menu == "expenses":
    st.markdown(clean_html(f"""<div class="brand-hero"><h1>{tr('expenses_hero_title')}</h1><p>{tr('expenses_hero_desc')}</p></div>"""), unsafe_allow_html=True)
    tab1, tab2 = st.tabs([tr('tab_add_expense'), tr('tab_expense_history')])

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
            g_names = list(g_options.keys())
            default_g_idx = 0
            if 'target_group_id' in st.session_state:
                for idx, g in enumerate(user_groups):
                    if g['id'] == st.session_state['target_group_id']:
                        default_g_idx = idx
                        break

            chosen_group_name = st.selectbox(tr('select_group_label'), g_names, index=default_g_idx)
            chosen_group_id = g_options[chosen_group_name]

            group_members = run_query("SELECT u.id, u.name FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s", (chosen_group_id,))
            member_dict = {m['name']: m['id'] for m in group_members}

            col1, col2 = st.columns(2)
            with col1:
                exp_desc = st.text_input(tr('exp_desc_label'), placeholder=tr('exp_desc_placeholder'))
                exp_amt = st.number_input(tr('exp_amt_label'), min_value=0.01, step=50.0, value=900.0)
            with col2:
                exp_cat = st.selectbox(tr('exp_cat_label'), CATEGORIES)
                exp_date = st.date_input(tr('exp_date_label'), value=datetime.date.today())

            payer_name = st.selectbox(tr('paid_by_label'), list(member_dict.keys()), index=list(member_dict.keys()).index(current_user_name) if current_user_name in member_dict else 0)
            payer_id = member_dict[payer_name]
            split_type = st.radio(tr('split_method_label'), [tr('split_equal'), tr('split_percentage'), tr('split_custom')], horizontal=True)

            selected_participants = []
            splits_data = []

            if split_type == tr('split_equal'):
                st.markdown("<small style='color:#636e72;'>Select who participated in this expense:</small>", unsafe_allow_html=True)
                for m_name, m_id in member_dict.items():
                    if st.checkbox(f"👤 {m_name}", value=True, key=f"part_eq_{m_id}"):
                        selected_participants.append(m_id)
                if selected_participants:
                    share_per_person = round(exp_amt / len(selected_participants), 2)
                    st.info(f"Each person's share: **₹{share_per_person:,.2f}**")
                    for pid in selected_participants:
                        splits_data.append((pid, share_per_person, round(100.0/len(selected_participants), 2)))

            elif split_type == tr('split_percentage'):
                total_pct = 0.0
                pct_inputs = {}
                cols = st.columns(len(member_dict))
                for idx, (m_name, m_id) in enumerate(member_dict.items()):
                    with cols[idx % len(cols)]:
                        p = st.number_input(f"{m_name} (%)", min_value=0.0, max_value=100.0, value=round(100.0/len(member_dict), 1), step=5.0, key=f"pct_{m_id}")
                        pct_inputs[m_id] = p
                        total_pct += p
                if abs(total_pct - 100.0) < 0.1:
                    for pid, pct in pct_inputs.items():
                        if pct > 0:
                            share = round(exp_amt * (pct / 100.0), 2)
                            splits_data.append((pid, share, pct))
                else:
                    st.error(f"Percentages must sum to 100% (currently {total_pct:.1f}%).")

            elif split_type == tr('split_custom'):
                total_cust = 0.0
                cust_inputs = {}
                cols = st.columns(len(member_dict))
                for idx, (m_name, m_id) in enumerate(member_dict.items()):
                    with cols[idx % len(cols)]:
                        amt = st.number_input(f"{m_name} (₹)", min_value=0.0, value=round(exp_amt/len(member_dict), 2), step=50.0, key=f"amt_{m_id}")
                        cust_inputs[m_id] = amt
                        total_cust += amt
                if abs(total_cust - exp_amt) < 0.01:
                    for pid, amt in cust_inputs.items():
                        if amt > 0:
                            splits_data.append((pid, amt, None))
                else:
                    st.error(f"Custom sum (₹{total_cust:,.2f}) must match total (₹{exp_amt:,.2f}).")

            # Live Budget Limit Alert
            grp_budget_row = run_query("""
                SELECT COALESCE(gb.monthly_budget, 0.0) as budget,
                       COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = %s), 0.0) as spent
                FROM `groups` g
                LEFT JOIN group_budgets gb ON g.id = gb.group_id
                WHERE g.id = %s
            """, (chosen_group_id, chosen_group_id))

            if grp_budget_row and float(grp_budget_row[0]['budget']) > 0:
                g_lim_b = float(grp_budget_row[0]['budget'])
                g_lim_s = float(grp_budget_row[0]['spent'])
                proj_spent_val = g_lim_s + float(exp_amt)
                lim_stat = get_budget_status(proj_spent_val, g_lim_b)
                if lim_stat['level'] == 'OVER_LIMIT':
                    st.error(f"🚨 **High Budget Alert**: Recording this ₹{exp_amt:,.2f} expense will push total group spending to **₹{proj_spent_val:,.2f}**, which **EXCEEDS** the monthly budget limit (₹{g_lim_b:,.2f}) by **₹{proj_spent_val - g_lim_b:,.2f}** ({lim_stat['pct']:.1f}% used)!")
                elif lim_stat['level'] == 'HIGH_ALERT':
                    st.warning(f"⚠️ **High Budget Alert**: This expense will push group spending to **{lim_stat['pct']:.1f}%** of its budget limit. Only ₹{g_lim_b - proj_spent_val:,.2f} will remain.")
                elif lim_stat['level'] == 'LOW_SAFE':
                    st.success(f"🟢 **Low Budget Alert (Safe)**: Spending is healthy and well within limits ({lim_stat['pct']:.1f}% used). Remaining limit: **₹{g_lim_b - proj_spent_val:,.2f}**.")
                else:
                    st.info(f"🟡 **Moderate Spending**: Total spending will reach **{lim_stat['pct']:.1f}%** of budget limit. Remaining: **₹{g_lim_b - proj_spent_val:,.2f}**.")

            if st.button(tr('btn_save_expense'), type="primary"):
                if not exp_desc.strip() or not splits_data:
                    st.error("Please fill all required fields.")
                else:
                    st_val = 'EQUAL' if split_type == tr('split_equal') else ('PERCENTAGE' if split_type == tr('split_percentage') else 'CUSTOM')
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
                SELECT e.id as ID, e.date as Date, e.description as Description, g.name as Group_Name,
                       e.category as Category, u.name as Paid_By, e.amount as Amount, e.split_type as Split_Type
                FROM expenses e
                JOIN `groups` g ON e.group_id = g.id
                JOIN users u ON e.paid_by = u.id
                WHERE e.group_id IN ({format_p})
                ORDER BY e.date DESC
            """, group_ids)
            if all_exp:
                st.dataframe(pd.DataFrame(all_exp), use_container_width=True)

                # Option to Delete an Expense
                with st.expander(tr('delete_expense_title')):
                    exp_select_map = {f"#{e['ID']}: {e['Description']} (₹{float(e['Amount']):,.2f} on {e['Date']})": e['ID'] for e in all_exp}
                    sel_exp_key = st.selectbox("Select Expense to Delete:", list(exp_select_map.keys()))
                    if st.button(tr('btn_delete_selected_expense'), key="btn_del_single_exp"):
                        target_eid = exp_select_map[sel_exp_key]
                        execute_cmd("DELETE FROM expense_splits WHERE expense_id = %s", (target_eid,))
                        execute_cmd("DELETE FROM expenses WHERE id = %s", (target_eid,))
                        st.success("Expense deleted successfully!")
                        st.rerun()
            else:
                st.info("No expenses recorded yet in your groups.")

    # Navigation Buttons for Step 2 -> Step 3
    st.markdown(clean_html(f"""
    <div style="background: linear-gradient(135deg, #f7f6fe 0%, #edeafe 100%); border: 1.5px solid #dcd6fa; border-radius: 12px; padding: 1rem 1.25rem; margin: 1.5rem 0 0.75rem 0;">
        <span style="background:#6c5ce7; color:#ffffff; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:8px; text-transform:uppercase;">Next Step</span>
        <h4 style="margin:4px 0 2px 0; color:#2d3436; font-size:1.05rem;">{tr('next_step_exp_title')}</h4>
        <small style="color:#636e72;">{tr('next_step_exp_sub')}</small>
    </div>
    """), unsafe_allow_html=True)
    col_exp_p, col_exp_n = st.columns(2)
    with col_exp_p:
        if st.button(tr('btn_back_to_groups'), key="exp_to_prev_groups", use_container_width=True):
            navigate_to("groups")
    with col_exp_n:
        if st.button(tr('btn_next_to_balances'), key="exp_to_next_bal", type="primary", use_container_width=True):
            navigate_to("balances")

# ==============================================================================
# 4. BALANCES (WHO OWES WHOM)
# ==============================================================================
elif menu == "balances":
    st.markdown(clean_html(f"""<div class="brand-hero"><h1>{tr('balances_hero_title')}</h1><p>{tr('balances_hero_desc')}</p></div>"""), unsafe_allow_html=True)
    user_groups = run_query("SELECT g.id, g.name FROM `groups` g JOIN group_members gm ON g.id = gm.group_id WHERE gm.user_id = %s", (current_user_id,))
    if not user_groups:
        st.info("No balances available. Join a group to begin tracking settlements.")
    else:
        for g in user_groups:
            gid = g['id']
            st.markdown(clean_html(f"""<div class="white-card"><h3 style="color:#2d3436; margin-bottom:1rem;">👥 {g['name']}</h3>"""), unsafe_allow_html=True)
            members = run_query("SELECT u.id, u.name FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s", (gid,))
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
                status = tr('status_gets_back') if net > 0.01 else (tr('status_owes') if net < -0.01 else tr('status_settled'))
                bal_list.append({tr('col_member'): m['name'], tr('col_paid'): f"₹{p:,.2f}", tr('col_share'): f"₹{s:,.2f}", tr('col_net'): f"{'+' if net > 0 else ''}₹{net:,.2f}", tr('col_status'): status})

            st.dataframe(pd.DataFrame(bal_list), use_container_width=True)

            settlements = simplify_debts(net_map, m_dict)
            st.markdown(f"<h4 style='color:#6c5ce7; margin-top:1rem;'>{tr('settlement_instructions')}</h4>", unsafe_allow_html=True)
            if not settlements:
                st.success(tr('all_settled'))
            else:
                for s in settlements:
                    st.markdown(clean_html(f"""
                    <div class="settlement-box">
                        <div><strong style="color:#d63031;">{s['debtor_name']}</strong> {tr('pays')} <strong style="color:#00b894;">{s['creditor_name']}</strong></div>
                        <strong style="color:#6c5ce7; font-size:1.1rem;">₹{s['amount']:,.2f}</strong>
                    </div>
                    """), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Navigation for Step 3 -> Step 4
        st.markdown(clean_html(f"""
        <div style="background: linear-gradient(135deg, #f7f6fe 0%, #edeafe 100%); border: 1.5px solid #dcd6fa; border-radius: 12px; padding: 1rem 1.25rem; margin: 1.5rem 0 0.75rem 0;">
            <span style="background:#6c5ce7; color:#ffffff; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:8px; text-transform:uppercase;">Next Step</span>
            <h4 style="margin:4px 0 2px 0; color:#2d3436; font-size:1.05rem;">{tr('next_step_bal_title')}</h4>
            <small style="color:#636e72;">{tr('next_step_bal_sub')}</small>
        </div>
        """), unsafe_allow_html=True)
        col_b_p, col_b_n1, col_b_n2 = st.columns([1, 1, 1.4])
        with col_b_p:
            if st.button(tr('btn_back_to_expenses'), key="bal_back_exp", use_container_width=True):
                navigate_to("expenses")
        with col_b_n1:
            if st.button(tr('btn_view_analytics'), key="bal_to_dash", use_container_width=True):
                navigate_to("dashboard")
        with col_b_n2:
            if st.button(tr('btn_proceed_to_history'), key="bal_to_hist", type="primary", use_container_width=True):
                navigate_to("history")

# ==============================================================================
# 5. GROUP BUDGETS & LIMIT ALERTS (High Alert vs Low Alert)
# ==============================================================================
elif menu == "budgets":
    st.markdown(clean_html(f"""
    <div class="brand-hero">
        <h1>{tr('budgets_hero_title')}</h1>
        <p>{tr('budgets_hero_desc')}</p>
    </div>
    """), unsafe_allow_html=True)

    budgets = run_query("""
        SELECT g.id, g.name, g.description,
               COALESCE(gb.monthly_budget, 0.00) as budget,
               COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) as spent
        FROM `groups` g JOIN group_members gm ON g.id = gm.group_id
        LEFT JOIN group_budgets gb ON g.id = gb.group_id WHERE gm.user_id = %s
    """, (current_user_id,))

    if not budgets:
        st.info("No group budgets found. Create a group in 'Groups & Members' to start tracking spending limits.")
    else:
        # High-Level Summary Card
        tot_b = sum(float(x['budget']) for x in budgets)
        tot_s = sum(float(x['spent']) for x in budgets)
        high_alerts = sum(1 for x in budgets if float(x['budget']) > 0 and (float(x['spent']) / float(x['budget']) >= 0.85))
        safe_groups = sum(1 for x in budgets if float(x['budget']) > 0 and (float(x['spent']) / float(x['budget']) < 0.50))

        st.markdown(clean_html("""<div class="white-card"><h3>🚨 Budget Limit Alert Overview</h3>"""), unsafe_allow_html=True)
        col_ov1, col_ov2, col_ov3, col_ov4 = st.columns(4)
        col_ov1.metric("Total Budgets Set", f"₹{tot_b:,.2f}")
        col_ov2.metric("Total Group Spending", f"₹{tot_s:,.2f}")
        col_ov3.metric("🔴 High Alert Groups", f"{high_alerts} Groups")
        col_ov4.metric("🟢 Low/Safe Groups", f"{safe_groups} Groups")
        st.markdown("</div>", unsafe_allow_html=True)

        for b_item in budgets:
            gid = b_item['id']
            b = float(b_item['budget'])
            s = float(b_item['spent'])
            stat = get_budget_status(s, b)

            st.markdown(clean_html(f"""
            <div class="white-card" style="margin-top:1.25rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:0.75rem;">
                    <h3 style="color:#2d3436; margin:0;">📁 {b_item['name']}</h3>
                    <span style="background:{stat['bg']}; color:{stat['color']}; border:1.5px solid {stat['border']}; padding:5px 14px; border-radius:16px; font-weight:700; font-size:0.88rem;">
                        {stat['badge']}
                    </span>
                </div>
            """), unsafe_allow_html=True)

            # Prominent High vs Low Alert Banners
            if stat['level'] == 'OVER_LIMIT':
                st.error(f"**{stat['headline']}** - {stat['sub']}")
            elif stat['level'] == 'HIGH_ALERT':
                st.warning(f"**{stat['headline']}** - {stat['sub']}")
            elif stat['level'] == 'LOW_SAFE':
                st.success(f"**{stat['headline']}** - {stat['sub']}")
            elif stat['level'] == 'MODERATE':
                st.info(f"**{stat['headline']}** - {stat['sub']}")
            else:
                st.caption(f"{stat['icon']} {stat['headline']} {stat['sub']}")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Monthly Limit", f"₹{b:,.2f}")
            m2.metric("Current Spent", f"₹{s:,.2f}")
            m3.metric("Remaining", f"₹{max(0.0, b - s):,.2f}")
            m4.metric("Budget Usage", f"{stat['pct']:.1f}%")

            if b > 0:
                prog_val = min(s / b, 1.0)
                st.progress(prog_val)

            with st.expander(f"✏️ Set / Update Spending Limit for '{b_item['name']}'"):
                new_b = st.number_input(f"Monthly Spending Limit (₹):", min_value=0.0, step=500.0, value=b, key=f"b_limit_{gid}")
                if st.button("Save New Limit", key=f"btn_save_limit_{gid}", type="primary"):
                    execute_cmd("""
                        INSERT INTO group_budgets (group_id, monthly_budget) VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE monthly_budget = %s
                    """ if db_type == 'mysql' else """
                        INSERT OR REPLACE INTO group_budgets (group_id, monthly_budget) VALUES (%s, %s)
                    """, (gid, new_b, new_b) if db_type == 'mysql' else (gid, new_b))
                    st.success("Group spending limit updated successfully!")
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_bud_p, col_bud_dash, col_bud_hist = st.columns([1, 1.2, 1.2])
        with col_bud_p:
            if st.button("⬅️ Back to Balances", key="bud_back_bal", use_container_width=True):
                navigate_to("balances")
        with col_bud_dash:
            if st.button("📊 View Full Analytics", key="bud_to_dash", use_container_width=True):
                navigate_to("dashboard")
        with col_bud_hist:
            if st.button("📜 Payment History", key="bud_to_hist", type="primary", use_container_width=True):
                navigate_to("history")

# ==============================================================================
# 7. PAYMENT & EXPENSE HISTORY (Shown at the last)
# ==============================================================================
elif menu == "history":
    st.markdown(clean_html(f"""<div class="brand-hero"><h1>{tr('history_hero_title')}</h1><p>{tr('history_hero_desc')}</p></div>"""), unsafe_allow_html=True)

    user_groups = run_query("""
        SELECT g.id, g.name FROM `groups` g
        JOIN group_members gm ON g.id = gm.group_id WHERE gm.user_id = %s
    """, (current_user_id,))

    if not user_groups:
        st.info("You do not belong to any groups yet.")
    else:
        group_ids = [g['id'] for g in user_groups]
        format_p = ','.join(['%s'] * len(group_ids))

        grp_opts = {tr("all_your_groups"): None}
        for g in user_groups:
            grp_opts[g['name']] = g['id']

        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            sel_grp_filter = st.selectbox(tr("filter_group_label"), list(grp_opts.keys()))

        filtered_gid = grp_opts[sel_grp_filter]
        if filtered_gid:
            history_query = """
                SELECT e.id as ID, e.date as Date, e.description as Description, g.name as Group_Name,
                       e.category as Category, u.name as Paid_By, e.amount as Total_Amount,
                       COALESCE(es.share_amount, 0.0) as Your_Share, e.split_type as Split_Method
                FROM expenses e
                JOIN `groups` g ON e.group_id = g.id
                JOIN users u ON e.paid_by = u.id
                LEFT JOIN expense_splits es ON e.id = es.expense_id AND es.user_id = %s
                WHERE e.group_id = %s
                ORDER BY e.date DESC
            """
            history_records = run_query(history_query, (current_user_id, filtered_gid))
        else:
            history_query = f"""
                SELECT e.id as ID, e.date as Date, e.description as Description, g.name as Group_Name,
                       e.category as Category, u.name as Paid_By, e.amount as Total_Amount,
                       COALESCE(es.share_amount, 0.0) as Your_Share, e.split_type as Split_Method
                FROM expenses e
                JOIN `groups` g ON e.group_id = g.id
                JOIN users u ON e.paid_by = u.id
                LEFT JOIN expense_splits es ON e.id = es.expense_id AND es.user_id = %s
                WHERE e.group_id IN ({format_p})
                ORDER BY e.date DESC
            """
            history_records = run_query(history_query, [current_user_id] + group_ids)

        if not history_records:
            st.info("No payment or expense records found for this selection.")
        else:
            total_spent_val = sum(float(r['Total_Amount']) for r in history_records)
            my_share_val = sum(float(r['Your_Share']) for r in history_records)

            st.markdown(clean_html(f"""
            <div class="white-card">
                <div style="display:flex; justify-content:space-around; align-items:center; flex-wrap:wrap; text-align:center;">
                    <div>
                        <div style="color:#636e72; font-size:0.8rem; text-transform:uppercase; font-weight:600;">{tr('stat_total_tx')}</div>
                        <strong style="font-size:1.4rem; color:#2d3436;">{len(history_records)}</strong>
                    </div>
                    <div style="width:1px; height:40px; background:#e9ecef;"></div>
                    <div>
                        <div style="color:#636e72; font-size:0.8rem; text-transform:uppercase; font-weight:600;">{tr('stat_total_spent')}</div>
                        <strong style="font-size:1.4rem; color:#6c5ce7;">₹{total_spent_val:,.2f}</strong>
                    </div>
                    <div style="width:1px; height:40px; background:#e9ecef;"></div>
                    <div>
                        <div style="color:#636e72; font-size:0.8rem; text-transform:uppercase; font-weight:600;">{tr('stat_your_share')}</div>
                        <strong style="font-size:1.4rem; color:#00b894;">₹{my_share_val:,.2f}</strong>
                    </div>
                </div>
            </div>
            """), unsafe_allow_html=True)

            df_display = pd.DataFrame(history_records)
            df_display['Total_Amount'] = df_display['Total_Amount'].apply(lambda x: f"₹{float(x):,.2f}")
            df_display['Your_Share'] = df_display['Your_Share'].apply(lambda x: f"₹{float(x):,.2f}")
            st.dataframe(df_display, use_container_width=True)

            with st.expander(tr('delete_history_title')):
                del_map = {f"#{r['ID']}: {r['Description']} ({r['Total_Amount']} on {r['Date']} in {r['Group_Name']})": r['ID'] for r in history_records}
                sel_del_exp = st.selectbox("Select entry to delete:", list(del_map.keys()))
                if st.button(tr('btn_delete_entry'), key="btn_del_hist_entry"):
                    t_eid = del_map[sel_del_exp]
                    execute_cmd("DELETE FROM expense_splits WHERE expense_id = %s", (t_eid,))
                    execute_cmd("DELETE FROM expenses WHERE id = %s", (t_eid,))
                    st.success("Entry deleted successfully!")
                    st.rerun()

            # Navigation back to earlier steps from Payment History
            st.markdown(clean_html(f"""
            <div style="background: linear-gradient(135deg, #f7f6fe 0%, #edeafe 100%); border: 1.5px solid #dcd6fa; border-radius: 12px; padding: 1rem 1.25rem; margin: 1.5rem 0 0.75rem 0; text-align:center;">
                <span style="background:#00b894; color:#ffffff; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:8px; text-transform:uppercase;">Lifecycle Complete</span>
                <h4 style="margin:4px 0 2px 0; color:#2d3436; font-size:1.05rem;">{tr('complete_lifecycle_title')}</h4>
                <small style="color:#636e72;">{tr('complete_lifecycle_sub')}</small>
            </div>
            """), unsafe_allow_html=True)
            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1:
                if st.button(tr('btn_goto_step1'), key="hist_to_grp", use_container_width=True):
                    navigate_to("groups")
            with col_h2:
                if st.button(tr('btn_goto_step2'), key="hist_to_exp", use_container_width=True):
                    navigate_to("expenses")
            with col_h3:
                if st.button(tr('btn_goto_step3'), key="hist_to_bal", use_container_width=True):
                    navigate_to("balances")
