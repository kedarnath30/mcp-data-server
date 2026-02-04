import sqlite3
import random
from datetime import datetime

conn = sqlite3.connect('data/business.db')
cursor = conn.cursor()

# Add 10 new sales
for i in range(10):
    quantity = random.randint(1, 20)
    unit_price = random.choice([99, 199, 299, 499, 999])
    revenue = quantity * unit_price
    
    cursor.execute("""
        INSERT INTO sales (sale_id, customer_id, product, sale_date, quantity, unit_price, revenue, sales_rep)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        f'S{99990+i}',
        f'C{random.randint(1, 50):04d}',
        random.choice(['Product A', 'Product B', 'Product C', 'Product D']),
        datetime.now().strftime('%Y-%m-%d'),
        quantity,
        unit_price,
        revenue,
        random.choice(['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Lee', 'Emma Wilson'])
    ))

conn.commit()
conn.close()
print("✅ Added 10 new sales to database!")
print("📊 Run 'python refresh_powerbi.py' to export updated data")