import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

def create_sample_database():
    """Create a realistic business database for demo purposes"""
    
    conn = sqlite3.connect('data/business.db')
    
    # 1. CUSTOMERS TABLE
    customers = pd.DataFrame({
        'customer_id': [f'C{i:04d}' for i in range(1, 51)],
        'company_name': [f'Company {chr(65 + i % 26)}{i}' for i in range(1, 51)],
        'industry': random.choices(['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing'], k=50),
        'region': random.choices(['North America', 'Europe', 'Asia Pacific', 'Latin America'], k=50),
        'tier': random.choices(['Enterprise', 'Mid-Market', 'SMB'], weights=[15, 35, 50], k=50),
        'lifetime_value': [random.randint(50000, 500000) for _ in range(50)]
    })
    
    # 2. SALES TABLE
    sales_records = []
    base_date = datetime(2024, 1, 1)
    
    for i in range(1, 201):
        sales_records.append({
            'sale_id': f'S{i:05d}',
            'customer_id': f'C{random.randint(1, 50):04d}',
            'product': random.choice(['Product A', 'Product B', 'Product C', 'Product D']),
            'sale_date': (base_date + timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            'quantity': random.randint(1, 20),
            'unit_price': random.choice([99, 199, 299, 499, 999]),
            'revenue': 0,
            'sales_rep': random.choice(['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Lee', 'Emma Wilson'])
        })
    
    sales = pd.DataFrame(sales_records)
    sales['revenue'] = sales['quantity'] * sales['unit_price']
    
    # 3. PRODUCTS TABLE
    products = pd.DataFrame({
        'product_name': ['Product A', 'Product B', 'Product C', 'Product D'],
        'category': ['Software', 'Hardware', 'Services', 'Consulting'],
        'cost': [50, 120, 150, 300],
        'margin_percent': [50, 40, 50, 67],
        'stock_level': [1000, 500, 2000, 100]
    })
    
    # 4. SALES PIPELINE TABLE
    pipeline = pd.DataFrame({
        'opportunity_id': [f'OPP{i:04d}' for i in range(1, 31)],
        'customer_id': [f'C{random.randint(1, 50):04d}' for _ in range(30)],
        'stage': random.choices(['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won'], 
                               weights=[20, 25, 25, 20, 10], k=30),
        'expected_value': [random.randint(10000, 200000) for _ in range(30)],
        'probability': [random.choice([10, 25, 50, 75, 90]) for _ in range(30)],
        'close_date': [(datetime.now() + timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d') for _ in range(30)]
    })
    
    # Save all tables
    customers.to_sql('customers', conn, if_exists='replace', index=False)
    sales.to_sql('sales', conn, if_exists='replace', index=False)
    products.to_sql('products', conn, if_exists='replace', index=False)
    pipeline.to_sql('pipeline', conn, if_exists='replace', index=False)
    
    # Also create CSV exports
    sales.to_csv('data/sales_export.csv', index=False)
    customers.to_csv('data/customers_export.csv', index=False)
    
    print("✅ Sample database created successfully!")
    print(f"   - {len(customers)} customers")
    print(f"   - {len(sales)} sales transactions")
    print(f"   - {len(products)} products")
    print(f"   - {len(pipeline)} pipeline opportunities")
    print("\n📊 Database location: data/business.db")
    
    conn.close()

if __name__ == "__main__":
    create_sample_database()