import sqlite3
from prettytable import PrettyTable
from mlb_vid_processing import process_hitter_video


conn = sqlite3.connect('mlb_hitters_data.db')
cursor = conn.cursor()
cursor.execute('''
        CREATE TABLE IF NOT EXISTS mlb_hitters (
            id INTEGER PRIMARY KEY,
            hitter_name TEXT,
            hitting_side TEXT, 
            stance_width TEXT,
            weight_distribution TEXT,
            spilling_over TEXT,
            video_location TEXT   
        )
    ''')
conn.commit()

def print_database_output(cursor):
    # Fetch all data from the database
    cursor.execute('SELECT * FROM mlb_hitters')
    hitters_data = cursor.fetchall()

    # Create a PrettyTable instance and add columns
    table = PrettyTable()
    table.field_names = ["ID", "Hitter Name", "Hitting Side", "Stance Width", "Weight Distribution", "Spilling Over", "Video Location"]

    # Add data to the table
    for row in hitters_data:
        table.add_row(row)
    print(table)

def open_mlb_db():
    print_database_output(cursor)


    choice = input("Select what you would like to do. \n1. Add an entry. \n2. Delete an entry. \n3. Return to menu.\n")
    if choice == "1":
        # Perform action for adding an entry
        print("You selected to add an entry.")
        process_hitter_video()
    elif choice == "2":
        # Perform action for deleting an entry
        print("You selected to delete an entry.")
        delete_entry = input("Enter the ID of the entry you want to delete (or '0' to cancel): ")

        if delete_entry.isdigit():
            entry_id = int(delete_entry)
            if entry_id != 0:
                # Delete the entry with the specified ID
                cursor.execute('DELETE FROM mlb_hitters WHERE id = ?', (entry_id,))
                conn.commit()
                print(f"Entry with ID {entry_id} deleted.")
            else:
                print("Deletion canceled.")
        # Call the function or write the code to delete an entry
    elif choice == "3":
        # Perform action for returning to the menu
        print("You selected to return to the menu.")
        # Write any additional code to return to the menu or end the program
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")
