# Given a CSV file with transitions rom Genexus 8 workflow, generates SQL code 
# to monitor how many instances are in each task

import csv
from collections import defaultdict

# Input CSV
csv_file_path = 'prc_example.csv'  # Replace with your CSV file path

# Output
output_file_path = csv_file_path + '.sql'

def generate_sql_from_csv(csv_file_path):
    transitions = defaultdict(list)
    
    # Read the CSV file
    with open(csv_file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header row if present
        for row in csvreader:
            current_task, next_task = map(int, row)
            transitions[current_task].append(next_task)
    
    # SQL template
    sql_template = """
UNION ALL

SELECT {id}, '{current} -> {next}', '{current} -> {next}', COUNT(*)
FROM wfwrkitems a (NOLOCK)
INNER JOIN wftask b (NOLOCK) ON a.WFTaskCod = b.WFTaskCod AND b.WFPrcId = @prcid
INNER JOIN wfattsvalues c (NOLOCK) ON a.WFInsPrcId = c.WFInsPrcId
WHERE a.WFTaskCod = {current}
AND WFItemInit >= @fecha
AND a.WFInsPrcId NOT IN (
    SELECT a.WFInsPrcId 
    FROM wfwrkitems a (NOLOCK)
    INNER JOIN wftask b (NOLOCK) ON a.WFTaskCod = b.WFTaskCod AND b.WFPrcId = @prcid
    WHERE a.WFTaskCod IN ({next_tasks})
    AND WFItemInit >= @fecha
)"""

    # Generate SQL
    sql_parts = []
    for id, (current, next_tasks) in enumerate(transitions.items(), start=1):
        next_tasks_str = ','.join(map(str, next_tasks))
        next_tasks_display = ','.join(map(str, sorted(next_tasks)))
        sql_parts.append(sql_template.format(
            id=id,
            current=current,
            next=next_tasks_display,
            next_tasks=next_tasks_str
        ))

    # Combine all parts
    full_sql = """
DECLARE @prcid INT = YOUR_PROCESS_ID; -- Replace with your actual process ID
DECLARE @fecha DATE = 'YOUR_DATE'; -- Replace with your actual date

SELECT 1 AS id, '1 -> 1' AS Tarea, '1 -> 1' AS Transicion, COUNT(*) AS cantidad
FROM wfwrkitems a (NOLOCK)
INNER JOIN wftask b (NOLOCK) ON a.WFTaskCod = b.WFTaskCod AND b.WFPrcId = @prcid
INNER JOIN wfattsvalues c (NOLOCK) ON a.WFInsPrcId = c.WFInsPrcId
WHERE 1=0 -- This ensures the first SELECT returns no rows but defines the structure
""" + ''.join(sql_parts)

    return full_sql

# Usage

sql_code = generate_sql_from_csv(csv_file_path)
print(sql_code)

# Open a file in write mode (this will create the file if it doesn't exist)
with open(output_file_path, "w") as file:
    # Write the string to the file
    file.write(sql_code)