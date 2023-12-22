from orchestrator import query_gpt_for_reminders
from reminders import check_create_csv, write_reminder, read_reminders, edit_reminder

def add_reminder(filename, reminder_name, reminder_date):
    """
    Add a new reminder.
    """
    print("Adding reminder...")
    write_reminder(filename=filename, reminder_name=reminder_name, reminder_date=reminder_date)

def edit_reminder(filename, old_reminder_name, new_reminder_name, new_reminder_date):
    """
    Edit an existing reminder.
    """
    print("Editing reminder...")
    edit_reminder(filename=filename, old_reminder_name=old_reminder_name, 
                  new_reminder_name=new_reminder_name, new_reminder_date=new_reminder_date)

def show_reminder(filename, date):
    """
    Show reminders for a specific date.
    """
    print("Showing reminders...")
    reminders = read_reminders(filename=filename, date=date)
    print(reminders)

# Orchestrating the reminders
from orchestrator import query_gpt_for_reminders  # Uncomment in actual usage
from reminders import write_reminder, edit_reminder, read_reminders  # Uncomment in actual usage

messages = [
    {
        "role": "system", 
        "content": (
            "You are the orchestrator of a reminders app. The user will tell you what they want. "
            "Based on this, you return in JSON format three elements: 1. The action (either add_reminder, "
            "delete_reminder, edit_reminder, show_reminder), 2. The reminder name, 3. The reminder date. Use this format: "
            "{ 'action': 'add_reminder', 'reminder_name': 'Doctor's appointment', 'reminder_date': '2022-04-15T10:00:00' }"
        )
    }
]

# Prompt from user
prompt = "add a reminder to call my dad tomorrow at 9pm"

# Process the prompt and get the task
orch_task = query_gpt_for_reminders(messages, prompt)  # Uncomment in actual usage

# Action mapping dictionary
action_mapping = {
    "add_reminder": add_reminder,
    "edit_reminder": edit_reminder,
    "show_reminder": show_reminder
}

# Filename for reminders
filename = "reminders_db.csv"

# Execute the corresponding action
action = orch_task['action']
if action in action_mapping:
    action_mapping[action](filename, **{k: orch_task[k] for k in orch_task if k != 'action'})
else:
    print(f"Action '{action}' is not recognized.")
