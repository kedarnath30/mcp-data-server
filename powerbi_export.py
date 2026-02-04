import pandas as pd
from database import DatabaseManager
from datetime import datetime
import os

class PowerBIExporter:
    """Export database queries to Power BI-ready formats"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.export_dir = 'powerbi_exports'
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_query_to_excel(self, query: str, filename: str = None):
        """
        Execute SQL query and export results to Excel
        
        Args:
            query: SQL SELECT query
            filename: Output filename (auto-generated if not provided)
            
        Returns:
            dict with success status and file path
        """
        try:
            # Execute query (no row limit for exports)
            result = self.db.execute_query(query, max_rows=10000)
            
            if not result['success']:
                return {
                    'success': False,
                    'error': result['error']
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(result['data'])
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"query_export_{timestamp}.xlsx"
            
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            filepath = os.path.join(self.export_dir, filename)
            
            # Export to Excel with formatting
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Data']
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    ) + 2
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
            
            return {
                'success': True,
                'filepath': filepath,
                'rows_exported': len(df),
                'columns': list(df.columns)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_table_to_excel(self, table_name: str, filename: str = None):
        """Export entire table to Excel"""
        query = f"SELECT * FROM {table_name}"
        
        if not filename:
            filename = f"{table_name}_export_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        return self.export_query_to_excel(query, filename)
    
    def create_powerbi_dataset(self):
        """
        Create a complete Power BI dataset with all tables
        
        Returns:
            dict with success status and file paths
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dataset_file = os.path.join(self.export_dir, f'powerbi_dataset_{timestamp}.xlsx')
            
            # Get all tables
            schema = self.db.get_schema_info()
            
            if not schema['success']:
                return {
                    'success': False,
                    'error': 'Failed to retrieve schema'
                }
            
            # Create Excel file with multiple sheets
            with pd.ExcelWriter(dataset_file, engine='openpyxl') as writer:
                for table_name in schema['tables'].keys():
                    result = self.db.execute_query(f"SELECT * FROM {table_name}", max_rows=10000)
                    
                    if result['success']:
                        df = pd.DataFrame(result['data'])
                        df.to_excel(writer, sheet_name=table_name, index=False)
                        
                        # Format worksheet
                        worksheet = writer.sheets[table_name]
                        for idx, col in enumerate(df.columns):
                            max_length = max(
                                df[col].astype(str).apply(len).max(),
                                len(col)
                            ) + 2
                            col_letter = chr(65 + idx) if idx < 26 else chr(65 + idx//26 - 1) + chr(65 + idx%26)
                            worksheet.column_dimensions[col_letter].width = min(max_length, 50)
            
            return {
                'success': True,
                'filepath': dataset_file,
                'tables_exported': list(schema['tables'].keys()),
                'message': 'Complete dataset exported. Ready to import into Power BI.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_sales_summary(self):
        """Export pre-built sales summary for Power BI"""
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
        
        return self.export_query_to_excel(query, 'sales_summary_powerbi.xlsx')

# Test the exporter
if __name__ == "__main__":
    import json
    
    exporter = PowerBIExporter()
    
    print("📊 Power BI Exporter Test\n")
    
    # Test 1: Export full dataset
    print("Creating complete Power BI dataset...")
    result = exporter.create_powerbi_dataset()
    print(json.dumps(result, indent=2))
    
    # Test 2: Export sales summary
    print("\n\nCreating sales summary...")
    result = exporter.export_sales_summary()
    print(json.dumps(result, indent=2))
    
    print("\n✅ Exports complete! Check the 'powerbi_exports' folder.")