#python postgres_test.py

from postgres_client import PostgresClient


client = PostgresClient("postgres://postgres:mysecretpassword@192.168.99.100:5432/postgres")
# Create
client.send("create", "CREATE TABLE IF NOT EXISTS films (title text, director text, year text)")
client.send("insert", "INSERT INTO films (title, director, year) VALUES ('Doctor Strange', 'Scott Derrickson', '2016')")

# Read
result_set = client.send("select", "SELECT * FROM films")
for r in result_set:
    print(r)

# Update
client.send("update", "UPDATE films SET title='Some2016Film' WHERE year='2016'")

# Delete
client.send("delete", "DELETE FROM films WHERE year='2016'")
