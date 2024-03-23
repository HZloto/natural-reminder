import csv
import os

def check_create_csv(filename):
    """Check if the CSV file exists and create it with headers if it doesn't."""
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['reminder_name', 'reminder_date'])

def origin_write_reminder(filename, reminder_name, reminder_date):
    """Write a new reminder to the CSV file."""
    check_create_csv(filename)  # Call check_create_csv function
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([reminder_name, reminder_date])

def origin_read_reminders(filename, date):
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

def origin_edit_reminder(filename, old_reminder_name, new_reminder_name, new_reminder_date):
    """Edit an existing reminder in the CSV file."""
    check_create_csv(filename)  # Ensure the CSV file exists
    updated_reminders = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == old_reminder_name:
                # Replace the row with new reminder name and date
                updated_reminders.append([new_reminder_name, new_reminder_date])
            else:
                updated_reminders.append(row)
    
    # Write the updated reminders back to the CSV file
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_reminders)

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_reminders)
        
def origin_delete_reminder(filename, reminder_name):
    """Delete an existing reminder from the CSV file, preserving headers."""
    check_create_csv(filename)  # Ensure the CSV file exists
    updated_reminders = []

    if reminder_name == 'all':
        # If the user wants to delete all, just read the headers and skip the rest
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Read only the first row (headers)
            updated_reminders.append(headers)
    else:
        # Proceed row-wise if not deleting all
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for index, row in enumerate(reader):
                if index == 0:
                    # Always append headers
                    updated_reminders.append(row)
                elif row[0] != reminder_name:
                    # Append rows that do not match the reminder to delete
                    updated_reminders.append(row)

    # Write the updated reminders back to the CSV file
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_reminders)