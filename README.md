# Expense Split and Settlement System
**B.Tech Major Project Review Edition**

A modern, responsive, and fully functional web application designed to track shared group expenses, monitor real-time group budgets, simplify peer-to-peer debt settlements using optimal cash-flow algorithms, and simulate hypothetical expense scenarios.

---

## 🚀 Key Features Implemented (Phase 1 / 50% Milestone)

1. **User Authentication & Session Management**:
   - Secure user registration, login, and logout using Werkzeug PBKDF2 password hashing.
   - Show/hide password toggle for smooth user experience.
   - Session-based authorization preventing unauthorized data access.

2. **Group Management**:
   - Create groups with names and descriptions.
   - Invite existing registered users to groups by email address.
   - Role management (Group Creator / Member).

3. **Expense Tracking & Advanced Split Methods**:
   - **Equal Split**: Even division among selected members with exact fractional remainder adjustment.
   - **Percentage Split**: Custom percentage assignment per member with strict 100% total validation.
   - **Custom Split**: Exact rupee amount assignment with sum validation matching expense total.
   - Category assignment, payer attribution, and complete edit/delete workflows.

4. **Optimal Debt Simplification ("Who Owes Whom")**:
   - Automatic calculation of Net Balance = Total Paid - Total Share.
   - Debt settlement algorithm reducing circular transactions into minimal direct repayments (e.g., *Alice owes Bob ₹300*).

5. **Group Spending Budgets & 4-Tier Automated Warnings**:
   - Set and adjust monthly spending budgets per group.
   - Real-time warning triggers:
     - **Normal**: `< 75%`
     - **Warning**: `75% - 89.9%`
     - **High Spending Alert**: `90% - 99.9%`
     - **Budget Exceeded**: `100%+`

6. **What-If Expense Simulator**:
   - Test potential purchases and hypothetical splits without altering database records.
   - Visual before-and-after spending projections, remaining budget impact, and warning levels.
   - Optional 1-click **Confirm and Add Expense** confirmation button.

7. **Interactive Visualizations (Chart.js)**:
   - Monthly Spending Trend (Line Chart).
   - Expense Category Breakdown (Doughnut Chart).
   - Group-wise Spending Comparison (Bar Chart).
   - Budget vs Spent Tracking (Bar Chart).

8. **Modern Purple-and-White Theme & Dark Mode**:
   - Purple gradient authentication views and crisp white cards.
   - Instant Dark/Light mode toggle stored in `localStorage`.
   - Adaptive Chart.js color palette for seamless dark theme contrast.

9. **Multi-Language Accessibility**:
   - Instant 1-click translation dictionary supporting **English**, **Kannada (ಕನ್ನಡ)**, **Telugu (తెలుగు)**, and **Hindi (हिन्दी)**.
   - Persists selected language across page reloads.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Chart.js, FontAwesome 6
- **Backend**: Python 3.10+ / Flask Framework
- **Database**: MySQL 8.0 / PyMySQL driver
- **Security**: PBKDF2:SHA256 password hashing, CSRF session tokens, parameterized SQL queries

---

## 📋 Required Software

Before setting up, ensure the following are installed on your Windows machine:
1. **Python 3.10 or newer** (with `pip` and "Add python.exe to PATH" checked during install).
2. **MySQL Server 8.0** (or MySQL Community / XAMPP).
3. **Visual Studio Code (VS Code)**.

---

## 💻 Step-by-Step Setup Guide on Windows

### Step 1: Open the Project in VS Code
1. Open VS Code.
2. Click **File** > **Open Folder...**
3. Select `expense-split-settlement-system` located at:
   ```
   c:\Users\akula\OneDrive\Desktop\Rajasree_DES\expense-split-settlement-system
   ```
4. Open a PowerShell terminal in VS Code using the shortcut:
   `Ctrl + ~` (or **Terminal** > **New Terminal**).

---

### Step 2: Create & Activate Python Virtual Environment
Run the following commands in the VS Code terminal:

```powershell
# Create the virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
```
*(You will see `(venv)` appear on the left of your terminal prompt).*

> **Tip for Execution Policy Error**: If Windows blocks running scripts, run this one-time command in PowerShell as Administrator:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

### Step 3: Install Required Dependencies
Install all required libraries using `requirements.txt`:

```powershell
pip install -r requirements.txt
```

---

### Step 4: Configure MySQL Credentials in `.env`
1. Locate the `.env` file in the project folder (or copy `.env.example` to `.env`):
   ```powershell
   Copy-Item .env.example .env
   ```
2. Open `.env` in VS Code and enter your MySQL root password:
   ```env
   SECRET_KEY=btech-expense-split-secret-key-2026

   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_actual_mysql_password
   DB_NAME=expense_split_db
   ```
3. Save the file (`Ctrl + S`).

---

### Step 5: Initialize the MySQL Database & Schema
Run the database initializer script to automatically create `expense_split_db` and all tables:

```powershell
python db.py init
```

*Expected output:*
```
Connecting to MySQL on localhost:3306 as 'root'...
Database 'expense_split_db' initialized successfully.
Schema initialized successfully!
```

---

### Step 6 (Optional): Populate Realistic Sample Data for Demo
To instantly showcase a rich dashboard, live charts, multi-member groups, and settlement recommendations during your project review, run the included seed script:

```powershell
python seed.py
```

*This creates 4 sample test accounts with password `password123`:*
- `rahul@example.com`
- `priya@example.com`
- `amit@example.com`
- `sneha@example.com`

---

### Step 7: Start the Flask Application
Run the Flask server:

```powershell
python app.py
```

*Expected output:*
```
Starting Expense Split and Settlement System on http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

### Step 8: Access the Website in Your Browser
Open your browser and visit:
👉 **`http://127.0.0.1:5000`**

---

## 🧪 Testing the Main Features

1. **Test Registration & Login**:
   - Register a new account with your name, email, and password.
   - Click the eye icon to verify show/hide password toggle.
2. **Test Group Creation**:
   - Click **Create Group** and name it (e.g., "Apartment 202"). Set a monthly budget of ₹10,000.
3. **Add Group Members**:
   - In group details, add a friend's registered email.
4. **Test Split Methods**:
   - **Equal Split**: Add ₹1,200 dinner split equally between members.
   - **Percentage Split**: Add a ₹5,000 rent payment (60% / 40%).
   - **Custom Split**: Add ₹3,000 utility payment with custom amounts.
5. **Verify Balances & Settlements**:
   - Go to **Balances** to view "Who Owes Whom" settlement instructions.
6. **Test Budget Warnings**:
   - Add expenses until group spending crosses 75%, 90%, and 100% of the budget.
   - Verify the color-coded alerts on the Dashboard and Group page.
7. **Test What-If Expense Simulator**:
   - Go to **Simulator**, enter a proposed expense of ₹4,000, and click **Run Simulation**.
   - Notice the before-and-after comparison without database modification.
   - Click **Confirm & Add Expense** to finalize.
8. **Test Dark/Light Mode & Languages**:
   - Click the moon/sun button in the top navigation.
   - Change the language dropdown to **ಕನ್ನಡ**, **తెలుగు**, or **हिन्दी**.

---

## 🛠️ Common Errors & Troubleshooting

| Error | Root Cause | Solution |
| :--- | :--- | :--- |
| `Access denied for user 'root'@'localhost'` | Incorrect MySQL password in `.env` | Open `.env` and verify `DB_PASSWORD=...` matches your MySQL root password. |
| `Can't connect to MySQL server on 'localhost'` | MySQL service is not running | Open Windows Services (`services.msc`), find **MySQL80**, and click **Start**. |
| `Unknown database 'expense_split_db'` | Database not created yet | Run `python db.py init` to automatically create database and schema. |
| `Execution of scripts is disabled on this system` | Windows PowerShell execution policy | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` in PowerShell. |

---

## 📂 Project Directory Structure

```
expense-split-settlement-system/
├── app.py                      # Main Flask application entry point
├── config.py                   # Central configuration & environment loader
├── db.py                       # MySQL connection pool & schema runner
├── requirements.txt            # Python dependencies
├── schema.sql                  # MySQL database schema with indexes & FKs
├── seed.py                     # Optional demo sample data generator
├── .env.example                # Example environment variables template
├── .env                        # Local database credentials
├── README.md                   # Complete documentation & guide
├── routes/
│   ├── __init__.py
│   ├── auth_utils.py           # Login decorator & CSRF verification
│   ├── auth.py                 # Registration, login, logout
│   ├── dashboard.py            # Overview metrics & chart data API
│   ├── groups.py               # Group CRUD & membership
│   ├── expenses.py             # Expense management & split calculations
│   ├── balances.py             # Balance calculations & Who Owes Whom
│   ├── budgets.py              # Spending limits & 4-tier alert monitoring
│   └── simulator.py            # What-If hypothetical expense simulator
├── templates/
│   ├── base.html               # Base layout with navbar, theme & lang toggles
│   ├── login.html              # Modern gradient login page
│   ├── register.html           # Modern gradient registration page
│   ├── dashboard.html          # Interactive dashboard with Chart.js
│   ├── groups.html             # Groups directory & creation modal
│   ├── group_details.html      # Group details, expenses & member balances
│   ├── expenses.html           # Filterable expense list
│   ├── add_expense.html        # Dynamic expense split form
│   ├── edit_expense.html       # Expense editor
│   ├── balances.html           # Who Owes Whom settlement page
│   ├── budgets.html            # Group budget health page
│   └── simulator.html          # What-If simulator interface
└── static/
    ├── css/
    │   └── style.css           # Purple & white theme / dark mode styling
    └── js/
        ├── theme.js            # Light/Dark mode manager & persistence
        ├── language.js         # Multi-language dictionary (EN, KN, TE, HI)
        ├── charts.js           # Live Chart.js graphs
        └── main.js             # Form validation & simulator controller
```

---

## 🎯 Features Reserved for Future Milestones (Next 50%)

- Email / SMS OTP Verification & Password Recovery
- UPI & QR Code Payment Gateway Settlement Integration
- OCR Bill & Receipt Scanning
- AI-based Auto-categorization
- Multi-currency Conversion
- Push Notifications & SMS Reminders
