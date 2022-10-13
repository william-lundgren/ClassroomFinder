import mysql.connector

with open("pass.txt", "r") as file:
    password = file.readline()

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="pets")

mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES")

for x in mycursor:
    print(x)
