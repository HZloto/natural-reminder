import csv
import os

def check_create_csv(filename):
    """Check if the CSV file exists and create it with headers if it doesn't."""
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['reminder_name', 'reminder_date'])

def write_reminder(filename, reminder_name, reminder_date):
    """Write a new reminder to the CSV file."""
    check_create_csv(filename)  # Call check_create_csv function
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([reminder_name, reminder_date])

def read_reminders(filename, date):
    """Read and return reminders for a specific date."""
    check_create_csv(filename)  # Call check_create_csv function
    reminders = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            if row[1] == date:
                reminders.append(row[0])
    return reminders

def edit_reminder(filename, old_reminder_name, new_reminder_name, new_reminder_date):
    """Edit an existing reminder in the CSV file."""
    check_create_csv(filename)  # Ensure the CSV file exists
    updated_reminders = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == old_reminder_name:
                updated_reminders.append([new_reminder_name, new_reminder_date])
            else:
                updated_reminders.append(row)

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_reminders)
