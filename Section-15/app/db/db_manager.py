import mysql.connector
import pandas as pd
import streamlit as st
from contextlib import contextmanager

class DBManager:
    def __init__(
        self,
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=st.secrets["mysql"]["port"]
    ):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port

    def get_connection(self, use_db=True):
        """Devuelve una conexión a MySQL, opcionalmente a la base de datos."""
        config = {
            "host": self.host,
            "user": self.user,
            "password": self.password,
            "port": self.port
        }
        if use_db:
            config["database"] = self.database
        return mysql.connector.connect(**config)

    @contextmanager
    def connect(self, use_db=True):
        """Context manager para conexión a MySQL."""
        conn = self.get_connection(use_db)
        try:
            yield conn
        finally:
            conn.close()

    def execute_sql(self, sql, params=None, use_db=True):
        """Ejecuta un SQL genérico (CREATE, INSERT, UPDATE, DELETE)."""
        with self.connect(use_db) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, params or ())
                conn.commit()
            finally:
                cursor.close()


    def create_customer_table(self):
        """Crea la tabla customer si no existe."""
        sql = """
            CREATE TABLE IF NOT EXISTS customer (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                surname VARCHAR(100),
                telephone VARCHAR(20),
                project TEXT,
                date DATE
            )
        """
        try:
            self.execute_sql(sql)
        except mysql.connector.Error as err:
            st.error(f"Error creando tabla customer: {err}")

    def insert_sample_customers(self):
        """Inserta datos de ejemplo solo si la tabla está vacía."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customer")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute("""
                    INSERT INTO customer (name, surname, telephone, project, date)
                    VALUES
                    ('Alice', 'Smith', '123456789', 'Project A', CURDATE()),
                    ('Bob', 'Johnson', '987654321', 'Project B', CURDATE())
                """)
                conn.commit()
            cursor.close()

    def fetch_customers(self):
        """Devuelve un DataFrame con los datos de la tabla customer."""
        with self.connect() as conn:
            try:
                df = pd.read_sql("SELECT * FROM customer", conn)
            except Exception as err:
                st.error(f"Error leyendo datos de customer: {err}")
                df = pd.DataFrame()
            return df

    def run_query(self, query, params=None):
        with self.connect() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                rows = cursor.fetchall()
                df = pd.DataFrame(rows)
            except Exception as err:
                st.error(f"Error running the query: {err}")
                df = pd.DataFrame()
            finally:
                cursor.close()
            return df

    def run_action(self, query, params=None):
        with self.connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params or ())
                conn.commit()
            except Exception as err:
                st.error(f"Error running the action: {err}")
            finally:
                cursor.close()

    
    def init_db(self):
        """Inicializa la base de datos y la tabla customer."""
        self.create_customer_table()
        self.insert_sample_customers()
