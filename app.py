from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///order_analysis.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    province = db.Column(db.String(50))
    city = db.Column(db.String(50))
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    
class CustomerOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    product = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))

# China provincial coordinates for map visualization
CHINA_PROVINCES = {
    'Beijing': [39.9042, 116.4074],
    'Shanghai': [31.2304, 121.4737],
    'Guangdong': [23.1291, 113.2644],
    'Jiangsu': [32.0603, 118.7969],
    'Zhejiang': [30.2741, 120.1551],
    'Hubei': [30.5844, 114.2986],
    'Shaanxi': [34.3416, 108.9398],
    'Sichuan': [30.5728, 104.0668],
    'Henan': [34.7580, 113.6494],
    'Hunan': [28.1127, 112.9838],
    'Shandong': [36.6512, 117.1201],
    'Fujian': [26.0789, 119.2965],
    'Anhui': [31.8612, 117.2849],
    'Heilongjiang': [45.7560, 126.6422],
    'Liaoning': [41.7968, 123.4292],
    'Jilin': [43.8868, 125.3245],
    'Hebei': [38.0428, 114.5149],
    'Shanxi': [37.8735, 112.5624],
    'Hainan': [20.0174, 110.3492],
    'Gansu': [36.0611, 103.8343],
    'Guizhou': [26.6470, 106.6302],
    'Yunnan': [25.0456, 102.7100],
    'Qinghai': [36.6232, 101.7788],
    'Ningxia': [38.4680, 106.2735],
    'Xinjiang': [43.7930, 87.6271],
    'Tibet': [29.6469, 91.1172],
    'Inner Mongolia': [40.8175, 111.6708],
    'Guangxi': [22.8176, 108.3669],
    'Jiangxi': [28.6765, 115.8922],
    'Chongqing': [29.5630, 106.5516],
    'Unknown': [35.8617, 104.1954]  # Center of China as fallback
}

def load_data():
    """Load customer and order data from CSV files"""
    try:
        # Load customer data with manual parsing to handle embedded commas
        import csv
        
        customer_data = []
        with open('customer data.txt', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Read header row
            
            for row in reader:
                # Handle the address field which contains commas
                # The first 6 fields should be separate, the rest is address
                if len(row) >= 7:
                    customer_row = {
                        'customer_id': row[0],
                        'name': row[1],
                        'dob': row[2],
                        'province': row[3],
                        'city': row[4],
                        'email': row[5],
                        'address': ', '.join(row[6:])  # Combine remaining fields as address
                    }
                    customer_data.append(customer_row)
        
        customer_df = pd.DataFrame(customer_data)
        
        # Debug: print the first few rows to see what's being loaded
        print("Customer data sample:")
        print(customer_df.head())
        
        # Check if columns are correctly loaded
        print(f"Columns: {list(customer_df.columns)}")
        
        customer_df['dob'] = pd.to_datetime(customer_df['dob'], format='%Y-%m-%d', errors='coerce')
        # Fill missing province values with 'Unknown'
        customer_df['province'] = customer_df['province'].fillna('Unknown')
        
        print(f"Loaded {len(customer_df)} customers, valid DOBs: {customer_df['dob'].notna().sum()}")
        
        # Load order data (should be simpler since no embedded commas)
        order_df = pd.read_csv('order data.txt')
        order_df['order_date'] = pd.to_datetime(order_df['order_date'], format='%Y-%m-%d', errors='coerce')
        
        print(f"Loaded {len(order_df)} orders, valid dates: {order_df['order_date'].notna().sum()}")
        
        return customer_df, order_df
    except Exception as e:
        print(f"Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def init_database():
    """Initialize database with customer and order data"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        customer_df, order_df = load_data()
        
        if customer_df is not None:
            for _, row in customer_df.iterrows():
                if pd.notna(row['dob']):  # Only add valid rows
                    customer = Customer(
                        customer_id=int(row['customer_id']),
                        name=row['name'],
                        dob=row['dob'],
                        province=row['province'],
                        city=row['city'],
                        email=row['email'],
                        address=row['address']
                    )
                    db.session.add(customer)
        
        if order_df is not None:
            for _, row in order_df.iterrows():
                if pd.notna(row['order_date']):  # Only add valid rows
                    order = CustomerOrder(
                        order_id=int(row['order_id']),
                        customer_id=int(row['customer_id']),
                        order_date=row['order_date'],
                        product=row['product'],
                        quantity=int(row['quantity']),
                        amount=float(row['amount']),
                        status=row['status']
                    )
                    db.session.add(order)
        
        db.session.commit()
        print(f"Database initialized successfully! Added {Customer.query.count()} customers and {CustomerOrder.query.count()} orders.")

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/summary')
def get_summary():
    """API endpoint for summary statistics"""
    with app.app_context():
        # Customer statistics
        total_customers = Customer.query.count()
        
        # Order statistics
        total_orders = CustomerOrder.query.count()
        total_revenue = db.session.query(db.func.sum(CustomerOrder.amount)).scalar() or 0
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Order status distribution
        status_counts = db.session.query(CustomerOrder.status, db.func.count(CustomerOrder.id)).group_by(CustomerOrder.status).all()
        status_distribution = {status: count for status, count in status_counts}
        
        # Product performance
        product_stats = db.session.query(
            CustomerOrder.product, 
            db.func.count(CustomerOrder.id).label('order_count'),
            db.func.sum(CustomerOrder.amount).label('total_revenue'),
            db.func.avg(CustomerOrder.amount).label('avg_revenue')
        ).group_by(CustomerOrder.product).all()
        
        return jsonify({
            'customers': {
                'total': total_customers
            },
            'orders': {
                'total': total_orders,
                'total_revenue': round(total_revenue, 2),
                'avg_order_value': round(avg_order_value, 2),
                'status_distribution': status_distribution
            },
            'products': [
                {
                    'product': product,
                    'order_count': count,
                    'total_revenue': round(revenue, 2),
                    'avg_revenue': round(avg_revenue, 2)
                } for product, count, revenue, avg_revenue in product_stats
            ]
        })

@app.route('/api/map-data')
def get_map_data():
    """API endpoint for China map data"""
    with app.app_context():
        # Group orders by province and calculate total order amount
        province_data = db.session.query(
            Customer.province, 
            db.func.sum(CustomerOrder.amount).label('total_amount')
        ).join(CustomerOrder, Customer.customer_id == CustomerOrder.customer_id) \
        .filter(Customer.province.isnot(None)) \
        .group_by(Customer.province).all()
        
        province_orders = []
        for province, amount in province_data:
            if province in CHINA_PROVINCES:
                lat, lon = CHINA_PROVINCES[province]
                province_orders.append({
                    'province': province,
                    'total_amount': float(amount),
                    'lat': lat,
                    'lon': lon
                })
        
        return jsonify(province_orders)

@app.route('/api/charts')
def get_charts():
    """API endpoint for chart data"""
    with app.app_context():
        # Monthly revenue trend
        monthly_revenue = db.session.query(
            db.func.strftime('%Y-%m', CustomerOrder.order_date).label('month'),
            db.func.sum(CustomerOrder.amount).label('revenue')
        ).group_by('month').order_by('month').all()
        
        # Customer age distribution
        customers = Customer.query.all()
        age_groups = {'18-25': 0, '26-35': 0, '36-45': 0, '46+': 0}
        
        for customer in customers:
            age = (datetime.now().date() - customer.dob).days // 365
            if age <= 25:
                age_groups['18-25'] += 1
            elif age <= 35:
                age_groups['26-35'] += 1
            elif age <= 45:
                age_groups['36-45'] += 1
            else:
                age_groups['46+'] += 1
        
        return jsonify({
            'monthly_revenue': [{'month': month, 'revenue': float(revenue)} for month, revenue in monthly_revenue],
            'age_distribution': age_groups
        })

if __name__ == '__main__':
    # Initialize database on first run or if force reinitialization is needed
    db_path = 'order_analysis.db'
    if not os.path.exists(db_path):
        print("Creating new database...")
        init_database()
    else:
        # Check if database needs to be reinitialized (e.g., if empty)
        with app.app_context():
            customer_count = Customer.query.count()
            order_count = CustomerOrder.query.count()
            print(f"Database exists with {customer_count} customers and {order_count} orders")
            
            if customer_count == 0 and order_count == 0:
                print("Database is empty, reinitializing...")
                init_database()
    
    # Run on port 8004 since 8000, 8001, 8002, and 8003 are in use
    app.run(debug=True, host='0.0.0.0', port=8004)