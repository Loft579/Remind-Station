from __future__ import annotations
import sqlite3



def create_reminders_table():
    connection = sqlite3.connect("reminders_file.db")

    cursor = connection.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, message_id INTEGER, content TEXT)")

    connection.commit()
    
    connection.close()


class Reminder:
    def __init__(self, message_id, content):

        self.message_id = message_id
        self.message_content = content
        self.db_id = None
        self.created_at = None
        

    @classmethod
    def insert_one(cls, reminder : Reminder):
        assert reminder.db_id == None
        connection = sqlite3.connect("reminders_file.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO reminders (message_id, content) VALUES (?, ?)", (reminder.message_id, reminder.message_content))
        connection.commit()
        connection.close()

    @classmethod
    def get_one_by_id(cls, id: int) -> Reminder:
        connection = sqlite3.connect("reminders_file.db")
        cursor = connection.cursor()
        reminder_data = cursor.execute("SELECT * FROM reminders WHERE ID = " + str(id) + ";").fetchone()
        if reminder_data != None:
            one = Reminder(reminder_data[2],reminder_data[3])
            one.db_id = reminder_data[0]
            one.created_at = reminder_data[1]
            return one
        connection.close()

    @classmethod
    def get_all(cls):
        connection = sqlite3.connect("reminders_file.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM reminders")
        all_rows = cursor.fetchall()
        all_reminders = []
        for row in all_rows:
            reminder = Reminder(row[2],row[3])
            reminder.db_id = row[0]
            reminder.created_at = row[1]
            all_reminders.append(reminder)
        connection.close()
        return all_reminders
        


#test zone 
'''
while True:
    action_select = input("c = create reminder | g = get & preview reminder by ID: | a = get & preview all reminders: | t = test the 3 functions:")
    create_reminders_table()
    if action_select == "c":
        message_id = input("create reminder, message_id:")
        message_content = input("create reminder, message_content:")
        new_reminder = Reminder(message_id, message_content)
        if input("insert 'y' to add to reminders") == 'y':
            Reminder.insert_one(new_reminder)
    if action_select == "g":
        id_get_id = int(input("insert the id of the reminder to preview the reminder:"))
        gotten_reminder = Reminder.get_one_by_id(id_get_id)
        print(gotten_reminder.message_id, "|", gotten_reminder.message_content, "|", gotten_reminder.db_id, "|",gotten_reminder.created_at)
    if action_select == "a":
        print(Reminder.get_all()[0].db_id)
    if action_select == "t":
        Reminder.insert_one(Reminder(464564165,"hola hola hola"))
        print(Reminder.get_all())
        print(Reminder.get_one_by_id(3).message_content)
'''
        
