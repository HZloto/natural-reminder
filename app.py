from flask import Flask, request, render_template_string
import pandas as pd
import csv
import time
from datetime import datetime
from reminders import origin_write_reminder, origin_edit_reminder, origin_delete_reminder  # Adjust import paths as necessary
from orchestrator import query_gpt_for_reminders
from main import *

app = Flask(__name__)


filename = "reminders_db.csv"

def load_reminders(filename):
    try:
        df = pd.read_csv(filename)
        reminders = df.to_dict('records')  # Converts the DataFrame into a list of dictionaries
        for reminder in reminders:
            # Parse the ISO 8601 date string to a datetime object
            reminder_date = datetime.fromisoformat(reminder['reminder_date'])
            # Reformat the date to a more readable string
            reminder['reminder_date'] = reminder_date.strftime("%B %d, %Y, %I:%M %p")
        return reminders
    except FileNotFoundError:
        return []


current_reminders = load_reminders(filename)

HTML_TEMPLATE = """
<!doctype html>
<html>
<head><title>Reminder App</title></head>
<body>
  <h2>Enter your reminder command</h2>
  <form method="post">
    <textarea name="command" rows="4" cols="50"></textarea><br>
    <input type="submit" value="Submit">
  </form>
  {% if response %}
    <h3>Response:</h3>
    <p>{{ response }}</p>
  {% endif %}
  
  <h3>Current Reminders:</h3>
  <table border="1">
    <tr>
      <th>Reminder Name</th>
      <th>Reminder Date</th>
    </tr>
    {% for reminder in reminders %}
    <tr>
      <td>{{ reminder.reminder_name }}</td>
      <td>{{ reminder.reminder_date }}</td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_input = request.form['command']
        response = process_command(user_input)
        # Reload the reminders here to ensure we have the latest list after processing the command
        reminders = load_reminders(filename)
        return render_template_string(HTML_TEMPLATE, response=response, reminders=reminders)
    
    # For a GET request, we also load the reminders to ensure the page loads with the current reminders list
    reminders = load_reminders(filename)  # Ensure this is outside the if block to cover both GET and POST
    return render_template_string(HTML_TEMPLATE, response=None, reminders=reminders)


def process_command(user_input):
    global current_reminders  # Only needed if modifying it
    
    # If you're referencing it to construct messages or for logic, ensure it's initialized
    if not current_reminders:
        current_reminders = load_reminders(filename)
    
    
    messages = [
        {
            "role": "system", 
            "content": (
                f"You are the orchestrator of a reminders app. The user will tell you what they want. "
                "Based on this, you return in JSON format four elements: 1. The action (either add_reminder, "
                "delete_reminder, edit_reminder, answer_question), 2. The reminder name, 3. The reminder date, 4. A response to the user (you are professional and not very verbose. clean and simple explanation of what you did, that's it). Use this format as an example: "
                "{ 'action': 'add_reminder', 'reminder_name': 'Doctor's appointment', 'reminder_date': '2022-04-15T10:00:00', 'response': 'Done. Added a reminder for your doctor appointment at 10}."
                f"If the user wishes to edit or delete a reminder, make sure to provide the exact name of the reminder (find the most fitting element from this list:{current_reminders})."
                "For an edit, provide old_reminder_name , new_reminder_name, new_reminder_date. "
                "If multiple elements fit the description, pick the latest one in the list."
                "if no hour is specified, use 12pm as the default time."
                "If no action is specified or the user asks a question, use answer_question as the action and just provide a response element: respond their question if it pertains to the app or reminders only. If it doesn't, just say 'I'm sorry, I can't help with that.'"
                "if the user wants to clear the reminders list of everything, call the delete_reminder action with the reminder_name as 'all'."
                "DO NOT ANSWER ANYTHING UNRELATED TO THE APP OR REMINDERS."
                
            )
        }
    ]


    prompt = f"The date is {current_time}. The current reminders are: {my_dict}. User prompt: {user_input}"

    # Process the prompt and get the task
    orch_task = query_gpt_for_reminders(messages, prompt)
    
    # Execute the corresponding action
    action = orch_task['action']

    # Debug
    # print("ORCH TASK:",orch_task)
    # print(orch_task['response'])


    if action in action_mapping:
        if action == 'add_reminder':
            action_mapping[action](filename, orch_task['reminder_name'], orch_task['reminder_date'])
        elif action == 'edit_reminder':
            action_mapping[action](filename, orch_task['old_reminder_name'], orch_task['new_reminder_name'], orch_task['new_reminder_date'])
        elif action == 'delete_reminder':
            action_mapping[action](filename, orch_task['reminder_name'])
        elif action == 'answer_question':
            action_mapping[action]()
    else:
        print(f"Action '{action}' is not recognized.")

    # Reload the reminders from CSV to reflect any changes made
    current_reminders = load_reminders(filename)
    
    return orch_task['response']
    

if __name__ == '__main__':
    app.run(debug=True)
