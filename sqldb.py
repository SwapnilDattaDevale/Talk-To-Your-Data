import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables from your .env file
load_dotenv()

def execute_query(query):
    # Fetch Azure credentials securely
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_DATABASE")
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    
    # Update connection parameters for Azure SQL Server
    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    
    # pyodbc contexts handle closing connection/cursor automatically
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            
            # Fetch actions only run if the query returns rows (e.g., SELECT)
            if cur.description:
                rows = [list(row) for row in cur.fetchall()] # Convert pyodbc Row objects to lists
                columns = [desc[0] for desc in cur.description]
                return columns, rows
            return [], []

def get_schema(table_name):
    # SQL Server uses 'dbo' as the default schema instead of 'public'
    query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'dbo'
          AND table_name = '{table_name}'"""
    schema = execute_query(query)
    return schema

# Example usage:
#result = get_schema("orders")
#print(result)