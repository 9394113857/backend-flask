import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import date
from flask_cors import CORS  # Import CORS

# Setup logger
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')  # Directory for logs
os.makedirs(logs_dir, exist_ok=True)  # Create logs directory if not exists
log_file = os.path.join(logs_dir, f'{date.today()}.log')  # Log file with today's date

# Rotating file handler for logging
log_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)  # Rotate logs after 1MB, keep 5 backups
log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(module)s:%(lineno)d] %(message)s'))  # Log format

logger = logging.getLogger(__name__)  # Get the logger
logger.setLevel(logging.INFO)  # Set logging level to INFO
logger.addHandler(log_handler)  # Add the rotating log handler to the logger

# Clean up older logs except today's
for filename in os.listdir(logs_dir):  # Iterate through all files in the logs directory
    if filename.endswith('.log'):  # Check if it's a log file
        filepath = os.path.join(logs_dir, filename)
        if filepath != log_file:  # Skip today's log file
            os.remove(filepath)  # Remove old log files

# Flask app setup
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create database and table
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid TEXT,
    passid TEXT,
    username TEXT,
    address TEXT,
    country TEXT,
    zip TEXT,
    email TEXT,
    sex TEXT,
    language TEXT,
    desc TEXT
)''')  # Create users table if it doesn't exist
conn.commit()
conn.close()

@app.route('/api/users', methods=['GET'])
def get_users():
    """Fetch all users."""
    try:
        conn = sqlite3.connect('users.db')  # Connect to the database
        c = conn.cursor()
        c.execute('SELECT * FROM users')  # Fetch all user data from the database
        data = c.fetchall()
        conn.close()

        # Log and return data as JSON
        logger.info("Fetched all users")
        return jsonify(data)  # Send data as JSON response
    except Exception as e:
        logger.error(f"Error fetching users: {e}")  # Log error if something goes wrong
        return jsonify({"error": "An error occurred while fetching users."}), 500

@app.route('/api/users', methods=['POST'])
def add_user():
    """Add a new user."""
    if request.is_json:  # Ensure the request is JSON
        try:
            data = request.get_json()  # Parse JSON data from the request

            # Collect data from JSON
            user_data = (
                data['userid'],
                data['passid'],
                data['username'],
                data['address'],
                data['country'],
                data['zip'],
                data['email'],
                data['sex'],
                ', '.join(data['language']),  # Join selected languages into a string
                data['desc']
            )

            conn = sqlite3.connect('users.db')  # Connect to the database
            c = conn.cursor()
            c.execute('''INSERT INTO users (userid, passid, username, address, country, zip, email, sex, language, desc)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', user_data)  # Insert data into the database
            conn.commit()
            conn.close()

            logger.info(f"New user added: {data['username']} ({data['email']})")  # Log new user addition
            return jsonify({"message": "User added successfully!"}), 201  # Respond with success message
        except Exception as e:
            logger.error(f"Error adding user: {e}")  # Log error if something goes wrong
            return jsonify({"error": "An error occurred while adding the user."}), 500
    else:
        return jsonify({"error": "Request must be JSON."}), 400

@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    """Fetch a user by ID."""
    try:
        conn = sqlite3.connect('users.db')  # Connect to the database
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE id=?', (id,))  # Fetch user data by ID
        user = c.fetchone()
        conn.close()

        if user:
            logger.info(f"Fetched user with ID: {id}")
            return jsonify(user)  # Return user data as JSON response
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        logger.error(f"Error fetching user {id}: {e}")  # Log error if something goes wrong
        return jsonify({"error": "An error occurred while fetching the user."}), 500

@app.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    """Update user data."""
    if request.is_json:  # Ensure the request is JSON
        try:
            data = request.get_json()  # Parse JSON data from the request

            # Collect data from JSON
            user_data = (
                data['userid'],
                data['passid'],
                data['username'],
                data['address'],
                data['country'],
                data['zip'],
                data['email'],
                data['sex'],
                ', '.join(data['language']),
                data['desc'],
                id  # Include the user ID to update the correct record
            )

            conn = sqlite3.connect('users.db')  # Connect to the database
            c = conn.cursor()
            c.execute('''UPDATE users SET userid=?, passid=?, username=?, address=?, country=?, zip=?, email=?, sex=?, language=?, desc=? WHERE id=?''', user_data)  # Update user in the database
            conn.commit()
            conn.close()

            logger.info(f"User {id} updated: {data['username']}")
            return jsonify({"message": "User updated successfully!"}), 200  # Respond with success message
        except Exception as e:
            logger.error(f"Error updating user {id}: {e}")  # Log error if something goes wrong
            return jsonify({"error": "An error occurred while updating the user."}), 500
    else:
        return jsonify({"error": "Request must be JSON."}), 400

@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    """Delete a user."""
    try:
        conn = sqlite3.connect('users.db')  # Connect to the database
        c = conn.cursor()
        c.execute('DELETE FROM users WHERE id=?', (id,))  # Delete the user with the given ID
        conn.commit()
        conn.close()

        logger.info(f"User {id} deleted")
        return jsonify({"message": "User deleted successfully!"}), 200  # Respond with success message
    except Exception as e:
        logger.error(f"Error deleting user {id}: {e}")  # Log error if something goes wrong
        return jsonify({"error": "An error occurred while deleting the user."}), 500

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
    # Note: In production, set debug=False and use a proper WSGI server like Gunicorn or uWSGI
# Note: This code is a simple Flask application with CRUD operations for user data.
