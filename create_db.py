import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# Create Employees table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Employees (
    ID INTEGER PRIMARY KEY,
    Name TEXT,
    Department TEXT,
    Salary REAL,
    Hire_Date TEXT
)
''')

# Create Departments table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Departments (
    ID INTEGER PRIMARY KEY,
    Name TEXT,
    Manager TEXT
)
''')

# Insert initial data into Employees
employees = [
    (1, 'Alice', 'Sales', 50000, '2021-01-15'),
    (2, 'Bob', 'Engineering', 70000, '2020-06-10'),
    (3, 'Charlie', 'Marketing', 60000, '2022-03-20')
]
cursor.executemany('INSERT INTO Employees VALUES (?, ?, ?, ?, ?)', employees)

# Insert initial data into Departments
departments = [
    (1, 'Sales', 'Alice'),
    (2, 'Engineering', 'Bob'),
    (3, 'Marketing', 'Charlie')
]
cursor.executemany('INSERT INTO Departments VALUES (?, ?, ?)', departments)

# Commit changes and close the connection
conn.commit()
conn.close()