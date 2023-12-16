import os
from dotenv import load_dotenv
load_dotenv()
import openai

openai.api_key = os.getenv('OPENAI')

def update_chat(messages, role, content):
    """Adds a message to the conversation history."""
    messages.append({"role": role, "content": content})
    return messages

def get_chatgpt_response(messages):
    """Gets the response from GPT-4."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=150
    )
    return response['choices'][0]['message']['content']

def query_gpt_for_reminders(messages, prompt):
    """Queries GPT-4 for reminder actions and formats the response."""
    update_chat(messages, "user", prompt)
    gpt_response = get_chatgpt_response(messages)
    update_chat(messages, "assistant", gpt_response)

    # Parsing the response (Adjust as needed based on actual response format)
    parts = gpt_response.split(',')
    try:
        action = parts[0].split(':')[1].strip()
        reminder_name = parts[1].split(':')[1].strip()
        reminder_date = parts[2].split(':')[1].strip()
    except IndexError:
        return {"error": "Response format is incorrect or incomplete"}

    return {
        "action": action,
        "reminder_name": reminder_name,
        "reminder_date": reminder_date
    }

# Example usage
messages = [{"role": "system", "content": "You are Nelson Mandela."}]  # Conversation history
prompt = "Who are you"
print(get_chatgpt_response(messages))

#response = query_gpt_for_reminders(messages, prompt)
#print(response)