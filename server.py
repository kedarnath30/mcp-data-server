import asyncio
import json
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from database import DatabaseManager
from powerbi_export import PowerBIExporter
from nl_to_sql import NaturalLanguageQueryEngine
import pandas as pd

# Initialize the MCP server
app = Server("business-data-server")
db = DatabaseManager()
pbi_exporter = PowerBIExporter()

# Initialize natural language query engine
try:
    nl_engine = NaturalLanguageQueryEngine()
    nl_enabled = True
    print("✅ Natural language queries enabled")
except ValueError as e:
    nl_engine = None
    nl_enabled = False
    print(f"⚠️  Natural language queries disabled: {e}")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    Define the tools (functions) that Claude can call
    """
    tools_list = [
        Tool(
            name="query_database",
            description=(
                "Execute SQL SELECT queries against the business database. "
                "Database contains tables: customers, sales, products, pipeline. "
                "Automatically limits results to prevent overwhelming responses. "
                "Use this to answer questions about business metrics, sales data, customer info."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    },
                    "max_rows": {
                        "type": "integer",
                        "description": "Maximum number of rows to return (default: 100)",
                        "default": 100
                    }
                },
                "required": ["sql_query"]
            }
        ),
        
        Tool(
            name="get_database_schema",
            description=(
                "Retrieve the complete database schema showing all tables, columns, "
                "data types, and row counts. Use this first to understand what data is available "
                "before writing queries."
            ),
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        Tool(
            name="get_table_sample",
            description=(
                "Get sample rows from a specific table to understand the data format. "
                "Useful for exploring data before writing complex queries."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to sample"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of sample rows (default: 5)",
                        "default": 5
                    }
                },
                "required": ["table_name"]
            }
        ),
        
        Tool(
            name="analyze_csv",
            description=(
                "Load and analyze CSV files from the data directory. "
                "Provides summary statistics, data types, and sample data. "
                "Available files: sales_export.csv, customers_export.csv"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "CSV filename (e.g., 'sales_export.csv')"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["summary", "head", "describe", "columns"],
                        "description": "Type of analysis to perform"
                    },
                    "rows": {
                        "type": "integer",
                        "description": "Number of rows for 'head' operation (default: 10)",
                        "default": 10
                    }
                },
                "required": ["filename", "operation"]
            }
        ),
        
        Tool(
            name="export_to_powerbi",
            description=(
                "Export SQL query results to Excel format for Power BI. "
                "Creates formatted Excel file with proper column widths. "
                "Perfect for creating Power BI data sources."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "SQL SELECT query to export"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename (optional)"
                    }
                },
                "required": ["sql_query"]
            }
        ),
        
        Tool(
            name="create_powerbi_dataset",
            description=(
                "Export all database tables to a single Excel file with multiple sheets. "
                "Creates a complete dataset ready to import into Power BI. "
                "Each table becomes a separate sheet."
            ),
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    
    # Add natural language tool if enabled
    if nl_enabled:
        tools_list.append(
            Tool(
                name="ask_question",
                description=(
                    "🤖 Ask questions about your data in NATURAL LANGUAGE! "
                    "Claude will automatically convert your question to SQL and execute it. "
                    "Examples: 'What's our total revenue?', 'Show top 5 customers', "
                    "'Which sales rep performs best?', 'What's our revenue by region?'"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Natural language question about the data"
                        },
                        "max_rows": {
                            "type": "integer",
                            "description": "Maximum rows to return (default: 50)",
                            "default": 50
                        }
                    },
                    "required": ["question"]
                }
            )
        )
    
    return tools_list

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool calls from Claude
    """
    
    if name == "query_database":
        sql_query = arguments.get("sql_query", "")
        max_rows = arguments.get("max_rows", 100)
        
        result = db.execute_query(sql_query, max_rows)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    elif name == "get_database_schema":
        schema = db.get_schema_info()
        
        return [TextContent(
            type="text",
            text=json.dumps(schema, indent=2)
        )]
    
    elif name == "get_table_sample":
        table_name = arguments.get("table_name")
        limit = arguments.get("limit", 5)
        
        result = db.get_sample_data(table_name, limit)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    elif name == "analyze_csv":
        filename = arguments.get("filename")
        operation = arguments.get("operation")
        rows = arguments.get("rows", 10)
        
        try:
            df = pd.read_csv(f"data/{filename}")
            
            if operation == "summary":
                result = {
                    "filename": filename,
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                    "null_counts": df.isnull().sum().to_dict()
                }
            
            elif operation == "head":
                result = {
                    "filename": filename,
                    "rows": df.head(rows).to_dict('records')
                }
            
            elif operation == "describe":
                result = {
                    "filename": filename,
                    "statistics": df.describe(include='all').to_dict()
                }
            
            elif operation == "columns":
                result = {
                    "filename": filename,
                    "columns": list(df.columns)
                }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": str(e)
                })
            )]
    
    elif name == "export_to_powerbi":
        sql_query = arguments.get("sql_query")
        filename = arguments.get("filename")
        
        result = pbi_exporter.export_query_to_excel(sql_query, filename)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    elif name == "create_powerbi_dataset":
        result = pbi_exporter.create_powerbi_dataset()
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    elif name == "ask_question":
        if not nl_enabled:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Natural language queries are disabled. Please set ANTHROPIC_API_KEY in .env"
                })
            )]
        
        question = arguments.get("question")
        max_rows = arguments.get("max_rows", 50)
        
        result = nl_engine.query(question, max_rows)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"})
        )]

async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())