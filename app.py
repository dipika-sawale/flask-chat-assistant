import re
from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

def query_db(query, args=(), one=False):
    try:
        with sqlite3.connect('company.db') as conn:
            cursor = conn.cursor()
            cursor.execute(query, args)
            rv = cursor.fetchall()
            print("Executed query:", query, "with args:", args, "Result:", rv)
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        print("Database error:", e)
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def handle_query():
    try:
        user_query = request.json.get('query')
        if not user_query:
            return jsonify({"response": "Query not provided."})
        lower_query = user_query.lower()
        response = ""
        
        # 1. "Employees in the ..." queries:
        if "employees in the" in lower_query:
            # Expected: "Employees in the [Department] department"
            department = lower_query.split("employees in the")[1].strip().replace(" department", "")
            department = department.capitalize()
            employees = query_db("SELECT Name FROM Employees WHERE Department = ?", [department])
            if employees:
                names = ', '.join([e[0] for e in employees])
                response = f"Employees in {department} department: {names}"
            else:
                response = f"No employees found in {department} department."
        
        # 2. "Manager of the ..." queries:
        elif "manager of the" in lower_query:
            department = lower_query.split("manager of the")[1].strip().replace(" department", "")
            department = department.capitalize()
            manager = query_db("SELECT Manager FROM Departments WHERE Name = ?", [department], one=True)
            if manager:
                response = f"The manager of {department} department is {manager[0]}."
            else:
                response = f"No manager found for {department} department."
        
        # 3. "Employees hired after ..." queries:
        elif "employees hired after" in lower_query:
            # Expected: "Show employees hired after 2021-01-01" or similar
            date = lower_query.split("hired after")[1].strip()
            employees = query_db("SELECT Name FROM Employees WHERE Hire_Date > ?", [date])
            if employees:
                names = ', '.join([e[0] for e in employees])
                response = f"Employees hired after {date}: {names}"
            else:
                response = f"No employees hired after {date}."
        
        # 4. "Total salary expense for the ..." queries:
        elif "total salary expense for the" in lower_query:
            department = lower_query.split("total salary expense for the")[1].strip().replace(" department", "")
            department = department.capitalize()
            total_salary = query_db("SELECT SUM(Salary) FROM Employees WHERE Department = ?", [department])
            if total_salary and total_salary[0][0] is not None:
                response = f"The total salary expense for {department} department is ${total_salary[0][0]:,.2f}."
            else:
                response = f"No salary data found for {department} department."
        
        # 5. "How many employees" queries (using regex for flexible extraction):
        elif "how many employees" in lower_query:
            # This regex looks for the department after "in"
            match = re.search(r'in\s+([\w\s]+?)(?:\s*department)?\s*\??$', lower_query)
            if match:
                department = match.group(1).strip().capitalize()
                count = query_db("SELECT COUNT(*) FROM Employees WHERE Department = ?", [department], one=True)
                # Ensure we got a valid result tuple
                if count is not None and count[0] is not None:
                    response = f"There are {count[0]} employees in the {department} department."
                else:
                    response = f"No employees found in {department} department."
            else:
                response = "Sorry, I didn't understand your query."
        
        else:
            response = "Sorry, I didn't understand your query."
    
    except Exception as e:
        print("Error in handling query:", e)
        response = "Sorry, there was an error processing your request."
    
    return jsonify({"response": response})

# Test endpoint to check database connectivity
@app.route('/test_db')
def test_db():
    try:
        with sqlite3.connect('company.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
        return jsonify({
            "status": "success", 
            "tables": [table[0] for table in tables]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
