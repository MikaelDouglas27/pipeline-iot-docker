"""Ingestão e tratamento do conjunto Temperature Readings: IoT Devices."""
import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "IOT-temp.csv")

def get_engine():
    user = os.getenv("POSTGRES_USER", "iot_user")
    password = os.getenv("POSTGRES_PASSWORD", "troque_esta_senha")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "iot_db")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")

def normalize_columns(df):
    # O CSV original usa nomes como "room_id/id" e "out/in".
    df.columns = [str(c).strip().lower() for c in df.columns]
    aliases = {
        "room_id/id": "room_id", "room_id": "room_id",
        "noted_date": "noted_at", "temp": "temperature",
        "out/in": "location", "out_in": "location"
    }
    df = df.rename(columns=aliases)
    required = {"noted_at", "temperature", "location"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {sorted(missing)}. Colunas encontradas: {list(df.columns)}")
    if "id" in df.columns:
        df = df.rename(columns={"id": "reading_id"})
    else:
        df["reading_id"] = range(1, len(df) + 1)
    if "room_id" not in df.columns:
        df["room_id"] = "nao_informado"
    df["noted_at"] = pd.to_datetime(df["noted_at"], errors="coerce", dayfirst=False)
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["location"] = df["location"].astype(str).str.strip().str.lower()
    df["room_id"] = df["room_id"].astype(str)
    df = df.dropna(subset=["noted_at", "temperature"])
    df = df.drop_duplicates(subset=["reading_id"])
    return df[["reading_id", "room_id", "noted_at", "temperature", "location"]]

def main():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV não encontrado: {CSV_PATH}. Baixe o Kaggle e coloque-o em data/IOT-temp.csv.")
    raw = pd.read_csv(CSV_PATH)
    clean = normalize_columns(raw)
    engine = get_engine()
    clean.to_sql("temperature_readings", engine, if_exists="replace", index=False, chunksize=5000, method="multi")
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE temperature_readings ADD PRIMARY KEY (reading_id)"))
        with open(os.path.join(ROOT, "sql", "views.sql"), encoding="utf-8") as f:
            for statement in f.read().split(";"):
                if statement.strip():
                    conn.execute(text(statement))
    print(f"Pipeline concluído: {len(clean)} leituras inseridas no PostgreSQL.")

if __name__ == "__main__":
    main()
