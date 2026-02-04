from powerbi_export import PowerBIExporter
from datetime import datetime
import json

def refresh_all_exports():
    """
    One-command refresh for all Power BI exports
    Overwrites existing files so Power BI refresh works
    """
    print("🔄 Starting Power BI Data Refresh...")
    print("=" * 60)
    
    exporter = PowerBIExporter()
    results = []
    
    # Export 1: Complete Dataset (FIXED FILENAME)
    print("\n📊 Exporting complete dataset...")
    result = exporter.export_query_to_excel(
        "SELECT * FROM customers", 
        "powerbi_dataset_customers.xlsx"
    )
    
    # Export all tables to one file manually
    import pandas as pd
    from database import DatabaseManager
    import os
    
    db = DatabaseManager()
    dataset_file = os.path.join(exporter.export_dir, 'powerbi_dataset_complete.xlsx')
    
    with pd.ExcelWriter(dataset_file, engine='openpyxl') as writer:
        # Export each table
        for table in ['customers', 'sales', 'products', 'pipeline']:
            result = db.execute_query(f"SELECT * FROM {table}", max_rows=10000)
            if result['success']:
                df = pd.DataFrame(result['data'])
                df.to_excel(writer, sheet_name=table, index=False)
    
    print(f"✅ Success: {dataset_file}")
    
    # Export 2: Sales Summary (FIXED FILENAME)
    print("\n📈 Exporting sales summary...")
    query = """
    SELECT 
        s.sale_date,
        s.product,
        s.sales_rep,
        c.region,
        c.industry,
        c.tier as customer_tier,
        s.quantity,
        s.revenue,
        p.category as product_category,
        p.margin_percent
    FROM sales s
    LEFT JOIN customers c ON s.customer_id = c.customer_id
    LEFT JOIN products p ON s.product = p.product_name
    """
    result = exporter.export_query_to_excel(query, 'sales_summary_powerbi.xlsx')
    if result['success']:
        print(f"✅ Success: {result['filepath']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Export 3: Revenue by Product (FIXED FILENAME)
    print("\n💰 Exporting revenue analysis...")
    query = """
    SELECT 
        product,
        COUNT(*) as sales_count,
        SUM(revenue) as total_revenue,
        AVG(revenue) as avg_revenue,
        MIN(revenue) as min_revenue,
        MAX(revenue) as max_revenue
    FROM sales
    GROUP BY product
    ORDER BY total_revenue DESC
    """
    result = exporter.export_query_to_excel(query, 'revenue_by_product.xlsx')
    if result['success']:
        print(f"✅ Success: {result['filepath']}")
    
    # Export 4: Regional Performance (FIXED FILENAME)
    print("\n🌍 Exporting regional performance...")
    query = """
    SELECT 
        c.region,
        COUNT(DISTINCT s.customer_id) as customer_count,
        COUNT(s.sale_id) as total_sales,
        SUM(s.revenue) as total_revenue,
        AVG(s.revenue) as avg_deal_size
    FROM sales s
    JOIN customers c ON s.customer_id = c.customer_id
    GROUP BY c.region
    ORDER BY total_revenue DESC
    """
    result = exporter.export_query_to_excel(query, 'regional_performance.xlsx')
    if result['success']:
        print(f"✅ Success: {result['filepath']}")
    
    # Export 5: Sales Rep Performance (FIXED FILENAME)
    print("\n👥 Exporting sales rep performance...")
    query = """
    SELECT 
        sales_rep,
        COUNT(*) as deals_closed,
        SUM(revenue) as total_revenue,
        AVG(revenue) as avg_deal_size,
        MAX(revenue) as largest_deal
    FROM sales
    GROUP BY sales_rep
    ORDER BY total_revenue DESC
    """
    result = exporter.export_query_to_excel(query, 'sales_rep_performance.xlsx')
    if result['success']:
        print(f"✅ Success: {result['filepath']}")
    
    print("\n" + "=" * 60)
    print("✅ All exports complete!")
    print("📁 Files location: powerbi_exports/")
    print("🔄 Now click REFRESH in Power BI Desktop to see updated data!")

if __name__ == "__main__":
    refresh_all_exports()