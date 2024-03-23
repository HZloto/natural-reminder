from orchestrator import query_gpt_for_reminders
from reminders import origin_write_reminder, origin_edit_reminder, origin_delete_reminder
import time
import pandas as pd
import csv

# Filename for reminders
filename = "reminders_db.csv"

df = pd.read_csv(filename)

# Load existing reminders
try:
    df = pd.read_csv(filename)
    current_reminders = df['reminder_name'].tolist()
except FileNotFoundError:
    current_reminders = []

#store the current date and time
current_time = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

def add_reminder(filename, reminder_name, reminder_date):
    """
    Add a new reminder.
    """
    print("Adding reminder...")
    origin_write_reminder(filename=filename, reminder_name=reminder_name, reminder_date=reminder_date)

def edit_reminder(filename, old_reminder_name, new_reminder_name, new_reminder_date):
    """
    Edit an existing reminder.
    """
    print("Editing reminder...")
    origin_edit_reminder(filename=filename, old_reminder_name=old_reminder_name, 
                  new_reminder_name=new_reminder_name, new_reminder_date=new_reminder_date)

def delete_reminder(filename, reminder_name):
    """
    Delete an existing reminder.
    """
    print("Deleting reminder...")
    origin_delete_reminder(filename=filename, reminder_name=reminder_name)
    
def answer_question():
    """
    Answer a question.
    """
    pass

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
            
        )
    }
]


# Action mapping dictionary
action_mapping = {
    "add_reminder": add_reminder,
    "edit_reminder": edit_reminder,
    "delete_reminder": delete_reminder,
    "answer_question": answer_question
}

# Initialize an empty dictionary
my_dict = {}

with open(filename, mode='r') as infile:
    reader = csv.reader(infile)
    # Skip the header if there is one
    # next(reader, None)
    my_dict = {rows[0]:rows[1] for rows in reader}



def main():
    while True:
        # Prompt from user
        user_prompt = input("Please enter your command or say 'exit' to quit: ")
        if user_prompt.lower() == 'exit':
            print("Exiting. Goodbye!")
            break

        prompt = f"The date is {current_time}. The current reminders are: {my_dict}. User prompt: {user_prompt}"

        # Process the prompt and get the task
        orch_task = query_gpt_for_reminders(messages, prompt)
        
        # Execute the corresponding action
        action = orch_task['action']

        print("Fesses",orch_task)
        print(orch_task['response'])


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

if __name__ == "__main__":
    main()