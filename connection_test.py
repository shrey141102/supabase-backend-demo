import psycopg2

# Try connecting to Supabase directly
try:
    # Using individual parameters to avoid URL parsing issues
    conn = psycopg2.connect(
        host="aws-0-ap-south-1.pooler.supabase.com",
        port="5432",
        database="postgres",
        user="postgres.abcd",
        password="xyz"
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print(f"Connection successful! Result: {result}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Connection failed: {e}")