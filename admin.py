import sqlite3
from prettytable import PrettyTable



def check_values():
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    for i in tables:
        rows = cursor.execute(f"PRAGMA table_info({str(*i)})").fetchall()
        column_names = [name[1] for name in rows]
        table = PrettyTable(column_names)
        data = cursor.execute(f"SELECT * FROM {str(*i)}").fetchall()
        for d in data:
            table.add_row(d)
        print(table, "\n")

def main():
    check_values()


if __name__ == "__main__":
    main()