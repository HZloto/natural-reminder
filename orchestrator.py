import os
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI'))


def update_chat(messages, role, content):
    """Adds a message to the conversation history."""
    messages.append({"role": role, "content": content})

def get_chatgpt_response(messages):
    """Gets the response from GPT-4."""
    try:
        response = client.chat.completions.create(response_format={ "type": "json_object" },
        model="gpt-3.5-turbo-1106",
        messages=messages,
        max_tokens=150)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in getting response: {e}"

def query_gpt_for_reminders(messages, prompt):
    """Queries GPT-4 for reminder actions and formats the response."""
    update_chat(messages, "user", prompt)
    gpt_response = get_chatgpt_response(messages)
    update_chat(messages, "assistant", gpt_response)

    # Attempt to parse the response
    try:
        parts = gpt_response.split(',')
        action, reminder_name, reminder_date = (part.split(':')[1].strip().strip('\'"') for part in parts)
        return {
            "action": action,
            "reminder_name": reminder_name,
            "reminder_date": reminder_date
        }
    except Exception as e:
        return {"error": f"Response format is incorrect or incomplete: {e}"},print(gpt_response)
