from flask import Flask, render_template_string
import os
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

@app.route('/')
def index():
    try:
        # Connect to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Get the current database user
        cursor.execute("SELECT USER()")
        db_user = cursor.fetchone()[0]

        # Get the list of all databases the user has access to
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]

        # Get tables for each database
        db_tables = {}
        for db in databases:
            try:
                cursor.execute(f"USE `{db}`")  # Switch to the database
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]
                db_tables[db] = tables
            except mysql.connector.Error:
                db_tables[db] = ["Access Denied"]  # Handle databases the user cannot access

        # Render the information on the web page
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Info</title>
            <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                color: #333;
                margin: 0;
                padding: 0;
            }
            header {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                text-align: center;
            }
            h1, h2 {
                color: #4CAF50;
            }
            p {
                font-size: 1.1em;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                background: #e8f5e9;
                margin: 5px 0;
                padding: 10px;
                border-radius: 5px;
            }
            .container {
                max-width: 800px;
                margin: 20px auto;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            .database {
                margin-bottom: 20px;
            }
            </style>
        </head>
        <body>
            <header>
            <h1 style="color: white;">DB VIEWER APP</h1>
            </header>
            <div style="background-color: #00008B; color: white; padding: 5px; text-align: center;">
                <h2 style="color: white;">All the databases and the tables within them to which {{ db_user }} has access</h2>
            </div>
            <div class="container">
            <p><strong>Current User:</strong> {{ db_user }}</p>
            <h2>Databases and Tables:</h2>
            {% for db, tables in db_tables.items() %}
                <div class="database">
                    <h3>Database: {{ db }}</h3>
                    <ul>
                        {% for table in tables %}
                        <li>{{ table }}</li>
                        {% endfor %}
                    </ul>
                </div>
            {% endfor %}
            </div>
        </body>
        </html>
        """
        return render_template_string(html_template, db_user=db_user, db_tables=db_tables)

    except mysql.connector.Error as err:
        return f"Error: {err}"

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)