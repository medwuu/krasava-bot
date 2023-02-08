import sqlite3
from prettytable import PrettyTable

connect = sqlite3.connect("data.db")
cursor = connect.cursor()
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()

def check_values():
    global connect
    global cursor
    global tables
    for i in tables:
        table = PrettyTable(["id", "username", "reputation", "cooldown"])
        data = cursor.execute(f"SELECT * FROM {str(*i)}").fetchall()
        for d in data:
            table.add_row(d)
        print(table, "\n")

def edit_values():
    global connect
    global cursor
    global tables
    for i in tables:
        print(*i)
    editing_table = tables[int(input("Enter table index (starts from zero): "))][0]
    print(", ".join(["id", "username", "reputation", "cooldown"]))
    editing_collumn = ["id", "username", "reputation", "cooldown"][int(input("Enter collumn number (starts from zero): "))]
    id_list = cursor.execute(f"SELECT username, id FROM {editing_table}").fetchall()
    print(*id_list)
    who = id_list[int(input("Enter index of user (starts from zero): "))]
    value = input("Enter a new value: ")
    cursor.execute(f"UPDATE {editing_table} set {editing_collumn} = ? where id = ?", (value, who[1]))
    connect.commit()
    print("\nSucsess!")


if __name__ == "__main__":
    check_values()
    if input("Wanna change values? (y) --- ").lower() == "y":
        edit_values()