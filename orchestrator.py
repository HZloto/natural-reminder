import os
from dotenv import load_dotenv
from openai import OpenAI
import os
import json

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
        # Assuming the response from GPT is a JSON-formatted string
        # Convert the string response to a dictionary
        response_dict = json.loads(gpt_response)
        
        # Check if all required keys are in the response
        if all(key in response_dict for key in ['action']):
            return response_dict
        else:
            # Missing one or more keys, return an error
            return {
                "error": "Response format is incorrect or incomplete: missing 'action')"
            }
    except json.JSONDecodeError as e:
        # Handle case where response is not a valid JSON
        return {
            "error": f"Failed to parse response as JSON: {e}"
        }
    except Exception as e:
        # General error handling
        return {
            "error": f"Unexpected error: {e}"
        }