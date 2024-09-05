import csv
import io
import tkinter as tk
from tkinter import scrolledtext

def create_diagram():
    tasks_text = tasks_textbox.get("1.0", "end-1c")
    flow_text = flow_textbox.get("1.0", "end-1c")

    tasks = {}
    reader = csv.DictReader(io.StringIO(tasks_text))
    for row in reader:
        tasks[row['task_id']] = row['task_name']

    flows = {}
    reader = csv.DictReader(io.StringIO(flow_text))
    for row in reader:
        if row['flow_task_id'] not in flows:
            flows[row['flow_task_id']] = []
        flows[row['flow_task_id']].append(row['next_task_id'])

    first_tasks = set(tasks.keys())
    for next_tasks in flows.values():
        for next_task in next_tasks:
            if next_task in first_tasks:
                first_tasks.remove(next_task)

    last_tasks = set(tasks.keys())
    for flow_task_id in flows.keys():
        if flow_task_id in last_tasks:
            last_tasks.remove(flow_task_id)

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

    result_textbox.delete(1.0, tk.END)
    result_textbox.insert(tk.END, diagram)

root = tk.Tk()
root.title("Mermaid Diagram Creator")

tasks_label = tk.Label(root, text="Tasks (CSV):")
tasks_label.pack()
tasks_textbox = scrolledtext.ScrolledText(root, width=50, height=10)
tasks_textbox.pack()

flow_label = tk.Label(root, text="Flow (CSV):")
flow_label.pack()
flow_textbox = scrolledtext.ScrolledText(root, width=50, height=10)
flow_textbox.pack()

create_button = tk.Button(root, text="Create!", command=create_diagram)
create_button.pack()

result_label = tk.Label(root, text="Result:")
result_label.pack()
result_textbox = scrolledtext.ScrolledText(root, width=50, height=10)
result_textbox.pack()

root.mainloop()