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
            reminder['reminder_date'] = reminder_date.strftime("%B %d, %I:%M %p")
        return reminders
    except FileNotFoundError:
        return []


current_reminders = load_reminders(filename)

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>NextUp</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: Arial, sans-serif;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e7e7e7;
        }
        .app-name {
            font-weight: bold;
            font-size: 24px;
            margin: 0;
        }
        .app-description {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #f9f9f9; /* Very slight grey color */
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            z-index: 1000;
        }
        .app-description h4 {
            font-size: 18px;
            margin-top: 0;
        }
        .close {
            cursor: pointer;
            float: right;
            font-size: 20px;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: calc(100% - 60px);
            padding: 20px; /* Adjusted padding for breathing room */
        }
        .chat-box {
            width: 100%;
            max-width: 600px;
            margin: 20px auto; /* Added top & bottom margin for equal spacing */
        }
        .messages-container, .reminder-container {
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 20px;
            overflow-y: auto;
        }
        .message, .reminder {
            padding: 10px 20px;
            margin-bottom: 8px;
            border-radius: 20px;
        }
        .reminder {
            background-color: #f0f0f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .reminder-name {
            font-weight: bold;
        }
        .user-message { background-color: #dcf8c6; align-self: flex-end; }
        .system-message { background-color: #f0f0f0; align-self: flex-start; }
        .input-area { display: flex; gap: 10px; margin-top: 20px; }
        textarea {
            flex-grow: 1;
            border-radius: 20px;
            padding: 10px;
            border: 1px solid #ccc;
            resize: none; /* Disables the resize option */
        }
        button { border-radius: 20px; }
        .reminder-container > strong {
            display: block;
            text-align: center;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <header>
        <div class="app-name">NextUp</div>
    </header>
    <div class="app-description">
        <span class="close" onclick="this.parentElement.style.display='none';">&times;</span>
        <h4>NextUp helps you stay on top of your tasks with simple, daily reminders. Organize your day effortlessly.</h4>
    </div>
    <div class="chat-container">
        <div class="chat-box">
            <div class="messages-container d-flex flex-column">
                <!-- Messages will be dynamically inserted here -->
                {% for message in messages %}
                <div class="message {{ message.role }}-message">{{ message.content }}</div>
                {% endfor %}
            </div>
            <form class="input-area" method="post">
                <!-- Added placeholder attribute -->
                <textarea name="command" rows="1" placeholder="Ex: Call parents tonight at 6"></textarea>
                <button type="submit" class="btn btn-primary">Send</button>
            </form>
            {% if reminders %}
            <div class="reminder-container">
                <strong>Your Reminders:</strong> <!-- Title renamed and centered -->
                {% for reminder in reminders %}
                <div class="reminder">
                    <span class="reminder-name">{{ reminder.reminder_name }}</span>
                    <span>{{ reminder.reminder_date }}</span>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script>
        document.querySelector('textarea[name="command"]').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault(); // Prevent default to avoid newline
                this.form.submit(); // Submit form
            }
        });
    </script>
</body>
</html>

"""


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_input = request.form['command']
        response = process_command(user_input)
        reminders = load_reminders(filename)
        messages = [
            {"role": "user", "content": user_input},
            {"role": "system", "content": response}
        ]
        return render_template_string(HTML_TEMPLATE, messages=messages, reminders=reminders)
    
    reminders = load_reminders(filename)
    messages = [
        {"role": "system", "content": "Welcome to the Reminder App. What can I do for you today?"}
    ]
    return render_template_string(HTML_TEMPLATE, messages=messages, reminders=reminders)


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
                "{ 'action': 'add_reminder', 'reminder_name': 'Doctor's appointment', 'reminder_date': '2022-04-15T10:00:00', 'response': 'Added a reminder for your doctor appointment at 10}."
                f"If the user wishes to edit or delete a reminder, make sure to provide the exact name of the reminder (find the most fitting element from this list:{current_reminders})."
                "For an edit, provide old_reminder_name , new_reminder_name, new_reminder_date. "
                "If multiple elements fit the description, pick the latest one in the list."
                "if no hour is specified, use 12pm as the default time."
                "If no action is specified or the user asks a question, use answer_question as the action and just provide a response element: respond their question if it pertains to the app or reminders only. If it doesn't, just say 'I can't help with that. Please ask a question related to the app or reminders.'"
                "You can help the use if they ask about the content for a given day by summarizing the reminders for that day in a simple way."
                "if the user wants to clear the reminders list of everything, call the delete_reminder action with the reminder_name as 'all'."
                "DO NOT ANSWER ANYTHING UNRELATED TO THE APP OR REMINDERS."
                
            )
        }
    ]

    # Initialize an empty dictionary
    my_dict = {}

    with open(filename, mode='r') as infile:
        reader = csv.reader(infile)
        # Skip the header if there is one
        # next(reader, None)
        my_dict = {rows[0]:rows[1] for rows in reader}
        
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
