import pyodbc
import csv

# Connection string for username / password authentication
db1_conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=SERVERNAME;"
    "DATABASE=DATABASE;"
    "UID=USERNAME;"
    "PWD=123456;"
)

# Connection string for Windows authentication
# db1_conn_str = (
#     "DRIVER={ODBC Driver 17 for SQL Server};"
#     "SERVER=SERVERNAME;"
#     "DATABASE=DATABASE;"
#     "Trusted_Connection=yes;"
# )

db2_conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=SERVERNAME_2;"
    "DATABASE=DATABASE_2;"
    "Trusted_Connection=yes;"
)


def get_tables(connection):
    query = """
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        return {row.TABLE_NAME for row in cursor.fetchall()}

def main():
    try:
        # Connect to Database 1
        conn_db1 = pyodbc.connect(db1_conn_str)
        tables_db1 = get_tables(conn_db1)
        conn_db1.close()

        # Connect to Database 2
        conn_db2 = pyodbc.connect(db2_conn_str)
        tables_db2 = get_tables(conn_db2)
        conn_db2.close()

        # Generate report
        all_tables = sorted(tables_db1.union(tables_db2))
        report_data = [
            [
                table,
                "Yes" if table in tables_db1 else "No",
                "Yes" if table in tables_db2 else "No",
            ]
            for table in all_tables
        ]

        # Write to CSV
        with open("database_comparison_report.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Table Name", "In Database1", "In Database2"])
            writer.writerows(report_data)

        print("Comparison report generated: database_comparison_report.csv")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
