from orchestrator import query_gpt_for_reminders

from reminders import ReminderAgent
messages = [
    {
        "role": "system", 
        "content": (
            "You are the orchestrator of a reminders app. The user will tell you what they want. "
            "Based on this, you return in JSON format three elements: 1. The action (either add_reminder, "
            "delete_reminder, edit_reminder,show_reminder), 2. The reminder name, 3. The reminder date. Use this format: "
            "{ 'action': 'add_reminder', 'reminder_name': 'Doctor's appointment', 'reminder_date': '2022-04-15T10:00:00' }"
        )
    }
]


prompt = input("What do you want to do? ")
while prompt != "exit":
    orch_task = query_gpt_for_reminders(messages, prompt)
    orch_task = {key: str(value).strip("\"") for key, value in orch_task.items()}
    print(orch_task)
    
    if orch_task['action'] == "add_reminder":
        
        agent = ReminderAgent()
        agent.write_reminder(orch_task['reminder_name'], orch_task['reminder_date'])
        
    
    prompt = input("anything else I can help with?: ")
print(query_gpt_for_reminders(messages,prompt))
