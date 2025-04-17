import os
import time
from urllib.parse import quote

def activity(activity_url, filename, log_file_path="./",):
    """
    Logs an activity with a timestamp to the specified file.

    Args:
        log_file_path (str): Path to the log file.
        filename (str): Name of the log file.
        activity_url (str): The ID-URL of the parameter to log.
    """
    # Encode the parameter to ensure it is safe for logging
    encoded_parameter = quote(activity_url, safe="")
    with open(os.path.join(log_file_path, filename), 'a') as file:
        file.write(str(time.time()) + "," + activity_url + "\n")


def add_question_mark(filename,log_file_path="./"):
    """
    Appends a question mark '?' as a new line to the log file.

    Args:
        log_file_path (str): Path to the log file.
        filename (str): The name of the log file.
    """
    with open(os.path.join(log_file_path, filename), 'a') as file:
        file.write('?,\n')

def undo_last_log(filename,log_file_path="./"):
    """
    Undo last log entry.

    Args:
        log_file_path (str): Path to the log file.
        filename (str): The name of the log file.
    """
    file_path = os.path.join(log_file_path, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError("Log file does not exist.")

    with open(file_path, 'r') as file:
        lines = file.readlines()

    if not lines:
        raise ValueError("Log file is empty.")
    
    lines.pop(-1)

    with open(file_path, 'w') as file:
        file.writelines(lines)