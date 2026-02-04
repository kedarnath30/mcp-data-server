import sqlite3
import pandas as pd
import os

def export_verizon_to_powerbi():
    """Export Verizon data to Power BI format"""
    
    conn = sqlite3.connect('data/verizon_mobile.db')
    output_file = 'powerbi_exports/verizon_mobile_dashboard.xlsx'
    
    print("📱 Exporting Verizon Mobile data to Power BI...")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Export each table
        tables = ['customers', 'monthly_usage', 'network_performance', 'plans']
        
        for table in tables:
            df = pd.read_sql(f"SELECT * FROM {table}", conn)
            df.to_excel(writer, sheet_name=table, index=False)
            print(f"   ✅ {table}: {len(df)} rows")
    
    conn.close()
    print(f"\n✅ Export complete: {output_file}")
    print("🎨 Ready to build your dashboard in Power BI!")

if __name__ == "__main__":
    export_verizon_to_powerbi()