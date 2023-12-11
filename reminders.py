import csv
import os
from datetime import datetime

class ReminderAgent:
    def __init__(self, filename='reminders.csv'):
        self.filename = filename
        self.check_create_csv()

    def check_create_csv(self):
        """Check if the CSV file exists and create it with headers if it doesn't."""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['reminder_name', 'reminder_date'])

    def write_reminder(self, reminder_name, reminder_date):
        """Write a new reminder to the CSV file."""
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([reminder_name, reminder_date])

    def read_reminders(self, date):
        """Read and return reminders for a specific date."""
        reminders = []
        with open(self.filename, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                if row[1] == date:
                    reminders.append(row[0])
        return reminders

if __name__ == "__main__":
    reminder_agent = ReminderAgent()

    # Add reminders
    reminder_agent.write_reminder("Doctor's Appointment", "2023-12-10")
    reminder_agent.write_reminder("Meeting with John", "2023-12-11")

    # Read reminders for a specific date
    reminders_for_today = reminder_agent.read_reminders("2023-12-10")
    print("Reminders for today:", reminders_for_today)
