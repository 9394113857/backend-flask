from flask import Flask
from datetime import datetime
import pytz  # Add this import

# Create an instance of the Flask class
app = Flask(__name__)

# Define the default route
@app.route('/')
def hello_world():
    # Get the current date and time in IST
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
    # Return an HTML response with the date and time in bold
    return f'Hello, World!<br><b>Current Date and Time (IST): {now}</b>'

# Check if the script is being run directly
if __name__ == '__main__':
    # Run the Flask development server
    app.run(debug=True)
