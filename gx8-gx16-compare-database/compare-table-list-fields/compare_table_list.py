import pyodbc
import csv

# Function to get field details (name and type) from a table
def get_table_schema(connection, table_name):
    query = f"""
    SELECT COLUMN_NAME, DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = '{table_name}'
    """
    cursor = connection.cursor()
    cursor.execute(query)
    return {row[0]: row[1] for row in cursor.fetchall()}

# Function to check if a table exists in the database
def table_exists(connection, table_name):
    query = f"""
    SELECT 1
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_NAME = '{table_name}'
    """
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchone() is not None

# Main function to compare table schemas
def compare_table_schemas(txt_file, output_csv, conn_str_db1, conn_str_db2):
    # Connect to both databases
    conn_db1 = pyodbc.connect(conn_str_db1)
    conn_db2 = pyodbc.connect(conn_str_db2)

    with open(txt_file, 'r') as file:
        tables = [line.strip() for line in file.readlines() if line.strip()]

    with open(output_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([
            "Table Name", 
            "Table Present in DB1", 
            "Table Present in DB2", 
            "Field Name", 
            "Field Present in DB1", 
            "Field Present in DB2", 
            "Field Type in DB1", 
            "Field Type in DB2",
            "has_changed"  # New column
        ])

        for table in tables:
            table_in_db1 = table_exists(conn_db1, table)
            table_in_db2 = table_exists(conn_db2, table)

            if table_in_db1:
                schema_db1 = get_table_schema(conn_db1, table)
            else:
                schema_db1 = {}

            if table_in_db2:
                schema_db2 = get_table_schema(conn_db2, table)
            else:
                schema_db2 = {}

            all_fields = set(schema_db1.keys()).union(set(schema_db2.keys()))

            for field in all_fields:
                # Check if any value in the row is False
                has_changed = not (
                    table_in_db1 and 
                    table_in_db2 and 
                    (field in schema_db1) and 
                    (field in schema_db2) and 
                    (schema_db1.get(field, "N/A") == schema_db2.get(field, "N/A"))
                )
                
                csvwriter.writerow([
                    table,
                    table_in_db1,
                    table_in_db2,
                    field,
                    field in schema_db1,
                    field in schema_db2,
                    schema_db1.get(field, "N/A"),
                    schema_db2.get(field, "N/A"),
                    has_changed  # New column value
                ])

    # Close the connections
    conn_db1.close()
    conn_db2.close()

# Configuration
if __name__ == "__main__":
    # Input TXT file with table names
    txt_file = "compare_table_list_tables.txt"

    # Output CSV file
    output_csv = "compare_table_list_comparison_results_2.csv"

    # Connection strings for both databases
    conn_str_db1 = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=SERVER_1;"
    "DATABASE=DATABASE_1;"
    "Trusted_Connection=yes;"
    )

    conn_str_db2 = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=SERVER_2;"
    "DATABASE=DATABASE_2;"
    "Trusted_Connection=yes;"
    )

    compare_table_schemas(txt_file, output_csv, conn_str_db1, conn_str_db2)