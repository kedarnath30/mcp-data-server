import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

def create_verizon_mobile_data():
    """Create realistic Verizon mobile customer data"""
    
    conn = sqlite3.connect('data/verizon_mobile.db')
    
    # 1. CUSTOMERS TABLE
    states = ['California', 'Texas', 'Florida', 'New York', 'Pennsylvania', 
              'Illinois', 'Ohio', 'Georgia', 'North Carolina', 'Michigan']
    
    customers = []
    for i in range(1, 501):  # 500 customers
        signup_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 730))
        customers.append({
            'customer_id': f'VZ{i:06d}',
            'state': random.choice(states),
            'plan_type': random.choices(['Unlimited', 'Limited 10GB', 'Limited 5GB', 'Prepaid'], 
                                       weights=[40, 25, 20, 15])[0],
            'signup_date': signup_date.strftime('%Y-%m-%d'),
            'monthly_charge': random.choice([70, 55, 45, 40]),
            'status': random.choices(['Active', 'Churned'], weights=[85, 15])[0],
            'data_usage_gb': round(random.uniform(2, 50), 2),
            'satisfaction_score': random.randint(1, 5)
        })
    
    customers_df = pd.DataFrame(customers)
    
    # 2. MONTHLY USAGE TABLE
    usage_records = []
    base_date = datetime(2024, 1, 1)
    
    for month in range(12):  # 12 months of data
        month_date = base_date + timedelta(days=month * 30)
        for customer in random.sample(customers, 400):  # 400 active customers per month
            usage_records.append({
                'usage_id': f'U{len(usage_records):07d}',
                'customer_id': customer['customer_id'],
                'month': month_date.strftime('%Y-%m'),
                'data_used_gb': round(random.uniform(1, 60), 2),
                'calls_minutes': random.randint(100, 2000),
                'texts_sent': random.randint(500, 5000),
                'revenue': customer['monthly_charge']
            })
    
    usage_df = pd.DataFrame(usage_records)
    
    # 3. NETWORK PERFORMANCE TABLE
    network_data = []
    for state in states:
        network_data.append({
            'state': state,
            'coverage_percent': round(random.uniform(92, 99.5), 1),
            'avg_download_mbps': round(random.uniform(50, 150), 1),
            'avg_upload_mbps': round(random.uniform(10, 50), 1),
            'network_satisfaction': round(random.uniform(3.5, 5.0), 1)
        })
    
    network_df = pd.DataFrame(network_data)
    
    # 4. PLANS TABLE
    plans = pd.DataFrame({
        'plan_name': ['Unlimited', 'Limited 10GB', 'Limited 5GB', 'Prepaid'],
        'monthly_price': [70, 55, 45, 40],
        'data_limit_gb': [999, 10, 5, 3],
        'features': ['Unlimited Talk/Text/Data', 'Talk/Text + 10GB', 'Talk/Text + 5GB', 'Pay As You Go']
    })
    
    # Save all tables
    customers_df.to_sql('customers', conn, if_exists='replace', index=False)
    usage_df.to_sql('monthly_usage', conn, if_exists='replace', index=False)
    network_df.to_sql('network_performance', conn, if_exists='replace', index=False)
    plans.to_sql('plans', conn, if_exists='replace', index=False)
    
    # Also create CSV exports for Power BI
    customers_df.to_csv('data/verizon_customers.csv', index=False)
    usage_df.to_csv('data/verizon_usage.csv', index=False)
    network_df.to_csv('data/verizon_network.csv', index=False)
    
    print("✅ Verizon Mobile database created successfully!")
    print(f"   - {len(customers_df)} customers")
    print(f"   - {len(usage_df)} monthly usage records")
    print(f"   - {len(network_df)} network performance records")
    print(f"   - {len(plans)} plans")
    print("\n📊 Database location: data/verizon_mobile.db")
    print("📁 CSV exports: data/verizon_*.csv")
    
    # Print some stats
    print(f"\n📈 Quick Stats:")
    print(f"   - Active Customers: {len(customers_df[customers_df['status'] == 'Active'])}")
    print(f"   - Churned Customers: {len(customers_df[customers_df['status'] == 'Churned'])}")
    print(f"   - Total Monthly Revenue: ${customers_df[customers_df['status'] == 'Active']['monthly_charge'].sum():,}")
    print(f"   - Avg Data Usage: {customers_df['data_usage_gb'].mean():.2f} GB")
    
    conn.close()

if __name__ == "__main__":
    create_verizon_mobile_data()