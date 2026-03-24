"""
Database manager — SQLite with sample schema + data.
Simulates a real analytics database.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "analytics.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS employees (
    employee_id   INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    department    TEXT NOT NULL,
    salary        REAL NOT NULL,
    hire_date     TEXT NOT NULL,
    manager_id    INTEGER,
    location      TEXT
);

CREATE TABLE IF NOT EXISTS departments (
    department_id   INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    budget          REAL NOT NULL,
    head_count      INTEGER,
    location        TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    order_id      INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    product       TEXT NOT NULL,
    amount        REAL NOT NULL,
    quantity      INTEGER NOT NULL,
    order_date    TEXT NOT NULL,
    status        TEXT NOT NULL,
    region        TEXT
);

CREATE TABLE IF NOT EXISTS products (
    product_id    INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    category      TEXT NOT NULL,
    price         REAL NOT NULL,
    stock         INTEGER NOT NULL,
    supplier      TEXT
);
"""

SAMPLE_DATA = """
INSERT OR IGNORE INTO employees VALUES
(1,'Alice Chen','Engineering',120000,'2020-03-15',NULL,'Seattle'),
(2,'Bob Smith','Engineering',95000,'2021-06-01',1,'Seattle'),
(3,'Carol White','Marketing',85000,'2019-11-20',NULL,'New York'),
(4,'David Lee','Engineering',110000,'2020-08-10',1,'Seattle'),
(5,'Eve Johnson','Sales',78000,'2022-01-15',NULL,'Chicago'),
(6,'Frank Brown','Marketing',90000,'2020-05-22',3,'New York'),
(7,'Grace Kim','Engineering',105000,'2021-03-30',1,'Remote'),
(8,'Henry Davis','Sales',82000,'2021-09-12',5,'Chicago'),
(9,'Iris Wang','Management',150000,'2018-01-01',NULL,'Seattle'),
(10,'Jack Wilson','Sales',76000,'2022-07-18',5,'New York');

INSERT OR IGNORE INTO departments VALUES
(1,'Engineering',2500000,4,'Seattle'),
(2,'Marketing',800000,2,'New York'),
(3,'Sales',600000,3,'Chicago'),
(4,'Management',500000,1,'Seattle');

INSERT OR IGNORE INTO orders VALUES
(1,'Acme Corp','Laptop Pro',2499.99,5,'2024-01-10','delivered','West'),
(2,'Beta LLC','Cloud License',899.99,12,'2024-01-15','delivered','East'),
(3,'Gamma Inc','Laptop Pro',2499.99,3,'2024-02-01','shipped','West'),
(4,'Delta Co','Keyboard Elite',149.99,20,'2024-02-10','delivered','Central'),
(5,'Epsilon Ltd','Cloud License',899.99,8,'2024-02-20','pending','East'),
(6,'Zeta Corp','Monitor Ultra',699.99,6,'2024-03-01','delivered','West'),
(7,'Eta Inc','Laptop Pro',2499.99,2,'2024-03-15','cancelled','East'),
(8,'Theta LLC','Keyboard Elite',149.99,15,'2024-03-20','delivered','Central'),
(9,'Iota Corp','Cloud License',899.99,20,'2024-04-01','delivered','West'),
(10,'Kappa Ltd','Monitor Ultra',699.99,4,'2024-04-10','shipped','East');

INSERT OR IGNORE INTO products VALUES
(1,'Laptop Pro','Electronics',2499.99,45,'TechSupply Co'),
(2,'Cloud License','Software',899.99,999,'SoftVendor Inc'),
(3,'Keyboard Elite','Peripherals',149.99,120,'KeyMaster Ltd'),
(4,'Monitor Ultra','Electronics',699.99,35,'ScreenTech Co'),
(5,'Wireless Mouse','Peripherals',59.99,200,'KeyMaster Ltd'),
(6,'USB Hub Pro','Accessories',39.99,300,'GadgetWorld'),
(7,'Webcam HD','Electronics',129.99,80,'TechSupply Co'),
(8,'Desk Lamp LED','Accessories',49.99,150,'LightCo');
"""

SCHEMA_DESCRIPTION = """
Database: Analytics DB

Tables:
1. employees(employee_id, name, department, salary, hire_date, manager_id, location)
   - Stores employee records with salary, department, hire date, and location

2. departments(department_id, name, budget, head_count, location)
   - Department budget and headcount info

3. orders(order_id, customer_name, product, amount, quantity, order_date, status, region)
   - Sales orders with status: delivered, shipped, pending, cancelled

4. products(product_id, name, category, price, stock, supplier)
   - Product catalog with pricing and inventory
"""


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.executescript(SAMPLE_DATA)
    conn.commit()
    conn.close()
    print("[DB] Database initialized with sample data")


def execute_query(sql: str):
    """Execute a SQL query and return results as list of dicts."""
    conn = get_connection()
    try:
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description] if cursor.description else []
        results = [dict(zip(columns, row)) for row in rows]
        return {"columns": columns, "rows": results, "count": len(results)}
    finally:
        conn.close()


def get_table_info():
    """Return schema info for all tables."""
    conn = get_connection()
    tables = {}
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for (table_name,) in cursor.fetchall():
        info = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        tables[table_name] = [{"name": col[1], "type": col[2]} for col in info]
    conn.close()
    return tables
