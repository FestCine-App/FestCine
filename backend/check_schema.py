import pg8000.native

conn = pg8000.native.Connection(user="postgres", password="141279", host="localhost", port=5432, database="festcine")

rows = conn.run("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name, ordinal_position")

for r in rows:
    if not r[0].startswith('vw_'):
        print(f"{r[0]}: {r[1]}")
