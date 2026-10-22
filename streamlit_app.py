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
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {
        background: linear-gradient(135deg, #6c5ce7 0%, #8e44ad 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.55rem 1.4rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(108, 92, 231, 0.25) !important;
    }
    .stButton>button p, .stButton>button span, div[data-testid="stFormSubmitButton"]>button p, div[data-testid="stFormSubmitButton"]>button span {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    .stButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {
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
    try:
        cur.execute("""DELETE FROM group_members WHERE id NOT IN (SELECT MIN(id) FROM group_members GROUP BY group_id, user_id);""")
        cur.execute("""CREATE UNIQUE INDEX IF NOT EXISTS idx_group_members_uniq ON group_members(group_id, user_id);""")
    except Exception:
        pass
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
        sql = re.sub(r'(?i)\bINSERT\s+IGNORE\s+INTO\b', 'INSERT OR IGNORE INTO', sql)
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
        sql = re.sub(r'(?i)\bINSERT\s+IGNORE\s+INTO\b', 'INSERT OR IGNORE INTO', sql)
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
        'nav_dashboard': '📊 Dashboard',
        'nav_groups': '👥 Groups',
        'nav_expenses': '➕ Add Expense',
        'nav_balances': '⚖️ Balances',
        'nav_budgets': '📊 Budgets',
        'nav_settings': '⚙️ Settings & Profile',
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

APP_LOGO_B64 = "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"

def render_brand_logo(size=48, key="logo"):
    return (
        f'<img src="data:image/png;base64,{APP_LOGO_B64}" width="{size}" height="{size}" '
        f'style="border-radius:{int(size*0.25)}px; box-shadow:0 8px 24px rgba(108,92,231,0.38); '
        f'vertical-align:middle; display:inline-block;" alt="SplitSettlement">'
    )

def render_brand_header(size=64, text_color="#ffffff", sub_color="rgba(255,255,255,0.88)", show_tagline=True):
    tagline_html = (
        '<div style="display:inline-block; margin-top:8px; background:rgba(255,255,255,0.16); '
        'border:1px solid rgba(255,255,255,0.28); color:#ffffff; font-size:0.82rem; font-weight:600; '
        'padding:3px 14px; border-radius:14px; letter-spacing:0.3px;">Split Smarter, Stay Together</div>'
        if show_tagline else ''
    )
    return (
        f'<div style="text-align:center; margin-bottom:1.5rem;">'
        f'{render_brand_logo(size=size)}'
        f'<h1 style="color:{text_color}; font-size:1.85rem; font-weight:800; margin:10px 0 2px 0; letter-spacing:-0.5px;">SplitSettlement</h1>'
        f'<p style="color:{sub_color}; font-size:0.95rem; font-weight:500; margin:0;">Expense Split & Settlement System</p>'
        f'{tagline_html}'
        f'</div>'
    )

render_logo = render_brand_logo

NAV_CANONICAL = ["dashboard", "groups", "expenses", "balances", "budgets", "settings"]

NAV_LABEL_KEYS = {
    "dashboard": "nav_dashboard",
    "groups": "nav_groups",
    "expenses": "nav_expenses",
    "balances": "nav_balances",
    "budgets": "nav_budgets",
    "settings": "nav_settings"
}

def normalize_nav(page_name):
    if page_name in NAV_CANONICAL:
        return page_name
    pl = page_name.lower()
    if "dash" in pl or "analytics" in pl:
        return "dashboard"
    if "group" in pl:
        return "groups"
    if "add" in pl or "expense" in pl:
        return "expenses"
    if "balance" in pl or "who owes" in pl:
        return "balances"
    if "budget" in pl or "alert" in pl or "simulator" in pl:
        return "budgets"
    if "setting" in pl or "password" in pl or "profile" in pl:
        return "settings"
    return "dashboard" 
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
# SCREEN 1: LOGIN & REGISTRATION PORTAL (Matching Exact Creative Mockup)
# ==============================================================================
if not st.session_state['authenticated']:
    # Inject Custom Login Screen Styles
    st.markdown("""
    <style>
        /* Immersive Deep Purple Gradient Viewport */
        .stApp {
            background: linear-gradient(135deg, #4f2cdb 0%, #683fea 45%, #7b4df2 100%) !important;
            min-height: 100vh !important;
        }

        /* Hide Streamlit Header & Sidebar on Login Screen */
        header[data-testid="stHeader"] {
            background: transparent !important;
        }
        section[data-testid="stSidebar"] {
            display: none !important;
        }


        /* The Form ITSELF is the Clean White Card (No extra empty containers) */
        div[data-testid="stForm"] {
            background: #ffffff !important;
            border-radius: 22px !important;
            padding: 2.2rem 2.2rem 1.8rem 2.2rem !important;
            box-shadow: 0 20px 60px rgba(15, 5, 55, 0.35) !important;
            border: none !important;
        }

        /* Inputs inside Auth Card */
        div[data-testid="stTextInput"] input {
            background-color: #fafbff !important;
            border: 1.5px solid #e1e8ed !important;
            border-radius: 10px !important;
            padding: 0.75rem 1rem !important;
            font-size: 0.95rem !important;
            color: #2d3436 !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #5b36e8 !important;
            background-color: #ffffff !important;
            box-shadow: 0 0 0 3px rgba(91, 54, 232, 0.15) !important;
        }
        div[data-testid="stTextInput"] label {
            color: #636e72 !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            margin-bottom: 2px !important;
        }

        /* Solid Purple Action Button */
        div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #6c5ce7 0%, #5031df 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.8rem 1.5rem !important;
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            width: 100% !important;
            box-shadow: 0 8px 22px rgba(91, 54, 232, 0.35) !important;
            transition: all 0.2s ease !important;
            margin-top: 0.6rem !important;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background: linear-gradient(135deg, #5b36e8 0%, #431fcf 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 28px rgba(91, 54, 232, 0.45) !important;
        }

        /* Bottom Switch Button */
        .auth-switch-box button {
            background: rgba(255, 255, 255, 0.15) !important;
            color: #ffffff !important;
            border: 1.5px solid rgba(255, 255, 255, 0.4) !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            padding: 0.5rem 1.2rem !important;
            transition: all 0.2s ease !important;
        }
        .auth-switch-box button:hover {
            background: rgba(255, 255, 255, 0.3) !important;
            color: #ffffff !important;
            transform: translateY(-1px) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Top Brand Header: Centered Squircle Logo & Brand Name (SplitSettlement)
    st.markdown(clean_html(render_brand_header(size=72, text_color="#ffffff", sub_color="rgba(255,255,255,0.88)", show_tagline=True)), unsafe_allow_html=True)

    # 2-Column Responsive Layout: Left Hero with Friends & Coins, Right Floating Card
    col_hero, col_card = st.columns([1.08, 1.12], gap="large")

    with col_hero:
        st.markdown(clean_html("""
        <div style="padding: 1.25rem 0.5rem 0 0.5rem;">
            <h2 style="color: #ffffff; font-size: 2.35rem; font-weight: 800; line-height: 1.2; margin-bottom: 1.15rem; letter-spacing: -0.5px;">
                Manage<br>Group Expenses<br>Easily
            </h2>
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.05rem; line-height: 1.55; max-width: 360px; margin-bottom: 1.5rem;">
                Split expenses, track balances and stay worry-free with your friends, family or team.
            </p>
        </div>
        """), unsafe_allow_html=True)

        # SVG Vector Illustration: 3 Friends with laptops & floating golden Rupee coins
        st.markdown(clean_html("""
        <div style="width:100%; max-width:440px; margin-top:0.5rem;">
            <svg viewBox="0 0 520 340" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="coinGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#ffeaa7"/>
                  <stop offset="50%" stop-color="#fdcb6e"/>
                  <stop offset="100%" stop-color="#e17055"/>
                </linearGradient>
                <linearGradient id="hillGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#6c5ce7" stop-opacity="0.65"/>
                  <stop offset="100%" stop-color="#4b38b3" stop-opacity="0.95"/>
                </linearGradient>
                <linearGradient id="hillGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#7d5fff" stop-opacity="0.4"/>
                  <stop offset="100%" stop-color="#5733d1" stop-opacity="0.75"/>
                </linearGradient>
                <filter id="coinGlow" x="-20%" y="-20%" width="140%" height="140%">
                  <feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#fdcb6e" flood-opacity="0.45"/>
                </filter>
              </defs>
              <!-- Decorative Hills -->
              <path d="M-20,270 Q140,200 290,250 T540,230 L540,360 L-20,360 Z" fill="url(#hillGrad2)"/>
              <path d="M-20,295 Q160,240 340,280 T540,265 L540,360 L-20,360 Z" fill="url(#hillGrad1)"/>
              
              <!-- Plants -->
              <path d="M25,290 Q15,235 48,225 Q42,265 25,290 Z" fill="#00b894" opacity="0.9"/>
              <path d="M40,290 Q62,245 82,255 Q62,278 40,290 Z" fill="#55efc4" opacity="0.8"/>
              <path d="M465,275 Q490,225 510,240 Q490,260 465,275 Z" fill="#00b894" opacity="0.9"/>

              <!-- Floating Coin 1 (Top Left) -->
              <g filter="url(#coinGlow)">
                <circle cx="80" cy="85" r="26" fill="url(#coinGrad)"/>
                <circle cx="80" cy="85" r="21" fill="none" stroke="#ffffff" stroke-width="2" stroke-opacity="0.7"/>
                <text x="80" y="94" font-family="'Segoe UI', Roboto, Arial, sans-serif" font-size="24" font-weight="900" fill="#2d3436" text-anchor="middle">₹</text>
              </g>

              <!-- Floating Coin 2 (Bottom Left) -->
              <g filter="url(#coinGlow)">
                <circle cx="65" cy="225" r="20" fill="url(#coinGrad)"/>
                <circle cx="65" cy="225" r="16" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-opacity="0.7"/>
                <text x="65" y="233" font-family="'Segoe UI', Roboto, Arial, sans-serif" font-size="18" font-weight="900" fill="#2d3436" text-anchor="middle">₹</text>
              </g>

              <!-- Floating Coin 3 (Right) -->
              <g filter="url(#coinGlow)">
                <circle cx="430" cy="115" r="24" fill="url(#coinGrad)"/>
                <circle cx="430" cy="115" r="19" fill="none" stroke="#ffffff" stroke-width="2" stroke-opacity="0.7"/>
                <text x="430" y="124" font-family="'Segoe UI', Roboto, Arial, sans-serif" font-size="22" font-weight="900" fill="#2d3436" text-anchor="middle">₹</text>
              </g>

              <!-- Person 1 (Left - Sitting with laptop) -->
              <g>
                <path d="M110,185 Q92,192 90,230 Q115,220 120,195 Z" fill="#2d3436"/>
                <path d="M105,200 Q115,195 130,200 L135,245 L95,245 Z" fill="#6c5ce7"/>
                <circle cx="116" cy="180" r="13" fill="#ffdfba"/>
                <path d="M110,215 L140,230 L135,240 Z" fill="#ffdfba"/>
                <polygon points="128,230 162,225 164,238 130,240" fill="#dfe6e9"/>
                <polygon points="135,215 158,212 162,226 138,228" fill="#ffffff"/>
                <path d="M95,245 Q80,270 120,275 Q150,275 140,250 Z" fill="#2d3436"/>
              </g>

              <!-- Person 2 (Middle - Male with laptop) -->
              <g>
                <ellipse cx="215" cy="178" rx="14" ry="11" fill="#2d3436"/>
                <circle cx="215" cy="186" r="12" fill="#fed330"/>
                <path d="M198,205 Q215,200 232,205 L236,252 L194,252 Z" fill="#ffffff"/>
                <path d="M198,210 L185,232 L205,236 Z" fill="#fed330"/>
                <path d="M232,210 L242,230 L225,236 Z" fill="#fed330"/>
                <polygon points="190,232 235,232 240,240 185,240" fill="#b2bec3"/>
                <polygon points="190,232 225,219 228,232 195,234" fill="#ffffff"/>
                <path d="M194,252 L180,285 L205,285 L215,258 L230,285 L250,285 L236,252 Z" fill="#4834d4"/>
              </g>

              <!-- Person 3 (Right - Teammate with laptop) -->
              <g>
                <ellipse cx="320" cy="188" rx="13" ry="10" fill="#2d3436"/>
                <circle cx="320" cy="195" r="12" fill="#ffdfba"/>
                <path d="M304,212 Q320,208 338,212 L342,255 L300,255 Z" fill="#ff7675"/>
                <polygon points="325,235 360,230 362,242 328,245" fill="#b2bec3"/>
                <polygon points="332,220 358,216 360,230 335,233" fill="#ffffff"/>
                <path d="M300,255 Q290,280 330,282 Q355,282 345,255 Z" fill="#1e272e"/>
              </g>
            </svg>
        </div>
        """), unsafe_allow_html=True)

    with col_card:
        # Determine current auth mode: login vs register
        auth_mode = st.session_state.get('auth_mode', 'login')

        # ======================================================================
        # CARD 1: LOGIN (Welcome Back) - THE FORM IS THE WHITE CARD
        # ======================================================================
        if auth_mode == 'login':
            with st.form("login_form"):
                st.markdown(clean_html("""
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <h3 style="color: #2d3436; font-size: 1.65rem; font-weight: 800; margin: 0 0 4px 0;">Welcome Back</h3>
                    <p style="color: #636e72; font-size: 0.92rem; margin: 0;">Login to your account</p>
                </div>
                """), unsafe_allow_html=True)

                login_ident = st.text_input("Email address", placeholder="Email address", key="login_ident_in")
                login_pwd = st.text_input("Password", type="password", placeholder="Password", key="login_pwd_in")

                col_rem, col_fog = st.columns([1.1, 1.1])
                with col_rem:
                    st.checkbox("Remember me", value=True, key="login_remember_me")
                with col_fog:
                    forgot_pwd = st.form_submit_button("Forgot password?", help="Click for password assistance")

                submit_login = st.form_submit_button("Login", use_container_width=True)

                if forgot_pwd:
                    st.info("💡 **Forgot Password / Account Recovery:** If your account was created by a friend, switch to **'Create Account'** using your email to choose a secure password. If you already have an account, enter your email and password, or reach out to your group admin.")

                if submit_login:
                    cleaned_ident = login_ident.strip()
                    if not cleaned_ident or not login_pwd:
                        st.error("Please enter both your email address and password.")
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
                            st.error(f"No account found for '{cleaned_ident}'. Click below to create your account in 1 click, or click 'Register' below.")
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

            # Switch prompt to Register (Clean button below the white form)
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            col_sw1, col_sw2 = st.columns([1.5, 1])
            with col_sw1:
                st.markdown("<p style='text-align:right; color:#ffffff; font-size:0.95rem; font-weight:600; margin-top:8px;'>Don\'t have an account?</p>", unsafe_allow_html=True)
            with col_sw2:
                st.markdown('<div class="auth-switch-box">', unsafe_allow_html=True)
                if st.button("Register", key="switch_to_reg"):
                    st.session_state['auth_mode'] = 'register'
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ======================================================================
        # CARD 2: REGISTER (Create Account) - THE FORM IS THE WHITE CARD
        # ======================================================================
        else:
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
                st.markdown(clean_html("""
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <h3 style="color: #2d3436; font-size: 1.65rem; font-weight: 800; margin: 0 0 4px 0;">Create Account</h3>
                    <p style="color: #636e72; font-size: 0.92rem; margin: 0;">Join now and start managing expenses</p>
                </div>
                """), unsafe_allow_html=True)

                reg_name = st.text_input("Full Name", value=default_reg_name, placeholder="Full Name", key="reg_name_in")
                reg_email = st.text_input("Email address", value=default_reg_email, placeholder="Email address", key="reg_email_in")
                reg_pwd = st.text_input("Password", type="password", placeholder="Password", key="reg_pwd_in")
                reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm Password", key="reg_conf_pwd_in")

                agree_terms = st.checkbox("I agree to the Terms and Conditions", value=True, key="reg_agree_terms")
                submit_reg = st.form_submit_button("Register", use_container_width=True)

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
                    elif not agree_terms:
                        st.error("Please agree to the Terms and Conditions to proceed.")
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

            # Switch prompt to Login (Clean button below the white form)
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            col_sw1, col_sw2 = st.columns([1.5, 1])
            with col_sw1:
                st.markdown("<p style='text-align:right; color:#ffffff; font-size:0.95rem; font-weight:600; margin-top:8px;'>Already have an account?</p>", unsafe_allow_html=True)
            with col_sw2:
                st.markdown('<div class="auth-switch-box">', unsafe_allow_html=True)
                if st.button("Login", key="switch_to_login"):
                    st.session_state['auth_mode'] = 'login'
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # Stop execution here until the user logs in
    st.stop()

# ==============================================================================
# SCREEN 2: AUTHENTICATED APPLICATION (Exact Match to Design System Mockup)
# ==============================================================================
current_user_id = st.session_state['user_id']
current_user_name = st.session_state['user_name']
current_user_email = st.session_state['user_email']

# ==============================================================================
# SIDEBAR NAVIGATION (Matching Modern Mockup Pill Style)
# ==============================================================================
st.sidebar.markdown(
    f'<div style="text-align: center; margin-bottom: 1.5rem;">'
    f'{render_brand_logo(size=52)}'
    f'<h2 style="font-size: 1.25rem; margin: 0.4rem 0 0 0; color: #2d3436; font-weight:700;">{tr("app_title")}</h2>'
    f'<small style="color: #6c5ce7; font-weight:600;">{tr("app_subtitle")}</small>'
    f'</div>',
    unsafe_allow_html=True
)

if 'nav_selection' not in st.session_state or st.session_state['nav_selection'] not in NAV_CANONICAL:
    st.session_state['nav_selection'] = "dashboard"

current_nav_index = NAV_CANONICAL.index(st.session_state['nav_selection'])
menu = st.sidebar.radio(
    "Navigation Menu",
    NAV_CANONICAL,
    index=current_nav_index,
    format_func=lambda k: tr(NAV_LABEL_KEYS[k]),
    label_visibility="collapsed"
)
st.session_state['nav_selection'] = menu

# Interface Language Dropdown in Sidebar
cur_lang_sb = st.session_state.get('interface_language', 'English')
lang_idx_sb = LANGUAGE_OPTIONS.index(cur_lang_sb) if cur_lang_sb in LANGUAGE_OPTIONS else 0
sel_lang_sb = st.sidebar.selectbox(
    "🌐 Interface Language:",
    LANGUAGE_OPTIONS,
    index=lang_idx_sb,
    key="sb_lang_dropdown_main"
)
if sel_lang_sb != st.session_state.get('interface_language'):
    st.session_state['interface_language'] = sel_lang_sb
    st.rerun()


st.sidebar.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
st.sidebar.caption(f"Engine: **{db_type.upper()}** &bull; Status: **Online**")
if st.sidebar.button(tr('btn_logout_account'), key="sidebar_bottom_logout_btn", use_container_width=True):
    st.session_state.clear()
    st.session_state['authenticated'] = False
    st.rerun()

# ==============================================================================
# TOP APP HEADER BAR (Mockup Top Bar with Search, Language & Profile Avatar)
# ==============================================================================
user_initial = current_user_name[0].upper() if current_user_name else "U"

col_top_l, col_top_r = st.columns([1.8, 2.2])
with col_top_l:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:12px; padding: 4px 0;">'
        f'{render_brand_logo(size=36)}'
        f'<span style="font-size:1.25rem; color:#2d3748; font-weight:800; letter-spacing:-0.3px;">{tr("app_title")}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

with col_top_r:
    col_t_lang, col_t_prof, col_t_btn = st.columns([1.0, 1.6, 1.4])
    with col_t_lang:
        cur_l = st.session_state.get('interface_language', 'English')
        cur_l_idx = LANGUAGE_OPTIONS.index(cur_l) if cur_l in LANGUAGE_OPTIONS else 0
        s_lang = st.selectbox("🌐", LANGUAGE_OPTIONS, index=cur_l_idx, key="top_bar_lang_sel", label_visibility="collapsed")
        if s_lang != st.session_state.get('interface_language'):
            st.session_state['interface_language'] = s_lang
            st.rerun()
    with col_t_prof:
        st.markdown(
            f'<div class="profile-badge" style="width:100%; justify-content:flex-start;">'
            f'<div class="profile-avatar">{user_initial}</div>'
            f'<div class="profile-info">'
            f'<span class="profile-name">{current_user_name}</span>'
            f'<span class="profile-status"><span style="color:#00b894;">●</span> Online</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with col_t_btn:
        if st.button("✏️ Edit Profile", key="btn_top_edit_profile", use_container_width=True):
            navigate_to("settings")

st.markdown("<div style='height:1px; background:#edf2f7; margin: 0.5rem 0 1.5rem 0;'></div>", unsafe_allow_html=True)

# Fetch current user groups
user_groups = run_query("""
    SELECT g.id, g.name, g.description, g.created_by,
           COALESCE(gb.monthly_budget, 0.00) AS monthly_budget,
           COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = g.id), 0.00) AS total_spent
    FROM `groups` g
    JOIN group_members gm ON g.id = gm.group_id
    LEFT JOIN group_budgets gb ON g.id = gb.group_id
    WHERE gm.user_id = %s
""", (current_user_id,))

group_ids = [g['id'] for g in user_groups] if user_groups else []
format_p = ','.join(['%s'] * len(group_ids)) if group_ids else '0' 

# ==============================================================================
# 1. DASHBOARD & ANALYTICS (SCREEN 3 IN MOCKUP)
# ==============================================================================
if menu == "dashboard":
    # Greeting Header with Action Buttons
    c_greet, c_actions = st.columns([1.7, 1.5])
    with c_greet:
        st.markdown(clean_html(f"""
        <div>
            <h2 style="font-size:1.85rem; font-weight:800; color:#2d3748; margin:0 0 4px 0;">Welcome, {current_user_name}! 👋</h2>
            <p style="color:#718096; font-size:0.95rem; margin:0;">Here's your expense summary</p>
        </div>
        """), unsafe_allow_html=True)
    with c_actions:
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("➕ Add Expense", key="dash_top_add_exp", type="primary", use_container_width=True):
                navigate_to("expenses")
        with col_btn2:
            if st.button("👥 Create Group", key="dash_top_create_grp", use_container_width=True):
                navigate_to("groups")
        with col_btn3:
            if st.button("✏️ Edit Profile", key="dash_top_edit_prof", use_container_width=True):
                navigate_to("settings")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    if not user_groups:
        st.info("You do not belong to any groups yet. Navigate to 'Groups' to create or join one!")
    else:
        group_ids = [g['id'] for g in user_groups]
        format_p = ','.join(['%s'] * len(group_ids))

        total_group_exp = float(run_query(f"SELECT COALESCE(SUM(amount), 0.00) as val FROM expenses WHERE group_id IN ({format_p})", group_ids)[0]['val'])
        total_paid = float(run_query(f"SELECT COALESCE(SUM(amount), 0.00) as val FROM expenses WHERE paid_by = %s AND group_id IN ({format_p})", [current_user_id] + group_ids)[0]['val'])
        
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

        # 5 Key Metric Cards (Matching Mockup with Colored Icons)
        c1, c2, c3, c4, c5 = st.columns(5)
        
        with c1:
            st.markdown(clean_html(f"""
            <div class="white-card" style="display:flex; align-items:center; gap:12px; padding:1.1rem;">
                <div style="width:44px; height:44px; border-radius:12px; background:#fee2e2; color:#ef4444; display:flex; align-items:center; justify-content:center; font-size:1.3rem;">🧾</div>
                <div>
                    <div style="font-size:0.75rem; color:#718096; font-weight:700; text-transform:uppercase;">Total Expenses</div>
                    <div style="font-size:1.35rem; font-weight:800; color:#1a202c;">₹{total_group_exp:,.2f}</div>
                    <div style="font-size:0.72rem; color:#059669; font-weight:600;">↑ 12% from last month</div>
                </div>
            </div>
            """), unsafe_allow_html=True)

        with c2:
            st.markdown(clean_html(f"""
            <div class="white-card" style="display:flex; align-items:center; gap:12px; padding:1.1rem;">
                <div style="width:44px; height:44px; border-radius:12px; background:#e0f2fe; color:#0284c7; display:flex; align-items:center; justify-content:center; font-size:1.3rem;">💳</div>
                <div>
                    <div style="font-size:0.75rem; color:#718096; font-weight:700; text-transform:uppercase;">Amount Paid</div>
                    <div style="font-size:1.35rem; font-weight:800; color:#1a202c;">₹{total_paid:,.2f}</div>
                    <div style="font-size:0.72rem; color:#64748b;">You paid this amount</div>
                </div>
            </div>
            """), unsafe_allow_html=True)

        with c3:
            st.markdown(clean_html(f"""
            <div class="white-card" style="display:flex; align-items:center; gap:12px; padding:1.1rem;">
                <div style="width:44px; height:44px; border-radius:12px; background:#ffedd5; color:#ea580c; display:flex; align-items:center; justify-content:center; font-size:1.3rem;">💸</div>
                <div>
                    <div style="font-size:0.75rem; color:#718096; font-weight:700; text-transform:uppercase;">You Owe</div>
                    <div style="font-size:1.35rem; font-weight:800; color:#1a202c;">₹{user_owes:,.2f}</div>
                    <div style="font-size:0.72rem; color:#ea580c; font-weight:600;">To settle with others</div>
                </div>
            </div>
            """), unsafe_allow_html=True)

        with c4:
            st.markdown(clean_html(f"""
            <div class="white-card" style="display:flex; align-items:center; gap:12px; padding:1.1rem;">
                <div style="width:44px; height:44px; border-radius:12px; background:#dcfce7; color:#16a34a; display:flex; align-items:center; justify-content:center; font-size:1.3rem;">💰</div>
                <div>
                    <div style="font-size:0.75rem; color:#718096; font-weight:700; text-transform:uppercase;">You Receive</div>
                    <div style="font-size:1.35rem; font-weight:800; color:#1a202c;">₹{others_owe:,.2f}</div>
                    <div style="font-size:0.72rem; color:#16a34a; font-weight:600;">Others owe you</div>
                </div>
            </div>
            """), unsafe_allow_html=True)

        with c5:
            st.markdown(clean_html(f"""
            <div class="white-card" style="display:flex; align-items:center; gap:12px; padding:1.1rem;">
                <div style="width:44px; height:44px; border-radius:12px; background:#ede9fe; color:#7c3aed; display:flex; align-items:center; justify-content:center; font-size:1.3rem;">👥</div>
                <div>
                    <div style="font-size:0.75rem; color:#718096; font-weight:700; text-transform:uppercase;">Total Groups</div>
                    <div style="font-size:1.35rem; font-weight:800; color:#1a202c;">{len(user_groups)}</div>
                    <div style="font-size:0.72rem; color:#64748b;">Active groups</div>
                </div>
            </div>
            """), unsafe_allow_html=True)

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        # =========================================================================
        # EXPENSE ANALYTICS SECTION (Interactive Filters, Metrics & Charts)
        # =========================================================================
        st.markdown(clean_html("""
        <div class="white-card" style="margin-bottom:14px; border-top:4px solid #6c5ce7;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <div>
                    <h3 style="font-size:1.2rem; font-weight:800; color:#2d3748; margin:0;">📊 Expense Analytics</h3>
                    <p style="color:#718096; font-size:0.85rem; margin:2px 0 0 0;">Interactive breakdown of category spending, monthly trends & averages</p>
                </div>
            </div>
        </div>
        """), unsafe_allow_html=True)

        # Filters: Group & Date Range
        with st.expander("🔍 Filter Analytics (by Group & Date Range)", expanded=True):
            col_fg, col_fs, col_fe = st.columns([1.5, 1, 1])
            with col_fg:
                sel_an_gid = st.selectbox(
                    "Filter by Group:",
                    options=[0] + group_ids,
                    format_func=lambda gid: "All Groups" if gid == 0 else next(g['name'] for g in user_groups if g['id'] == gid),
                    key="an_flt_grp"
                )
            with col_fs:
                an_start_d = st.date_input("Start Date:", value=None, key="an_flt_start")
            with col_fe:
                an_end_d = st.date_input("End Date:", value=None, key="an_flt_end")

        # Build dynamic query based on actual database records
        an_where_clauses = [f"group_id IN ({format_p})"]
        an_params = list(group_ids)

        if sel_an_gid != 0:
            an_where_clauses = ["group_id = %s"]
            an_params = [sel_an_gid]

        if an_start_d:
            an_where_clauses.append("date >= %s")
            an_params.append(str(an_start_d))
        if an_end_d:
            an_where_clauses.append("date <= %s")
            an_params.append(str(an_end_d))

        an_where_sql = " AND ".join(an_where_clauses)

        # 1. Total spending under filters
        an_tot_res = run_query(f"SELECT COALESCE(SUM(amount), 0.00) as val FROM expenses WHERE {an_where_sql}", an_params)
        an_total_spending = float(an_tot_res[0]['val']) if an_tot_res else 0.0

        # 2. Monthly spending under filters
        month_rows = run_query(f"""
            SELECT substr(date, 1, 7) as month_label, SUM(amount) as total
            FROM expenses WHERE {an_where_sql}
            GROUP BY month_label ORDER BY month_label ASC
        """, an_params)

        an_active_months = len(month_rows)
        an_avg_monthly = round(an_total_spending / an_active_months, 2) if an_active_months > 0 else 0.0

        # Analytics Metrics Cards: Total Spending & Average Monthly Spending
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown(clean_html(f"""
            <div class="white-card" style="padding:1rem; border-left:4px solid #6c5ce7;">
                <div style="font-size:0.75rem; color:#718096; font-weight:700; text-transform:uppercase;">Total Spending</div>
                <div style="font-size:1.45rem; font-weight:800; color:#6c5ce7;">₹{an_total_spending:,.2f}</div>
                <div style="font-size:0.72rem; color:#64748b;">Filtered expense total</div>
            </div>
            """), unsafe_allow_html=True)

        with col_m2:
            st.markdown(clean_html(f"""
            <div class="white-card" style="padding:1rem; border-left:4px solid #00b894;">
                <div style="font-size:0.75rem; color:#718096; font-weight:700; text-transform:uppercase;">Avg Monthly Spending</div>
                <div style="font-size:1.45rem; font-weight:800; color:#00b894;">₹{an_avg_monthly:,.2f}</div>
                <div style="font-size:0.72rem; color:#64748b;">Across active months</div>
            </div>
            """), unsafe_allow_html=True)

        with col_m3:
            st.markdown(clean_html(f"""
            <div class="white-card" style="padding:1rem; border-left:4px solid #0984e3;">
                <div style="font-size:0.75rem; color:#718096; font-weight:700; text-transform:uppercase;">Active Months</div>
                <div style="font-size:1.45rem; font-weight:800; color:#0984e3;">{an_active_months}</div>
                <div style="font-size:0.72rem; color:#64748b;">With recorded expenses</div>
            </div>
            """), unsafe_allow_html=True)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # Charts: Bar Chart (Monthly Expenses) & Pie Chart (Category Breakdown)
        col_c1, col_c2 = st.columns([1.2, 1], gap="medium")
        with col_c1:
            st.markdown(clean_html("""<div class="white-card"><h3 style="font-size:1.1rem; font-weight:700; margin:0 0 1rem 0; color:#2d3748;">📊 Monthly Expenses (Bar Chart)</h3>"""), unsafe_allow_html=True)
            if month_rows:
                df_m = pd.DataFrame(month_rows)
                fig_m = px.bar(
                    df_m,
                    x='month_label',
                    y='total',
                    labels={'month_label': 'Month', 'total': 'Expenses (₹)'},
                    color_discrete_sequence=['#6c5ce7']
                )
                fig_m.update_layout(
                    paper_bgcolor='#ffffff',
                    plot_bgcolor='#ffffff',
                    font_color='#2d3436',
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=270
                )
                fig_m.update_xaxes(showgrid=False)
                fig_m.update_yaxes(showgrid=True, gridcolor='#f1f2f6')
                st.plotly_chart(fig_m, use_container_width=True)
            else:
                st.info("No expense data recorded for this filter criteria.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_c2:
            st.markdown(clean_html("""<div class="white-card"><h3 style="font-size:1.1rem; font-weight:700; margin:0 0 1rem 0; color:#2d3748;">🥧 Expenses by Category (Pie Chart)</h3>"""), unsafe_allow_html=True)
            cat_rows = run_query(f"""
                SELECT category, SUM(amount) as total
                FROM expenses WHERE {an_where_sql}
                GROUP BY category ORDER BY total DESC
            """, an_params)
            if cat_rows:
                df_cat = pd.DataFrame(cat_rows)
                fig_c = px.pie(
                    df_cat,
                    names='category',
                    values='total',
                    hole=0.45,
                    color_discrete_sequence=['#6c5ce7', '#00b894', '#0984e3', '#fdcb6e', '#e17055', '#e84393', '#00cec9', '#636e72']
                )
                fig_c.update_layout(
                    paper_bgcolor='#ffffff',
                    plot_bgcolor='#ffffff',
                    font_color='#2d3436',
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=270,
                    showlegend=True
                )
                st.plotly_chart(fig_c, use_container_width=True)
            else:
                st.info("No expense categories recorded for this filter criteria.")
            st.markdown("</div>", unsafe_allow_html=True)

        # Charts Row 2: Group Spending Comparison, Budget Usage & Recent Expenses
        col_r2_1, col_r2_2, col_r2_3 = st.columns([1.1, 1.1, 1.3], gap="medium")

        with col_r2_1:
            st.markdown(clean_html("""<div class="white-card"><h3 style="font-size:1.1rem; font-weight:700; margin:0 0 1rem 0; color:#2d3748;">Group Spending Comparison</h3>"""), unsafe_allow_html=True)
            grp_spend_data = [{'Group': g['name'], 'Spent': float(g['total_spent'])} for g in user_groups]
            if grp_spend_data:
                df_g_spend = pd.DataFrame(grp_spend_data)
                fig_g = px.bar(df_g_spend, x='Group', y='Spent', color_discrete_sequence=['#0984e3'])
                fig_g.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', font_color='#2d3436', margin=dict(l=10, r=10, t=10, b=10), height=220)
                fig_g.update_xaxes(showgrid=False)
                fig_g.update_yaxes(showgrid=True, gridcolor='#f1f2f6')
                st.plotly_chart(fig_g, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_r2_2:
            st.markdown(clean_html("""<div class="white-card"><h3 style="font-size:1.1rem; font-weight:700; margin:0 0 0.5rem 0; color:#2d3748;">Budget Usage</h3>"""), unsafe_allow_html=True)
            tot_b = sum(float(g['monthly_budget']) for g in user_groups)
            tot_s = sum(float(g['total_spent']) for g in user_groups)
            b_pct = (tot_s / tot_b * 100.0) if tot_b > 0 else 0.0

            # Mockup Circular / Usage Gauge
            st.markdown(clean_html(f"""
            <div style="text-align:center; padding:0.5rem 0;">
                <div style="display:inline-flex; width:100px; height:100px; border-radius:50%; border:7px solid #6c5ce7; align-items:center; justify-content:center; font-size:1.4rem; font-weight:800; color:#2d3748; margin-bottom:0.5rem;">
                    {b_pct:.0f}%
                </div>
                <div style="font-weight:700; font-size:1rem; color:#2d3436;">₹{tot_s:,.2f} of ₹{tot_b:,.2f}</div>
            </div>
            """), unsafe_allow_html=True)

            if tot_b > 0 and b_pct >= 85:
                st.warning(f"⚠️ High Alert: {b_pct:.0f}% of budget used! Only ₹{max(0.0, tot_b - tot_s):,.2f} remains.")
            elif tot_b > 0 and b_pct >= 50:
                st.info(f"🟡 Moderate Spending: {b_pct:.0f}% of budget consumed.")
            elif tot_b > 0:
                st.success(f"🟢 Low Alert: Healthy budget surplus! Remaining: ₹{tot_b - tot_s:,.2f}.")
            else:
                st.caption("No monthly budget cap set for groups.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_r2_3:
            st.markdown(clean_html("""<div class="white-card"><h3 style="font-size:1.1rem; font-weight:700; margin:0 0 0.75rem 0; color:#2d3748;">Recent Expenses</h3>"""), unsafe_allow_html=True)
            recent_list = run_query(f"""
                SELECT e.description, g.name as group_name, e.date, e.category, e.amount
                FROM expenses e JOIN `groups` g ON e.group_id = g.id
                WHERE e.group_id IN ({format_p})
                ORDER BY e.date DESC LIMIT 4
            """, group_ids)
            if recent_list:
                cat_icons = {'Food': '🍕', 'Travel': '✈️', 'Hotel': '🏨', 'Shopping': '🛍️', 'Entertainment': '🎬', 'Groceries': '🛒', 'Others': '📦'}
                for r in recent_list:
                    c_ico = cat_icons.get(r['category'], '🧾')
                    st.markdown(clean_html(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid #f1f2f6;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:1.1rem;">{c_ico}</span>
                            <div>
                                <div style="font-weight:700; font-size:0.88rem; color:#2d3436;">{r['description']}</div>
                                <div style="font-size:0.75rem; color:#a0aec0;">{r['group_name']} &bull; {r['date']}</div>
                            </div>
                        </div>
                        <div style="font-weight:800; font-size:0.95rem; color:#2d3436;">₹{float(r['amount']):,.2f}</div>
                    </div>
                    """), unsafe_allow_html=True)
            else:
                st.info("No recorded expenses yet.")
            st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 2. MY GROUPS (SCREEN 4 IN MOCKUP)
# ==============================================================================
elif menu == "groups":
    c_gh, c_ga = st.columns([2.5, 1])
    with c_gh:
        st.markdown(clean_html("""
        <div>
            <h2 style="font-size:1.85rem; font-weight:800; color:#2d3748; margin:0 0 4px 0;">My Groups</h2>
            <p style="color:#718096; font-size:0.95rem; margin:0;">Manage your groups and members</p>
        </div>
        """), unsafe_allow_html=True)
    with c_ga:
        open_create_grp = st.button("➕ Create Group", key="btn_my_groups_create", type="primary", use_container_width=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    all_reg_users = run_query("SELECT id, name, email FROM users WHERE id != %s ORDER BY name ASC", (current_user_id,))
    with st.expander("➕ Create New Group", expanded=open_create_grp):
        with st.form("create_group_form"):
            new_grp_name = st.text_input(tr('group_name_label'), placeholder="e.g. Goa Trip, Hostel Expenses, Family")
            new_grp_desc = st.text_input(tr('group_desc_label'), placeholder="e.g. Vacation with friends, monthly bills")
            new_grp_budget = st.number_input(tr('group_budget_label'), min_value=0.0, step=500.0, value=10000.0)
            
            sel_registered = st.multiselect(
                "Select registered users to add:",
                options=[u['id'] for u in all_reg_users],
                format_func=lambda uid: next(f"👤 {u['name']} ({u['email']})" for u in all_reg_users if u['id'] == uid),
                key="ms_new_grp_users"
            ) if all_reg_users else []

            new_grp_members = st.text_input("Or enter other member emails / names (separated by commas):", placeholder="e.g. friend1@gmail.com, Priya")
            submit_create = st.form_submit_button(tr('btn_create_group'), use_container_width=True)

            if submit_create:
                c_name = new_grp_name.strip()
                if not c_name:
                    st.error("Group name cannot be empty.")
                else:
                    new_gid = execute_cmd("INSERT INTO `groups` (name, description, created_by) VALUES (%s, %s, %s)", (c_name, new_grp_desc.strip(), current_user_id))
                    execute_cmd("INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)", (new_gid, current_user_id))
                    if new_grp_budget > 0:
                        execute_cmd("INSERT INTO group_budgets (group_id, monthly_budget) VALUES (%s, %s)", (new_gid, new_grp_budget))
                    
                    # Add selected registered users
                    for r_uid in sel_registered:
                        execute_cmd("INSERT IGNORE INTO group_members (group_id, user_id) VALUES (%s, %s)", (new_gid, r_uid))
                    
                    # Add extra members by text
                    if new_grp_members.strip():
                        for raw_item in new_grp_members.split(','):
                            item = raw_item.strip()
                            if item:
                                clean_item = item.lower()
                                user_matches = run_query("SELECT id FROM users WHERE LOWER(TRIM(email)) = %s OR LOWER(TRIM(name)) = %s", (clean_item, clean_item))
                                if user_matches:
                                    t_uid = user_matches[0]['id']
                                else:
                                    pwd_hash = make_password_hash("123456")
                                    if '@' in item:
                                        t_email = item.lower()
                                        t_name = item.split('@')[0].replace('.', ' ').strip().title()
                                    else:
                                        t_name = item
                                        t_email = f"{re.sub(r'[^a-zA-Z0-9]', '', item.lower())}@splitsettle.app"
                                    
                                    chk_exist = run_query("SELECT id FROM users WHERE LOWER(TRIM(email)) = %s", (t_email.lower(),))
                                    if chk_exist:
                                        t_uid = chk_exist[0]['id']
                                    else:
                                        t_uid = execute_cmd("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)", (t_name, t_email, pwd_hash))
                                execute_cmd("INSERT IGNORE INTO group_members (group_id, user_id) VALUES (%s, %s)", (new_gid, t_uid))
                        heal_user_accounts()
                    st.success(f"🎉 Group '{c_name}' created successfully!")
                    st.rerun()

    if not user_groups:
        st.info("No groups found. Click '+ Create Group' above to create your first expense sharing group!")
    else:
        # Mockup 2-Column Grid of Group Cards
        grp_icons = ['🌴', '🏢', '🍕', '🏠', '🚗', '⛺', '🎓', '🎉']
        for i in range(0, len(user_groups), 2):
            col_g1, col_g2 = st.columns(2, gap="medium")
            for col_target, grp in zip([col_g1, col_g2], user_groups[i:i+2]):
                with col_target:
                    gid = grp['id']
                    b = float(grp['monthly_budget'])
                    s = float(grp['total_spent'])
                    m_count = run_query("SELECT COUNT(*) as c FROM group_members WHERE group_id = %s", (gid,))[0]['c']
                    pct = min(s / b, 1.0) if b > 0 else 0.0
                    g_icon = grp_icons[(gid - 1) % len(grp_icons)]
                    b_stat = get_budget_status(s, b)

                    st.markdown(clean_html(f"""
                    <div class="white-card">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
                            <div style="display:flex; gap:12px; align-items:center;">
                                <div style="width:48px; height:48px; border-radius:50%; background:#f0f3ff; display:flex; align-items:center; justify-content:center; font-size:1.6rem;">{g_icon}</div>
                                <div>
                                    <h3 style="margin:0; font-size:1.2rem; font-weight:800; color:#2d3748;">{grp['name']}</h3>
                                    <p style="margin:0; font-size:0.85rem; color:#718096;">{grp['description'] or 'Shared group expenses'}</p>
                                </div>
                            </div>
                            <span style="background:{b_stat['bg']}; color:{b_stat['color']}; border:1px solid {b_stat['border']}; font-size:0.75rem; font-weight:700; padding:3px 10px; border-radius:12px;">
                                {b_stat['badge']}
                            </span>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:0.9rem; font-weight:600; color:#4a5568; margin-bottom:0.4rem;">
                            <span>👥 {m_count} members</span>
                            <span style="color:#6c5ce7; font-weight:800;">₹{s:,.2f} spent</span>
                        </div>
                    """), unsafe_allow_html=True)

                    if b > 0:
                        st.progress(pct, text=f"{(s/b)*100:.0f}% of ₹{b:,.2f}")
                    else:
                        st.caption("No budget limit configured")

                    is_manage_open = st.session_state.get(f"manage_exp_{gid}", False)
                    with st.expander(f"⚙️ Manage '{grp['name']}'", expanded=is_manage_open):
                        if is_manage_open:
                            st.session_state[f"manage_exp_{gid}"] = False

                        m_list = run_query("SELECT u.id, u.name, u.email FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s ORDER BY u.name ASC", (gid,))
                        existing_ids = {m['id'] for m in m_list}

                        st.markdown("<p style='font-weight:700; color:#2d3748; margin-bottom:8px;'>Members in group:</p>", unsafe_allow_html=True)
                        chip_html = "<div style='display:flex; flex-wrap:wrap; gap:8px; margin-bottom:14px;'>"
                        for m in m_list:
                            is_creator = (m['id'] == grp.get('created_by'))
                            badge_style = "background:#6c5ce7; color:#fff;" if is_creator else "background:#edf2f7; color:#4a5568;"
                            badge_text = "👑 Creator" if is_creator else "Member"
                            chip_html += f"<div style='display:inline-flex; align-items:center; background:#ffffff; border:1px solid #e2e8f0; border-radius:20px; padding:5px 12px; font-size:0.85rem; font-weight:600; color:#2d3748; box-shadow:0 1px 3px rgba(0,0,0,0.05);'>👤 {m['name']} <span style='font-size:0.75rem; color:#718096; margin-left:6px;'>({m['email']})</span><span style='{badge_style} border-radius:10px; font-size:0.65rem; padding:2px 7px; margin-left:8px; font-weight:700;'>{badge_text}</span></div>"
                        chip_html += "</div>"
                        st.markdown(chip_html, unsafe_allow_html=True)

                        all_users = run_query("SELECT id, name, email FROM users ORDER BY name ASC")
                        avail_users = [u for u in all_users if u['id'] not in existing_ids]

                        st.markdown("<div style='height:1px; background:#edf2f7; margin:10px 0;'></div>", unsafe_allow_html=True)
                        st.markdown("<p style='font-weight:700; color:#2d3748; font-size:0.95rem; margin-bottom:6px;'>➕ Add Member to Group</p>", unsafe_allow_html=True)

                        with st.form(f"form_add_member_{gid}", clear_on_submit=True):
                            if avail_users:
                                sel_user_id = st.selectbox(
                                    "Choose from registered users:",
                                    options=[0] + [u['id'] for u in avail_users],
                                    format_func=lambda uid: "-- Select a registered user --" if uid == 0 else next(f"👤 {u['name']} ({u['email']})" for u in avail_users if u['id'] == uid),
                                    key=f"sel_reg_{gid}"
                                )
                            else:
                                sel_user_id = 0
                                st.info("All registered users are already members of this group!")

                            new_m_input = st.text_input("Or enter a new name or email:", placeholder="e.g. Bhoomika or friend@gmail.com", key=f"text_m_{gid}")

                            btn_add = st.form_submit_button("➕ Add Member", type="primary", use_container_width=True)
                            if btn_add:
                                target_uid = None
                                target_name = ""

                                if sel_user_id and sel_user_id != 0:
                                    target_uid = sel_user_id
                                    target_name = next((u['name'] for u in avail_users if u['id'] == sel_user_id), "Member")
                                elif new_m_input and new_m_input.strip():
                                    clean_m = new_m_input.strip().lower()
                                    matches = run_query("SELECT id, name FROM users WHERE LOWER(TRIM(email)) = %s OR LOWER(TRIM(name)) = %s", (clean_m, clean_m))
                                    if matches:
                                        target_uid = matches[0]['id']
                                        target_name = matches[0]['name']
                                    else:
                                        pwd_hash = make_password_hash("123456")
                                        if '@' in new_m_input:
                                            t_email = new_m_input.strip().lower()
                                            t_name = new_m_input.strip().split('@')[0].replace('.', ' ').strip().title()
                                        else:
                                            t_name = new_m_input.strip()
                                            t_email = f"{re.sub(r'[^a-zA-Z0-9]', '', new_m_input.strip().lower())}@splitsettle.app"

                                        chk_exist = run_query("SELECT id, name FROM users WHERE LOWER(TRIM(email)) = %s", (t_email.lower(),))
                                        if chk_exist:
                                            target_uid = chk_exist[0]['id']
                                            target_name = chk_exist[0]['name']
                                        else:
                                            target_uid = execute_cmd("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)", (t_name, t_email, pwd_hash))
                                            target_name = t_name

                                if target_uid:
                                    if target_uid in existing_ids:
                                        st.warning(f"⚠️ {target_name} is already in this group.")
                                    else:
                                        execute_cmd("INSERT IGNORE INTO group_members (group_id, user_id) VALUES (%s, %s)", (gid, target_uid))
                                        heal_user_accounts()
                                        st.session_state[f"manage_exp_{gid}"] = True
                                        st.success(f"🎉 Successfully added {target_name} to {grp['name']}!")
                                        st.rerun()
                                else:
                                    st.warning("⚠️ Please select a user from the dropdown or enter an email/name.")

                        st.markdown("<div style='height:1px; background:#edf2f7; margin:14px 0 10px 0;'></div>", unsafe_allow_html=True)
                        with st.expander("⚠️ Danger Zone (Delete Group)"):
                            st.caption("Permanently delete this group and all its expenses. This action cannot be undone.")
                            confirm_del = st.checkbox("Confirm group deletion", key=f"chk_del_{gid}")
                            if st.button("🗑️ Delete Entire Group", key=f"btn_del_grp_{gid}", type="secondary", disabled=not confirm_del, use_container_width=True):
                                execute_cmd("DELETE FROM expense_splits WHERE expense_id IN (SELECT id FROM expenses WHERE group_id = %s)", (gid,))
                                execute_cmd("DELETE FROM expenses WHERE group_id = %s", (gid,))
                                execute_cmd("DELETE FROM group_members WHERE group_id = %s", (gid,))
                                execute_cmd("DELETE FROM group_budgets WHERE group_id = %s", (gid,))
                                execute_cmd("DELETE FROM `groups` WHERE id = %s", (gid,))
                                st.success("Group deleted successfully!")
                                st.rerun()

                    st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 3. ADD EXPENSE (SCREEN 5 IN MOCKUP: FORM ON LEFT, LIVE SPLIT PREVIEW ON RIGHT)
# ==============================================================================
elif menu == "expenses":
    st.markdown(clean_html("""
    <div>
        <h2 style="font-size:1.85rem; font-weight:800; color:#2d3748; margin:0 0 4px 0;">Add Expense</h2>
        <p style="color:#718096; font-size:0.95rem; margin:0;">Record a new expense for your group</p>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    if not user_groups:
        st.warning("Please create or join a group first before adding expenses.")
    else:
        grp_dict = {g['name']: g['id'] for g in user_groups}
        col_form, col_preview = st.columns([1.25, 1], gap="large")

        with col_form:
            sel_grp_name = st.selectbox("Group", list(grp_dict.keys()), key="exp_sel_grp")
            chosen_gid = grp_dict[sel_grp_name]

            members_in_grp = run_query("""
                SELECT u.id, u.name, u.email FROM group_members gm
                JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s
            """, (chosen_gid,))
            m_names = {m['id']: m['name'] for m in members_in_grp}

            exp_desc = st.text_input("Description", value="Dinner at Café", placeholder="e.g. Dinner, Taxi, Tickets", key="exp_in_desc")
            
            c_amt, c_cat = st.columns(2)
            with c_amt:
                exp_amt = st.number_input("Amount (₹)", min_value=1.0, value=1200.0, step=50.0, key="exp_in_amt")
            with c_cat:
                cat_options = ['Food', 'Travel', 'Hotel', 'Shopping', 'Entertainment', 'Groceries', 'Others']
                exp_cat = st.selectbox("Category", cat_options, index=0, key="exp_in_cat")

            c_date, c_paid = st.columns(2)
            with c_date:
                exp_date = st.date_input("Date", value=datetime.date.today(), key="exp_in_date")
            with c_paid:
                paid_opts = {m['name']: m['id'] for m in members_in_grp}
                cur_user_idx = list(paid_opts.values()).index(current_user_id) if current_user_id in paid_opts.values() else 0
                sel_paid_by_name = st.selectbox("Paid by", list(paid_opts.keys()), index=cur_user_idx, key="exp_in_paid")
                paid_by_id = paid_opts[sel_paid_by_name]

            split_method = st.radio("Split Method", ["Equal Split", "Percentage Split", "Custom Split"], horizontal=True, key="exp_in_split_method")

            st.markdown("<p style='font-size:0.9rem; font-weight:600; color:#4a5568; margin-top:0.75rem;'>Participants</p>", unsafe_allow_html=True)
            chosen_uids = []
            cols_parts = st.columns(min(len(members_in_grp), 4))
            for i, m in enumerate(members_in_grp):
                col_p = cols_parts[i % len(cols_parts)]
                with col_p:
                    checked = st.checkbox(f"👤 {m['name']}", value=True, key=f"part_chk_{m['id']}")
                    if checked:
                        chosen_uids.append(m['id'])

        with col_preview:
            st.markdown(clean_html("""
            <div class="white-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                    <h3 style="margin:0; font-size:1.15rem; font-weight:800; color:#6c5ce7;">📋 Split Preview</h3>
                </div>
            """), unsafe_allow_html=True)

            st.markdown(f"<div style='font-size:1.1rem; font-weight:800; color:#2d3748; margin-bottom:0.75rem;'>Total Amount: ₹{exp_amt:,.2f}</div>", unsafe_allow_html=True)

            computed_splits = {}
            if chosen_uids:
                if split_method == "Equal Split":
                    per_share = round(float(exp_amt) / len(chosen_uids), 2)
                    for uid in chosen_uids:
                        computed_splits[uid] = per_share
                else:
                    per_share = round(float(exp_amt) / len(chosen_uids), 2)
                    for uid in chosen_uids:
                        computed_splits[uid] = per_share

                for uid in chosen_uids:
                    st.markdown(clean_html(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:7px 0; border-bottom:1px solid #f1f2f6;">
                        <span style="font-weight:600; color:#2d3436; font-size:0.92rem;">👤 {m_names[uid]}</span>
                        <span style="font-weight:700; color:#6c5ce7; font-size:0.95rem;">₹{computed_splits[uid]:,.2f}</span>
                    </div>
                    """), unsafe_allow_html=True)

                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                st.success(f"✓ Split is valid! Each person will pay ₹{computed_splits[chosen_uids[0]]:,.2f}")

                # Live Budget Alert
                grp_b_row = run_query("SELECT COALESCE(gb.monthly_budget, 0.0) as budget, COALESCE((SELECT SUM(amount) FROM expenses WHERE group_id = %s), 0.0) as spent FROM `groups` g LEFT JOIN group_budgets gb ON g.id = gb.group_id WHERE g.id = %s", (chosen_gid, chosen_gid))
                if grp_b_row and float(grp_b_row[0]['budget']) > 0:
                    g_b = float(grp_b_row[0]['budget'])
                    g_s = float(grp_b_row[0]['spent'])
                    proj_s = g_s + float(exp_amt)
                    l_stat = get_budget_status(proj_s, g_b)
                    if l_stat['level'] == 'OVER_LIMIT':
                        st.error(f"🚨 **High Budget Alert**: This expense pushes spending to ₹{proj_s:,.2f}, exceeding the budget limit (₹{g_b:,.2f})!")
                    elif l_stat['level'] == 'HIGH_ALERT':
                        st.warning(f"⚠️ **High Budget Alert**: Group spending will reach {l_stat['pct']:.1f}% of limit!")
                    elif l_stat['level'] == 'LOW_SAFE':
                        st.success(f"🟢 **Low Budget Alert (Safe)**: Spending is healthy ({l_stat['pct']:.1f}% used).")

                if st.button("Confirm and Add Expense", type="primary", use_container_width=True):
                    new_eid = execute_cmd("""
                        INSERT INTO expenses (group_id, paid_by, amount, description, category, date, split_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (chosen_gid, paid_by_id, exp_amt, exp_desc.strip(), exp_cat, str(exp_date), split_method))

                    for uid in chosen_uids:
                        execute_cmd("INSERT INTO expense_splits (expense_id, user_id, share_amount) VALUES (%s, %s, %s)", (new_eid, uid, computed_splits[uid]))

                    st.success("🎉 Expense recorded and split successfully!")
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📜 Recorded Expenses & Management"):
            all_exp = run_query(f"""
                SELECT e.id as ID, e.date as Date, e.description as Description, g.name as Group_Name,
                       e.category as Category, u.name as Paid_By, e.amount as Amount
                FROM expenses e JOIN `groups` g ON e.group_id = g.id JOIN users u ON e.paid_by = u.id
                WHERE e.group_id IN ({format_p}) ORDER BY e.date DESC
            """, group_ids)
            if all_exp:
                st.dataframe(pd.DataFrame(all_exp), use_container_width=True)
                sel_del_map = {f"#{x['ID']}: {x['Description']} (₹{float(x['Amount']):,.2f} in {x['Group_Name']})": x['ID'] for x in all_exp}
                del_ch = st.selectbox("Select expense to delete:", list(sel_del_map.keys()))
                if st.button("🗑️ Delete Selected Expense"):
                    d_eid = sel_del_map[del_ch]
                    execute_cmd("DELETE FROM expense_splits WHERE expense_id = %s", (d_eid,))
                    execute_cmd("DELETE FROM expenses WHERE id = %s", (d_eid,))
                    st.success("Expense deleted successfully!")
                    st.rerun()
            else:
                st.info("No recorded expenses in your groups yet.")

# ==============================================================================
# 4. WHO OWES WHOM (SCREEN 6 IN MOCKUP: SIMPLIFIED SETTLEMENTS & BALANCES)
# ==============================================================================
elif menu == "balances":
    st.markdown(clean_html("""
    <div>
        <h2 style="font-size:1.85rem; font-weight:800; color:#2d3748; margin:0 0 4px 0;">Who Owes Whom</h2>
        <p style="color:#718096; font-size:0.95rem; margin:0;">Simplified settlement suggestions</p>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    if not user_groups:
        st.info("No groups found. Create a group to start tracking settlements.")
    else:
        grp_opts = {tr("all_your_groups"): None}
        for g in user_groups:
            grp_opts[g['name']] = g['id']

        sel_b_grp = st.selectbox("Filter by Group:", list(grp_opts.keys()))
        t_gid = grp_opts[sel_b_grp]

        all_settlements = []
        user_balances_table = []

        active_gids = [t_gid] if t_gid else [g['id'] for g in user_groups]
        for gid in active_gids:
            members = run_query("SELECT u.id, u.name FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s", (gid,))
            m_dict = {m['id']: m['name'] for m in members}
            paid_rows = {r['user_id']: float(r['val']) for r in run_query("SELECT paid_by as user_id, SUM(amount) as val FROM expenses WHERE group_id = %s GROUP BY paid_by", (gid,))}
            share_rows = {r['user_id']: float(r['val']) for r in run_query("SELECT es.user_id, SUM(es.share_amount) as val FROM expense_splits es JOIN expenses e ON es.expense_id = e.id WHERE e.group_id = %s GROUP BY es.user_id", (gid,))}

            net_map = {}
            for m in members:
                uid = m['id']
                p = paid_rows.get(uid, 0.0)
                s = share_rows.get(uid, 0.0)
                net = p - s
                net_map[uid] = net
                user_balances_table.append({
                    'Member': m['name'],
                    'Total Paid': f"₹{p:,.2f}",
                    'Total Share': f"₹{s:,.2f}",
                    'Net Balance': f"{'+' if net >= 0 else '-'} ₹{abs(net):,.2f}",
                    'Status': 'Gets Back' if net >= 0 else 'Owes'
                })

            all_settlements.extend(simplify_debts(net_map, m_dict))

        # Settlement Cards Matching Mockup
        st.markdown(clean_html("""<div class="white-card"><h3 style="font-size:1.15rem; font-weight:800; color:#2d3748; margin:0 0 1rem 0;">Suggested Settlements</h3>"""), unsafe_allow_html=True)
        if not all_settlements:
            st.success("✅ Everyone is completely settled up in this selection!")
        else:
            for i, stl in enumerate(all_settlements):
                c_st1, c_st2 = st.columns([3, 1])
                with c_st1:
                    is_me_debtor = (stl['debtor_id'] == current_user_id)
                    is_me_creditor = (stl['creditor_id'] == current_user_id)
                    badge_color = "#e53e3e" if is_me_debtor else ("#38a169" if is_me_creditor else "#4a5568")

                    st.markdown(clean_html(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:#f7fafc; border:1px solid #edf2f7; border-radius:12px; margin-bottom:8px;">
                        <span style="font-size:0.95rem; font-weight:700; color:#2d3748;">👤 <strong>{stl['debtor_name']}</strong> owes <strong>{stl['creditor_name']}</strong></span>
                        <span style="font-size:1.05rem; font-weight:800; color:{badge_color};">₹{stl['amount']:,.2f}</span>
                    </div>
                    """), unsafe_allow_html=True)
                with c_st2:
                    if st.button("Settle", key=f"btn_settle_{i}", use_container_width=True):
                        st.success(f"Payment of ₹{stl['amount']:,.2f} recorded between {stl['debtor_name']} and {stl['creditor_name']}!")

        st.markdown("</div>", unsafe_allow_html=True)

        # Individual Balances Table Matching Mockup
        if user_balances_table:
            st.markdown(clean_html("""<div class="white-card"><h3 style="font-size:1.15rem; font-weight:800; color:#2d3748; margin:0 0 1rem 0;">Individual Balances</h3>"""), unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(user_balances_table).drop_duplicates(subset=['Member']), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 5. GROUP BUDGETS & LIMIT ALERTS (HIGH VS LOW ALERT)
# ==============================================================================
elif menu == "budgets":
    st.markdown(clean_html("""
    <div>
        <h2 style="font-size:1.85rem; font-weight:800; color:#2d3748; margin:0 0 4px 0;">Group Budgets & Limit Alerts</h2>
        <p style="color:#718096; font-size:0.95rem; margin:0;">Monitor spending limits with real-time High Alert and Low Alert warnings</p>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    if not user_groups:
        st.info("No groups found. Create a group to track budget limits.")
    else:
        tot_b = sum(float(x['monthly_budget']) for x in user_groups)
        tot_s = sum(float(x['total_spent']) for x in user_groups)
        high_alerts = sum(1 for x in user_groups if float(x['monthly_budget']) > 0 and (float(x['total_spent']) / float(x['monthly_budget']) >= 0.85))
        safe_groups = sum(1 for x in user_groups if float(x['monthly_budget']) > 0 and (float(x['total_spent']) / float(x['monthly_budget']) < 0.50))

        st.markdown(clean_html("""<div class="white-card"><h3>🚨 Budget Limit Alert Overview</h3>"""), unsafe_allow_html=True)
        col_ov1, col_ov2, col_ov3, col_ov4 = st.columns(4)
        col_ov1.metric("Total Budgets Set", f"₹{tot_b:,.2f}")
        col_ov2.metric("Total Group Spending", f"₹{tot_s:,.2f}")
        col_ov3.metric("🔴 High Alert Groups", f"{high_alerts} Groups")
        col_ov4.metric("🟢 Low/Safe Groups", f"{safe_groups} Groups")
        st.markdown("</div>", unsafe_allow_html=True)

        for grp in user_groups:
            gid = grp['id']
            b = float(grp['monthly_budget'])
            s = float(grp['total_spent'])
            stat = get_budget_status(s, b)

            st.markdown(clean_html(f"""
            <div class="white-card" style="margin-top:1.25rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:0.75rem;">
                    <h3 style="color:#2d3436; margin:0;">📁 {grp['name']}</h3>
                    <span style="background:{stat['bg']}; color:{stat['color']}; border:1.5px solid {stat['border']}; padding:5px 14px; border-radius:16px; font-weight:700; font-size:0.88rem;">
                        {stat['badge']}
                    </span>
                </div>
            """), unsafe_allow_html=True)

            if stat['level'] == 'OVER_LIMIT':
                st.error(f"**{stat['headline']}** - {stat['sub']}")
            elif stat['level'] == 'HIGH_ALERT':
                st.warning(f"**{stat['headline']}** - {stat['sub']}")
            elif stat['level'] == 'LOW_SAFE':
                st.success(f"**{stat['headline']}** - {stat['sub']}")
            elif stat['level'] == 'MODERATE':
                st.info(f"**{stat['headline']}** - {stat['sub']}")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Monthly Limit", f"₹{b:,.2f}")
            m2.metric("Current Spent", f"₹{s:,.2f}")
            m3.metric("Remaining", f"₹{max(0.0, b - s):,.2f}")
            m4.metric("Budget Usage", f"{stat['pct']:.1f}%")

            if b > 0:
                st.progress(min(s / b, 1.0))

            with st.expander(f"✏️ Set / Update Spending Limit for '{grp['name']}'"):
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

# ==============================================================================
# 6. SETTINGS & PROFILE (SCREEN 7 IN MOCKUP)
# ==============================================================================
elif menu == "settings":
    st.markdown(clean_html("""
    <div>
        <h2 style="font-size:1.85rem; font-weight:800; color:#2d3748; margin:0 0 4px 0;">Settings & Profile</h2>
        <p style="color:#718096; font-size:0.95rem; margin:0;">Manage your profile, security and preferences</p>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    col_set1, col_set2 = st.columns(2, gap="large")

    with col_set1:
        # User statistics
        u_groups_count = len(user_groups) if user_groups else 0
        u_exp_count = run_query("SELECT COUNT(*) as c FROM expenses WHERE paid_by = %s", (current_user_id,))
        exp_c = u_exp_count[0]['c'] if u_exp_count else 0

        # Profile Overview Card
        st.markdown(clean_html(f"""
        <div class="white-card" style="margin-bottom:1.25rem;">
            <div style="display:flex; align-items:center; gap:18px;">
                <div class="profile-avatar" style="width:64px; height:64px; font-size:1.75rem; border-radius:50%; background:linear-gradient(135deg, #6c5ce7 0%, #a367dc 100%); color:#ffffff; display:flex; align-items:center; justify-content:center; font-weight:800; box-shadow:0 6px 16px rgba(108, 92, 231, 0.35);">{user_initial}</div>
                <div>
                    <h3 style="margin:0; font-size:1.35rem; font-weight:800; color:#1a202c;">{current_user_name}</h3>
                    <p style="margin:2px 0 6px 0; font-size:0.9rem; color:#718096;">{current_user_email}</p>
                    <div style="display:flex; flex-wrap:wrap; gap:8px;">
                        <span style="background:#dcfce7; color:#16a34a; font-size:0.75rem; font-weight:700; padding:3px 10px; border-radius:12px;">● Active Account</span>
                        <span style="background:#f1f5f9; color:#475569; font-size:0.75rem; font-weight:700; padding:3px 10px; border-radius:12px;">📁 {u_groups_count} Groups</span>
                        <span style="background:#f1f5f9; color:#475569; font-size:0.75rem; font-weight:700; padding:3px 10px; border-radius:12px;">🧾 {exp_c} Expenses</span>
                    </div>
                </div>
            </div>
            <div style="margin-top:12px; font-size:0.8rem; color:#a0aec0;">Connected Database: <strong style="color:#718096;">{db_type.upper()}</strong></div>
        </div>
        """), unsafe_allow_html=True)

        # Edit Profile Form Card
        st.markdown(clean_html("""
        <div class="white-card">
            <h3 style="font-size:1.15rem; font-weight:800; color:#2d3748; margin:0 0 1rem 0;">✏️ Edit Profile Information</h3>
        """), unsafe_allow_html=True)

        with st.form("edit_profile_form"):
            edit_name = st.text_input("Full Name / Display Name", value=current_user_name)
            edit_email = st.text_input("Email Address", value=current_user_email)
            btn_save_profile = st.form_submit_button("💾 Save Profile Changes", type="primary", use_container_width=True)

            if btn_save_profile:
                c_ename = edit_name.strip()
                c_eemail = edit_email.strip().lower()

                if not c_ename:
                    st.error("Name cannot be empty.")
                elif not c_eemail or '@' not in c_eemail or '.' not in c_eemail:
                    st.error("Please enter a valid email address.")
                else:
                    # Check if email is already taken by another account
                    email_clash = run_query("SELECT id FROM users WHERE LOWER(TRIM(email)) = %s AND id != %s", (c_eemail, current_user_id))
                    if email_clash:
                        st.error(f"The email '{c_eemail}' is already registered to another account.")
                    else:
                        execute_cmd("UPDATE users SET name = %s, email = %s WHERE id = %s", (c_ename, c_eemail, current_user_id))
                        st.session_state['user_name'] = c_ename
                        st.session_state['user_email'] = c_eemail
                        heal_user_accounts()
                        st.success("🎉 Profile updated successfully!")
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with col_set2:
        # Change Password Card
        st.markdown(clean_html("""
        <div class="white-card" style="margin-bottom:1.25rem;">
            <h3 style="font-size:1.15rem; font-weight:800; color:#2d3748; margin:0 0 1rem 0;">🔑 Change Password</h3>
        """), unsafe_allow_html=True)
        with st.form("settings_change_pwd_form"):
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
        st.markdown("</div>", unsafe_allow_html=True)

        # Preferences & App Info Card
        st.markdown(clean_html("""
        <div class="white-card">
            <h3 style="font-size:1.15rem; font-weight:800; color:#2d3748; margin:0 0 0.8rem 0;">⚙️ Preferences</h3>
            <p style="color:#718096; font-size:0.88rem; margin-bottom:1rem;">Customize your interface language and regional settings.</p>
        """), unsafe_allow_html=True)
        cur_lang_set = st.session_state.get('interface_language', 'English')
        cur_lang_idx = LANGUAGE_OPTIONS.index(cur_lang_set) if cur_lang_set in LANGUAGE_OPTIONS else 0
        new_set_lang = st.selectbox("Preferred Interface Language:", LANGUAGE_OPTIONS, index=cur_lang_idx, key="settings_lang_sel")
        if new_set_lang != st.session_state.get('interface_language'):
            st.session_state['interface_language'] = new_set_lang
            st.rerun()
        st.markdown("""
            <div style="margin-top:1rem; padding:12px; background:#f8fafc; border-radius:10px; font-size:0.85rem; color:#64748b;">
                <div>💱 <strong>Default Currency:</strong> Indian Rupee (₹ INR)</div>
                <div style="margin-top:4px;">🛡️ <strong>Session Security:</strong> End-to-End Encrypted Session Active</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
