import sqlite3

connection = sqlite3.connect("not_telegram.db")
cursor = connection.cursor()

cursor.execute("DELETE FROM Users WHERE id = 6")

cursor.execute("SELECT COUNT(*) FROM Users")
total_records = cursor.fetchone()[0]

cursor.execute("SELECT SUM(balance) FROM Users")
total_balance = cursor.fetchone()[0]

cursor.execute("SELECT AVG(balance) FROM Users")
average_balance = cursor.fetchone()[0]
print(average_balance)

connection.commit()
connection.close()
