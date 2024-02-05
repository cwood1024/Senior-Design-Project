import sqlite3
from prettytable import PrettyTable

def print_database_output(cursor):
    # Fetch all data from the database
    cursor.execute('SELECT * FROM hitters')
    hitters_data = cursor.fetchall()

    # Create a PrettyTable instance and add columns
    table = PrettyTable()
    table.field_names = ["Hitter Name", "Hitting Side", "Stance Width", "Video Location"]

    # Add data to the table
    for row in hitters_data:
        table.add_row(row[1:])  # Exclude the 'id' column
        
    print(table)

def open_mlb_db():
    conn = sqlite3.connect('mlb_hitters_data.db')
    cursor = conn.cursor()
    print_database_output(cursor)

    delete_entry = input("Enter the ID of the entry you want to delete (or '0' to cancel): ")

    if delete_entry.isdigit():
        entry_id = int(delete_entry)
        if entry_id != 0:
            # Delete the entry with the specified ID
            cursor.execute('DELETE FROM hitters WHERE id = ?', (entry_id,))
            conn.commit()
            print(f"Entry with ID {entry_id} deleted.")
        else:
            print("Deletion canceled.")

    conn.close()
