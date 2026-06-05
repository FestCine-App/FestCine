import pg8000.native
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": "festcine", # Connect to festcine db

    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

print("Testing database connection to 'postgres' using config:")
print("Host:", DB_CONFIG["host"])
print("Port:", DB_CONFIG["port"])
print("Database:", DB_CONFIG["database"])
print("User:", DB_CONFIG["user"])
print("Password length:", len(DB_CONFIG["password"]) if DB_CONFIG["password"] else 0)

try:
    conn = pg8000.native.Connection(**DB_CONFIG)
    print("Database connection to 'postgres' SUCCESSFUL!")
    
    print("\nListing Tables:")
    tables = conn.run("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name")
    for t in tables:
        print(f" - {t[0]}")
        
    print("\nListing Views:")
    views = conn.run("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'VIEW' ORDER BY table_name")
    for v in views:
        print(f" - {v[0]}")
        
    print("\nListing Procedures/Functions:")
    procs = conn.run("""
        SELECT p.proname, pg_catalog.pg_get_function_identity_arguments(p.oid)
        FROM pg_catalog.pg_proc p
        JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname = 'public'
        ORDER BY p.proname
    """)
    for p in procs:
        print(f" - {p[0]}({p[1]})")

        
    conn.close()
except Exception as e:
    print("Database connection to 'postgres' FAILED:", e)
