from flask import Flask

# Create an instance of the Flask class
app = Flask(__name__)

# Define the default route
@app.route('/')
def hello_world():
    return 'Hello, World!'

# Check if the script is being run directly
if __name__ == '__main__':
    # Run the Flask development server
    app.run(debug=True)
