import os
from decimal import Decimal
import pymysql
from flask import Flask, render_template, session
from config import Config
from db import close_db
from routes.auth_utils import generate_csrf_token

# Import blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.groups import groups_bp
from routes.expenses import expenses_bp
from routes.balances import balances_bp
from routes.budgets import budgets_bp
from routes.simulator import simulator_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(balances_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(simulator_bp)

    # Close database connection on context teardown
    app.teardown_appcontext(close_db)

    # Context processors for global template variables
    @app.context_processor
    def inject_global_data():
        return {
            'csrf_token': generate_csrf_token(),
            'current_user': {
                'id': session.get('user_id'),
                'name': session.get('user_name'),
                'email': session.get('user_email')
            } if 'user_id' in session else None
        }

    # Custom Jinja template filters
    @app.template_filter('currency')
    def currency_filter(val):
        try:
            num = Decimal(str(val or 0))
            return f"₹{num:,.2f}"
        except Exception:
            return f"₹0.00"

    @app.template_filter('date_format')
    def date_filter(val):
        if not val:
            return ""
        try:
            return str(val)
        except Exception:
            return str(val)

    # Friendly error handlers
    @app.errorhandler(pymysql.MySQLError)
    def handle_mysql_error(e):
        return render_template(
            'base.html',
            error_title="MySQL Configuration Required",
            error_message=f"Could not connect to MySQL: {str(e)}. Please configure your MySQL password in the .env file and run 'python db.py init'."
        ), 500

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_title="404 - Page Not Found", error_message="The requested page could not be found."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_title="500 - Server Error", error_message="An unexpected server error occurred. Please verify your MySQL credentials in .env."), 500

    return app

app = create_app()

if __name__ == '__main__':
    from db import check_db_connection
    success, msg = check_db_connection()
    if not success:
        print("\n" + "="*70)
        print(" [!] DATABASE CONFIGURATION NOTICE:")
        print(f" MySQL is running, but requires authentication: {msg}")
        print(" --> Please open '.env' in this directory and enter your MySQL password:")
        print("     DB_PASSWORD=your_actual_password")
        print(" --> Then run: python db.py init")
        print("="*70 + "\n")
    else:
        print(" [*] MySQL Database connection verified successfully.")

    # Run development server
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Expense Split and Settlement System on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=True)
