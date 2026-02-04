from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import json

load_dotenv()

class DatabaseManager:
    """Manages database connections and query execution"""
    
    def __init__(self):
        db_type = os.getenv('DB_TYPE', 'sqlite')
        
        if db_type == 'sqlite':
            self.engine = create_engine('sqlite:///data/business.db', echo=False)
        elif db_type == 'postgresql':
            conn_str = os.getenv('POSTGRES_CONNECTION_STRING')
            self.engine = create_engine(conn_str)
        elif db_type == 'mysql':
            conn_str = os.getenv('MYSQL_CONNECTION_STRING')
            self.engine = create_engine(conn_str)
        elif db_type == 'snowflake':
            # For your Snowflake experience!
            from snowflake.sqlalchemy import URL
            self.engine = create_engine(URL(
                account=os.getenv('SNOWFLAKE_ACCOUNT'),
                user=os.getenv('SNOWFLAKE_USER'),
                password=os.getenv('SNOWFLAKE_PASSWORD'),
                database=os.getenv('SNOWFLAKE_DATABASE'),
                warehouse=os.getenv('SNOWFLAKE_WAREHOUSE')
            ))
        
        self.Session = sessionmaker(bind=self.engine)
    
    def execute_query(self, query: str, max_rows: int = 100):
        """
        Execute SQL query safely with automatic row limiting
        
        Args:
            query: SQL SELECT statement
            max_rows: Maximum rows to return (default 100)
        
        Returns:
            dict with success status, columns, rows, and metadata
        """
        try:
            with self.Session() as session:
                # Security: Only SELECT queries allowed
                if not query.strip().upper().startswith('SELECT'):
                    return {
                        'success': False,
                        'error': 'Only SELECT queries are allowed for security'
                    }
                
                # Add LIMIT if not present
                if 'LIMIT' not in query.upper():
                    query = f"{query} LIMIT {max_rows}"
                
                # Execute query
                result = session.execute(text(query))
                columns = list(result.keys())
                rows = result.fetchall()
                
                # Convert to list of dicts for JSON serialization
                data = [dict(zip(columns, row)) for row in rows]
                
                return {
                    'success': True,
                    'columns': columns,
                    'data': data,
                    'row_count': len(data),
                    'query_executed': query
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def get_schema_info(self):
        """
        Get comprehensive database schema information
        
        Returns:
            dict containing all tables, columns, and data types
        """
        try:
            inspector = inspect(self.engine)
            schema_info = {}
            
            for table_name in inspector.get_table_names():
                columns = []
                for column in inspector.get_columns(table_name):
                    columns.append({
                        'name': column['name'],
                        'type': str(column['type']),
                        'nullable': column['nullable']
                    })
                
                # Get sample row count
                with self.Session() as session:
                    count_result = session.execute(
                        text(f"SELECT COUNT(*) as count FROM {table_name}")
                    )
                    row_count = count_result.fetchone()[0]
                
                schema_info[table_name] = {
                    'columns': columns,
                    'row_count': row_count
                }
            
            return {
                'success': True,
                'tables': schema_info,
                'table_count': len(schema_info)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_sample_data(self, table_name: str, limit: int = 5):
        """Get sample rows from a table"""
        try:
            with self.Session() as session:
                result = session.execute(
                    text(f"SELECT * FROM {table_name} LIMIT {limit}")
                )
                columns = list(result.keys())
                rows = result.fetchall()
                
                return {
                    'success': True,
                    'table': table_name,
                    'sample_data': [dict(zip(columns, row)) for row in rows]
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Test the database manager
if __name__ == "__main__":
    db = DatabaseManager()
    
    # Test schema retrieval
    print("📊 Database Schema:")
    schema = db.get_schema_info()
    print(json.dumps(schema, indent=2))
    
    # Test query
    print("\n🔍 Sample Query:")
    result = db.execute_query("SELECT * FROM sales ORDER BY revenue DESC")
    print(f"Found {result['row_count']} rows")
    if result['success']:
        print(f"Top sale: {result['data'][0]}")