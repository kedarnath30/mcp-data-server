import os
from anthropic import Anthropic
from database import DatabaseManager

class NaturalLanguageQueryEngine:
    """Converts natural language questions to SQL using Claude"""
    
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=api_key)
        self.db = DatabaseManager()
        
    def query(self, question: str, max_rows: int = 50):
        """
        Convert natural language question to SQL and execute it
        
        Args:
            question: Natural language question about the data
            max_rows: Maximum rows to return
            
        Returns:
            dict with SQL query, results, and explanation
        """
        
        # Step 1: Get database schema
        schema = self.db.get_schema_info()
        
        if not schema['success']:
            return {
                'success': False,
                'error': 'Failed to retrieve database schema'
            }
        
        # Step 2: Build schema description for Claude
        schema_description = self._format_schema(schema['tables'])
        
        # Step 3: Create prompt for Claude
        prompt = f"""You are a SQL expert. Convert the following natural language question into a SQL query.

DATABASE SCHEMA:
{schema_description}

IMPORTANT RULES:
1. Generate ONLY a SELECT query (no INSERT, UPDATE, DELETE)
2. Use proper SQL syntax for SQLite
3. Include column aliases for clarity
4. Add ORDER BY when relevant to show most important results first
5. The query should answer the question directly
6. Return ONLY the SQL query, no explanations, no markdown, no code blocks

QUESTION: {question}

SQL Query:"""
        
        try:
            # Step 4: Call Claude API to generate SQL
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract SQL from response
            sql_query = message.content[0].text.strip()
            
            # Clean up any markdown formatting and semicolons
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            sql_query = sql_query.rstrip(';')  # Remove trailing semicolons
            
            # Step 5: Execute the generated SQL
            result = self.db.execute_query(sql_query, max_rows)
            
            if result['success']:
                return {
                    'success': True,
                    'question': question,
                    'generated_sql': sql_query,
                    'data': result['data'],
                    'columns': result['columns'],
                    'row_count': result['row_count'],
                    'explanation': f"Generated and executed SQL query successfully"
                }
            else:
                return {
                    'success': False,
                    'question': question,
                    'generated_sql': sql_query,
                    'error': result['error'],
                    'note': 'SQL was generated but execution failed. The query might need refinement.'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate or execute SQL: {str(e)}'
            }
    
    def _format_schema(self, tables: dict) -> str:
        """Format database schema for Claude's context"""
        schema_lines = []
        
        for table_name, table_info in tables.items():
            schema_lines.append(f"\nTable: {table_name} ({table_info['row_count']} rows)")
            schema_lines.append("Columns:")
            
            for col in table_info['columns']:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                schema_lines.append(f"  - {col['name']} ({col['type']}) {nullable}")
        
        return "\n".join(schema_lines)

# Test the engine
if __name__ == "__main__":
    import json
    
    print("🧠 Natural Language to SQL Test\n")
    
    try:
        engine = NaturalLanguageQueryEngine()
        
        # Test questions
        test_questions = [
            "What's the total revenue by product?",
            "Show me the top 5 customers by lifetime value",
            "Which sales rep has the most sales?",
            "What's our average deal size by region?"
        ]
        
        for question in test_questions:
            print(f"\n{'='*60}")
            print(f"❓ QUESTION: {question}")
            print('='*60)
            
            result = engine.query(question)
            
            if result['success']:
                print(f"✅ Generated SQL: {result['generated_sql']}")
                print(f"📊 Results: {result['row_count']} rows")
                print("\nData preview:")
                for row in result['data'][:3]:  # Show first 3 rows
                    print(f"   {row}")
            else:
                print(f"❌ Error: {result['error']}")
    
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n💡 Make sure ANTHROPIC_API_KEY is set in your .env file")