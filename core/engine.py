"""
Natural Language → SQL Engine
Uses Claude (Anthropic API) to convert plain English questions
into executable SQL queries against a known schema.
"""
import re
import json
import requests
from core.database import SCHEMA_DESCRIPTION, execute_query, get_table_info


SYSTEM_PROMPT = f"""You are an expert SQL query generator for a SQLite analytics database.

{SCHEMA_DESCRIPTION}

Rules:
1. Generate ONLY valid SQLite SQL — no explanations, no markdown, no backticks
2. Always use proper JOINs when querying across tables
3. Use aliases for readability (e.g. e for employees)
4. Limit results to 100 rows unless asked for more
5. For aggregations always include a meaningful column alias
6. Return ONLY the raw SQL query, nothing else

Examples:
Q: Show all employees in Engineering
A: SELECT * FROM employees WHERE department = 'Engineering';

Q: What is the average salary by department?
A: SELECT department, ROUND(AVG(salary), 2) AS avg_salary FROM employees GROUP BY department ORDER BY avg_salary DESC;

Q: Top 5 products by total revenue
A: SELECT product, SUM(amount) AS total_revenue FROM orders WHERE status = 'delivered' GROUP BY product ORDER BY total_revenue DESC LIMIT 5;
"""


class NL2SQLEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.query_history = []

    def generate_sql(self, question: str) -> dict:
        """Convert natural language question to SQL using Claude API."""
        if not self.api_key:
            return self._fallback_sql(question)

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 500,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": question}],
                },
                timeout=15,
            )
            data = response.json()
            sql = data["content"][0]["text"].strip()
            sql = re.sub(r"```sql|```", "", sql).strip()
            return {"sql": sql, "source": "claude", "question": question}

        except Exception as e:
            print(f"[NL2SQL] API error: {e}, falling back to rule-based")
            return self._fallback_sql(question)

    def run(self, question: str) -> dict:
        """Full pipeline: NL → SQL → Execute → Return results."""
        gen = self.generate_sql(question)
        sql = gen["sql"]

        try:
            result = execute_query(sql)
            entry = {
                "question": question,
                "sql": sql,
                "source": gen["source"],
                "columns": result["columns"],
                "rows": result["rows"],
                "count": result["count"],
                "error": None,
            }
        except Exception as e:
            entry = {
                "question": question,
                "sql": sql,
                "source": gen["source"],
                "columns": [],
                "rows": [],
                "count": 0,
                "error": str(e),
            }

        self.query_history.append(entry)
        return entry

    def _fallback_sql(self, question: str) -> dict:
        """
        Rule-based fallback when no API key is set.
        Handles common query patterns without LLM.
        """
        q = question.lower()

        # salary queries
        if "average salary" in q and "department" in q:
            sql = "SELECT department, ROUND(AVG(salary),2) AS avg_salary FROM employees GROUP BY department ORDER BY avg_salary DESC;"
        elif "highest salary" in q or "top salary" in q or "highest paid" in q:
            sql = "SELECT name, department, salary FROM employees ORDER BY salary DESC LIMIT 5;"
        elif "salary" in q and "engineering" in q:
            sql = "SELECT name, salary FROM employees WHERE department='Engineering' ORDER BY salary DESC;"
        elif "salary" in q:
            sql = "SELECT name, department, salary FROM employees ORDER BY salary DESC;"

        # employee queries
        elif "how many employees" in q or "count employees" in q:
            sql = "SELECT department, COUNT(*) AS employee_count FROM employees GROUP BY department ORDER BY employee_count DESC;"
        elif "employee" in q and "engineering" in q:
            sql = "SELECT * FROM employees WHERE department='Engineering';"
        elif "employee" in q and "marketing" in q:
            sql = "SELECT * FROM employees WHERE department='Marketing';"
        elif "all employees" in q or "list employees" in q:
            sql = "SELECT * FROM employees ORDER BY department, name;"
        elif "recently hired" in q or "new employee" in q:
            sql = "SELECT name, department, hire_date FROM employees ORDER BY hire_date DESC LIMIT 5;"

        # order queries
        elif "revenue" in q and ("top" in q or "best" in q):
            sql = "SELECT product, SUM(amount) AS total_revenue FROM orders WHERE status='delivered' GROUP BY product ORDER BY total_revenue DESC LIMIT 5;"
        elif "pending order" in q:
            sql = "SELECT * FROM orders WHERE status='pending' ORDER BY order_date DESC;"
        elif "order" in q and "region" in q:
            sql = "SELECT region, COUNT(*) AS orders, SUM(amount) AS total FROM orders GROUP BY region ORDER BY total DESC;"
        elif "total revenue" in q or "total sales" in q:
            sql = "SELECT SUM(amount) AS total_revenue, COUNT(*) AS total_orders FROM orders WHERE status='delivered';"
        elif "cancelled" in q:
            sql = "SELECT * FROM orders WHERE status='cancelled';"

        # product queries
        elif "low stock" in q or "out of stock" in q:
            sql = "SELECT name, category, stock FROM products WHERE stock < 50 ORDER BY stock ASC;"
        elif "expensive product" in q or "most expensive" in q:
            sql = "SELECT name, category, price FROM products ORDER BY price DESC LIMIT 5;"
        elif "product" in q and "category" in q:
            sql = "SELECT category, COUNT(*) AS products, AVG(price) AS avg_price FROM products GROUP BY category;"

        # department queries
        elif "department budget" in q or "budget" in q:
            sql = "SELECT name, budget, head_count FROM departments ORDER BY budget DESC;"

        # default
        else:
            sql = "SELECT * FROM employees ORDER BY department LIMIT 20;"

        return {"sql": sql, "source": "rule-based", "question": question}
