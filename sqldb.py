import pyodbc

def execute_query(query):
    # Update connection parameters for SQL Server
    connection_string = (
        
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-QATNOPD\SQLEXPRESS;"
        "DATABASE=namastesql;"
        "Trusted_Connection=yes;"  # Use Windows Authentication
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
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
