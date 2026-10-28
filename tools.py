import sqlite3
from typing import Dict, Any
from langchain_core.tools import tool

DB_PATH = "enterprise_data.db"

@tool
def get_db_schema() -> str:
    """
    Returns the schema of all tables in the enterprise database.
    Use this to inspect table structures, column names, and data types before writing SQL.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return "\n\n".join([table[0] for table in tables if table[0]])

@tool
def execute_sql_query(query: str) -> Dict[str, Any]:
    """
    Executes a read-only SQL SELECT query against the enterprise database.
    Returns column names and fetched data rows, or an error message if invalid.
    """
    # Safety guardrail: Prevent accidental data modifications (Responsible AI practice)
    forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    if any(keyword in query.upper() for keyword in forbidden_keywords):
        return {
            "status": "error",
            "message": "Query rejected by security guardrail: Only SELECT queries are permitted."
        }

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        conn.close()
        return {
            "status": "success",
            "columns": columns,
            "data": rows,
            "row_count": len(rows)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"SQL Execution Error: {str(e)}"
        }