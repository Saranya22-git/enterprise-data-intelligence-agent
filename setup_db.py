import sqlite3

def create_database():
    conn = sqlite3.connect("enterprise_data.db")
    cursor = conn.cursor()

    # 1. Department Performance & Financials Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS department_kpis (
        record_id INTEGER PRIMARY KEY,
        department TEXT,
        quarter TEXT,
        revenue_usd REAL,
        operational_cost_usd REAL,
        retention_rate REAL,
        customer_count INTEGER
    )
    """)

    # 2. Project Delivery & Risk Metrics Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_risk_metrics (
        project_id INTEGER PRIMARY KEY,
        project_name TEXT,
        department TEXT,
        risk_level TEXT,
        budget_variance_pct REAL,
        delivery_status TEXT
    )
    """)

    # Department KPI seed data
    kpi_records = [
        (1, "Healthcare Solutions", "Q1-2025", 1250000.0, 750000.0, 0.94, 320),
        (2, "Healthcare Solutions", "Q2-2025", 1400000.0, 800000.0, 0.96, 350),
        (3, "Financial Services", "Q1-2025", 2100000.0, 1200000.0, 0.89, 540),
        (4, "Financial Services", "Q2-2025", 1950000.0, 1150000.0, 0.87, 510),
        (5, "Retail & Consumer", "Q1-2025", 980000.0, 620000.0, 0.91, 410),
        (6, "Retail & Consumer", "Q2-2025", 1120000.0, 640000.0, 0.93, 440)
    ]

    # Project Risk seed data
    risk_records = [
        (101, "Clinical Workflow AI", "Healthcare Solutions", "Low", 2.4, "On Track"),
        (102, "EHR Data Lake Migration", "Healthcare Solutions", "Medium", 6.8, "Delayed"),
        (103, "Fraud Detection Pipeline", "Financial Services", "Low", -1.2, "On Track"),
        (104, "Core Banking Modernization", "Financial Services", "High", 14.5, "At Risk"),
        (105, "Omnichannel Recommendation Engine", "Retail & Consumer", "Low", 0.5, "On Track"),
        (106, "Inventory Prediction Service", "Retail & Consumer", "Medium", 5.2, "On Track")
    ]

    cursor.executemany("INSERT OR REPLACE INTO department_kpis VALUES (?, ?, ?, ?, ?, ?, ?)", kpi_records)
    cursor.executemany("INSERT OR REPLACE INTO project_risk_metrics VALUES (?, ?, ?, ?, ?, ?)", risk_records)

    conn.commit()
    conn.close()
    print("Database 'enterprise_data.db' generated successfully with 2 tables.")

if __name__ == "__main__":
    create_database()