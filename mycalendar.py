import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def retrieve_events(start_date, end_date):
    """Retrieves and displays calendar events between start_date and end_date."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
        start_datetime_str = start_datetime.isoformat() + "Z"  # 'Z' indicates UTC time
        end_datetime_str = end_datetime.isoformat() + "Z"  # 'Z' indicates UTC time

        print(f"Getting events between {start_datetime_str} and {end_datetime_str}")
        events_result = (
                service.events()
                .list(
                        calendarId="primary",
                        timeMin=start_datetime_str,
                        timeMax=end_datetime_str,
                        singleEvents=True,
                        orderBy="startTime",
                )
                .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No events found between the specified dates.")
            return

        # Prints the start and name of the events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

    except HttpError as error:
        print(f"An error occurred: {error}")


def main():
    # Define the start and end dates for retrieving events
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=7)

    # Retrieve and display events
    retrieve_events(start_date, end_date)


if __name__ == "__main__":
    main()
