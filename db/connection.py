import psycopg2

def connect_db():
    return psycopg2.connect(
        dbname="CARDS",
        user="postgres",
        password="Sunina12",
        host="localhost",
        port="5432"
    )
