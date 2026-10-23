# Expense Split and Settlement System
**B.Tech Major Project Edition**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://expense-split-settlement.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-black.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)](https://www.mysql.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Cloud-FF4B4B.svg)](https://streamlit.io/)

A modern, responsive, and full-featured financial web application designed to track shared group expenses, monitor real-time group spending budgets with automated limit alerts, simplify peer-to-peer debt settlements using optimal cash-flow algorithms, and provide interactive expense analytics.

🌐 **Live Streamlit Cloud Deployment**: [https://expense-split-settlement.streamlit.app/](https://expense-split-settlement.streamlit.app/)  
📂 **GitHub Repository**: [https://github.com/grajasree/expense-split-settlement-system-flask](https://github.com/grajasree/expense-split-settlement-system-flask)

---

## 🌟 Key Features & Capabilities

### 1. User Authentication & Profile Management
- Secure user registration, login, and session persistence using Werkzeug PBKDF2 password hashing.
- Show/hide password toggle for enhanced usability.
- **Edit Profile**: Seamlessly update full name, registered email, and password.
- **Account Statistics**: View user member join date, total groups joined, lifetime amount paid, and net balance.
- Top-right interactive **Profile Badge** for quick profile access.

### 2. Group Management & Member Collaboration
- Create and manage groups with custom names, descriptions, and monthly spending budgets.
- **Effortless Member Addition**: Add registered users directly using a smart dropdown selector or email lookup.
- Visual member chips displaying member names and roles (Group Creator / Member).
- Automatic cascade handling and settlement protection when managing group members.

### 3. Expense Tracking & Advanced Interactive Split Methods
- **Equal Split**: Evenly divides expenses among selected participants with automatic cent/paisa remainder distribution.
- **Percentage Split (Interactive & Live)**:
  - Custom percentage input box (`%`) for each selected participant.
  - Live ₹ share calculation preview for every member in real time.
  - Strict 100.0% total validation with instant visual indicators showing remaining or excess percentage.
- **Custom Split (Interactive & Live)**:
  - Custom rupee amount input (`₹`) per participant.
  - Real-time sum tracking matching against total expense with validation preventing mismatched submissions.
- Categorization across 10 categories (*Food & Dining, Transportation, Housing & Rent, Utilities, Entertainment, Groceries, Travel, Healthcare, Shopping, Other*).
- Complete expense editing, deletion, and split recalculation workflows.

### 4. Interactive Expense Analytics
- **Category Breakdown Chart**: Visual doughnut/pie chart showing spending proportions across expense categories.
- **Monthly Spending Trends**: Interactive bar chart displaying month-by-month expenditure.
- **Summary Metrics**: High-level KPI cards for Total Spending, Average Monthly Spending, and Transaction Count.
- **Dynamic Filters**: Real-time filtering by Date Range (From/To) and specific Group.

### 5. Optimal Debt Simplification ("Who Owes Whom")
- Real-time balance calculation: `Net Balance = Total Paid - Total Share`.
- Greedy cash-flow minimization algorithm that eliminates circular debts into the minimum number of direct peer-to-peer repayments (e.g., *Alice owes Bob ₹350*).
- One-click **Record Settlement** feature to clear debts and record payments.

### 6. Group Spending Budgets & 4-Tier Automated Alert System
- Define and adjust monthly budgets per group.
- Automated real-time spending status alerts:
  - 🟢 **Low Alert / Safe**: `< 75%` budget consumed.
  - 🟡 **Moderate Warning**: `75% - 84.9%` budget consumed.
  - ⚠️ **High Budget Alert**: `85% - 99.9%` budget consumed.
  - 🚨 **Over Budget / Exceeded**: `100%+` budget exceeded with immediate warning notices.

### 7. Modern Finance UI (Midnight Indigo & Ice Blue)
- Styled with a premium financial color palette:
  - **Midnight Indigo (`#4338CA`)**: Navigation, primary buttons, active menus, and key headings.
  - **Ice Blue (`#BAE6FD`)**: Card accents, hover states, metric highlights, and chart themes.
- Clean typography, rounded cards, responsive mobile/tablet/desktop layouts, and light/dark theme toggle.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Chart.js, FontAwesome 6, Jinja2 Templates |
| **Backend** | Python 3.10+, Flask Framework, Streamlit Cloud framework |
| **Database** | MySQL 8.0 (PyMySQL connection pool) / SQLite (Standalone Cloud fallback) |
| **Security** | Werkzeug PBKDF2:SHA256 password hashing, CSRF session tokens, SQL parameterized queries |
| **Hosting** | Streamlit Community Cloud (Live Web), Localhost (Flask & MySQL) |

---

## 💻 Setup & Installation Guide (Windows)

The application supports two run modes:
- **Mode A: Flask Web Application with MySQL** (Recommended for local development & review)
- **Mode B: Streamlit Cloud / Local Streamlit Application** (Instant setup without MySQL)

---

### Prerequisites
1. **Python 3.10 or newer** installed (ensure `Add python.exe to PATH` was selected during installation).
2. **MySQL Server 8.0** (or XAMPP / MySQL Community) running locally for Mode A.
3. **Visual Studio Code (VS Code)** or your preferred IDE.

---

### Mode A: Running the Flask Application (with MySQL)

#### Step 1: Open the Project
Open VS Code, click **File > Open Folder...**, and select:
```
c:\Users\akula\OneDrive\Desktop\Rajasree_DES\expense-split-settlement-system
```
Open a PowerShell terminal (`Ctrl + ~`).

#### Step 2: Create & Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```
*(If execution is blocked by Windows, run: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`)*

#### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

#### Step 4: Configure Database Credentials
Create or edit `.env` in the root folder:
```env
SECRET_KEY=btech-expense-split-secret-key-2026

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_password
DB_NAME=expense_split_db
```

#### Step 5: Initialize the Database
```powershell
python db.py init
```

#### Step 6 (Optional): Seed Demo Data
To instantly populate realistic sample groups, expenses, and settlements for your presentation:
```powershell
python seed.py
```
*(Includes 4 demo users: `rahul@example.com`, `priya@example.com`, `amit@example.com`, `sneha@example.com` with password: `password123`)*

#### Step 7: Launch Flask Server
```powershell
python app.py
```
Open your browser and visit: **`http://127.0.0.1:5000`**

---

### Mode B: Running the Streamlit Application (Standalone / Cloud)

You can run the full interactive application using Streamlit without needing a local MySQL server (uses embedded SQLite):

```powershell
# Ensure virtual environment is activated
streamlit run streamlit_app.py
```
Open your browser and visit: **`http://localhost:8501`**

Default pre-registered credentials:
- **Email**: `sree11@gmail.com` | **Password**: `sree@11`
- **Email**: `bhoomika@gmail.com` | **Password**: `123456`
- **Email**: `priya@gmail.com` | **Password**: `123456`
*(Or click "Register" to create your own account)*

---

## 🧪 Step-by-Step Feature Walkthrough

1. **User Authentication & Profile**:
   - Register a new account or log in.
   - Click the **Profile** button in the header or sidebar to view your account stats or update your name/email/password.
2. **Create a Group**:
   - Go to **Groups**, click **Create Group**, give it a name (e.g., *"Trip to Goa"* or *"Apartment 101"*), and set a monthly budget (e.g., `₹15,000`).
3. **Add Members**:
   - Select the group, open the **Add Members** section, pick a registered user from the dropdown, and add them instantly.
4. **Record Expenses with Different Split Methods**:
   - **Equal Split**: Enter ₹1,200 for Dinner split equally between all members.
   - **Percentage Split**: Enter ₹5,000 for Hotel with custom percentages (e.g., 60% and 40%). Observe real-time ₹ calculations and 100% total validation.
   - **Custom Split**: Enter ₹3,000 with exact ₹ amounts per person. Observe live sum matching validation.
5. **View Balances & Who Owes Whom**:
   - Navigate to **Balances** to see net balances and the simplified settlement plan generated by the cash-flow algorithm.
6. **Check Budget Status & Live Alerts**:
   - Go to **Budgets** to view progress bars and color-coded status badges (Normal, Moderate, High Alert, or Over Budget).
7. **Explore Expense Analytics**:
   - View category breakdown charts, monthly expense bars, and KPI metrics filtered by date range and group.

---

## 📂 Project Directory Structure

```
expense-split-settlement-system/
├── app.py                      # Flask application entry point
├── streamlit_app.py            # Streamlit standalone & cloud web application
├── config.py                   # Central configuration & environment loader
├── db.py                       # MySQL connection pool & schema manager
├── requirements.txt            # Python package dependencies
├── schema.sql                  # MySQL database schema (DDL & constraints)
├── seed.py                     # Demo sample data generator script
├── .env.example                # Environment variables template
├── .env                        # Local database credentials
├── README.md                   # Complete project documentation
├── routes/
│   ├── __init__.py
│   ├── auth_utils.py           # Authentication decorators & CSRF protection
│   ├── auth.py                 # Registration, login, logout, profile update
│   ├── dashboard.py            # Summary dashboard & chart analytics APIs
│   ├── groups.py               # Group management & member roster
│   ├── expenses.py             # Expense recording & split validations
│   ├── balances.py             # Balance calculation & debt simplification
│   └── budgets.py              # Spending budgets & 4-tier alert system
├── templates/
│   ├── base.html               # Master layout with navbar, theme & scripts
│   ├── login.html              # Gradient login page
│   ├── register.html           # Registration page
│   ├── dashboard.html          # Main dashboard with charts & summaries
│   ├── groups.html             # Groups directory & modal
│   ├── group_details.html      # Group details, expenses & balances
│   ├── expenses.html           # Filterable expense list
│   ├── add_expense.html        # Dynamic expense split form
│   ├── edit_expense.html       # Expense editing with split validations
│   ├── balances.html           # Debt simplification settlement view
│   └── budgets.html            # Group budget health monitoring
└── static/
    ├── css/
    │   └── style.css           # Midnight Indigo & Ice Blue theme styles
    └── js/
        ├── theme.js            # Light/Dark mode toggler & persistence
        ├── language.js         # Multi-language dictionary (EN, KN, TE, HI)
        ├── charts.js           # Chart.js analytics graphs
        └── main.js             # Form validation & dynamic split calculations
```

---

## 🛠️ Common Troubleshooting

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `Access denied for user 'root'@'localhost'` | Incorrect MySQL password | Verify `DB_PASSWORD` in `.env` matches your MySQL root password. |
| `Can't connect to MySQL server on 'localhost'` | MySQL service is stopped | Open `services.msc`, find **MySQL80**, and click **Start**. |
| `Unknown database 'expense_split_db'` | Database not initialized | Run `python db.py init` in terminal to create the database schema. |
| `Execution of scripts is disabled on this system` | Windows PowerShell execution policy | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` in PowerShell. |
| Port 5000 already in use | Previous Flask process still running | Run `Stop-Process -Name python -Force` in PowerShell, then restart. |

---

## 🎯 Future Roadmap (Phase 2)

- [ ] UPI Deep-Linking & Instant QR Code Payment Settlement
- [ ] OCR Optical Bill & Receipt Scanning
- [ ] AI-Powered Automated Expense Categorization
- [ ] Multi-Currency Support with Real-Time Exchange Rates
- [ ] Automated Email / SMS Reminders for Pending Settlements
