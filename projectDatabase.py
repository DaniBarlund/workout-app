import sqlite3
from sqlite3.dbapi2 import Cursor

def printDatabase():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    print('done')

def clearDatabase():
    conn = sqlite3.connect('workouts.db')
    c = conn.cursor()

    # delete all rows from table
    c.execute('DELETE FROM workouts;',)

    #commit the changes to db			
    conn.commit()
    #close the connection
    conn.close()

#Create account database
#conn = sqlite3.connect('users.db')
#cursor = conn.cursor()

#Create table

'''cursor.execute("""CREATE TABLE users(
    username text,
    password text,
    id integer)""")
'''

#Create database for workouts
conn = sqlite3.connect('workouts.db')
cursor = conn.cursor()
'''cursor.execute("""CREATE TABLE workouts (
    id integer,
    date text,
    Squat text,
    Bench_Press text,
    Incline_Dumbbell_Press text,
    Deadlift text,
    Leg_Extension text,
    Leg_Curl text,
    Chest_Fly text,
    Peck_Deck text,
    Pullover text,
    Lat_Pulldown text,
    Row_Machine text,
    Tricep_Pushdown text,
    Bicep_Curl text)""")
'''

conn.commit()

printDatabase()

conn.close()

