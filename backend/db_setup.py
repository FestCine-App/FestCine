import pg8000.native
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "festcine"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

ddl = """
CREATE OR REPLACE FUNCTION fn_call_comprarentradaevento(
    p_IdAsistente INT, p_IdEvento INT, p_IdTarifa INT
) RETURNS TABLE (respuesta VARCHAR(300)) LANGUAGE plpgsql AS $$
DECLARE v_resp VARCHAR(300);
BEGIN
    CALL ComprarEntradaEvento(p_IdAsistente, p_IdEvento, p_IdTarifa, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;
"""

try:
    conn = pg8000.native.Connection(**DB_CONFIG)
    print("Connected to database.")
    conn.run(ddl)
    print("Wrapper function fn_call_comprarentradaevento created successfully!")
    conn.close()
except Exception as e:
    print("Error creating wrapper function:", e)
