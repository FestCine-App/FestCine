import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'festcine_backend.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT routine_name, routine_type 
        FROM information_schema.routines 
        WHERE specific_schema = 'public' AND routine_type IN ('PROCEDURE', 'FUNCTION');
    """)
    print("ROUTINES:")
    for row in cursor.fetchall():
        print(f"- {row[0]} ({row[1]})")

    cursor.execute("""
        SELECT table_name 
        FROM information_schema.views 
        WHERE table_schema = 'public';
    """)
    print("\nVIEWS:")
    for row in cursor.fetchall():
        print(f"- {row[0]}")
