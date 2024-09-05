import csv

# Read tasks.csv
tasks = {}
with open('tasks.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row)
        tasks[row['task_id']] = row['task_name']

print(tasks)

# Read flow.csv
flows = {}
with open('flow.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row)
        if row['flow_task_id'] not in flows:
            flows[row['flow_task_id']] = []
        flows[row['flow_task_id']].append(row['next_task_id'])

# Find the first task (the task to which no arrow points)
first_tasks = set(tasks.keys())
for next_tasks in flows.values():
    for next_task in next_tasks:
        if next_task in first_tasks:
            first_tasks.remove(next_task)

# Find the last tasks (the tasks that do not have any arrows pointing to other tasks)
last_tasks = set(tasks.keys())
for flow_task_id in flows.keys():
    if flow_task_id in last_tasks:
        last_tasks.remove(flow_task_id)

print(tasks)
print(first_tasks)
print(last_tasks)

# Create mermaid diagram
diagram = "graph TD\n"
for task_id, task_name in tasks.items():
    diagram += f"{task_id}[{task_id}: {task_name}]\n"

for first_task in first_tasks:
    diagram += f"start_{first_task}(( )) --> {first_task}\n"

for flow_task_id, next_tasks in flows.items():
    if len(next_tasks) > 1:
        diagram += f"{flow_task_id} --> if_{flow_task_id}[IF]\n"
        for next_task in next_tasks:
            diagram += f"if_{flow_task_id} --> {next_task}\n"
    else:
        diagram += f"{flow_task_id} --> {next_tasks[0]}\n"

for last_task in last_tasks:
    diagram += f"{last_task} --> end_{last_task}(( ))\n"

# Print the diagram
print(diagram)