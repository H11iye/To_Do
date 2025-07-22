from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import time
from sqlalchemy.exc import OperationalError

# APP initialization
app = Flask(__name__)
CORS(app)  # Enable cross-origin resource sharing

# --- Database Configuration for MariaDB ---
# We get the database credentials from environment variables.
# These will be set in the docker-compose.yml file.
db_user = os.environ.get('MARIADB_USER')
db_password = os.environ.get('MARIADB_PASSWORD')
db_name = os.environ.get('MARIADB_DATABASE')
db_host = 'db'  # This is the service name of the MariaDB container in docker-compose

# SQLAlchemy Database URI for MariaDB
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'

# Disables a feature that signals the application every time a change is about to be made in the database.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class Task(db.Model):
    """ Task Model
    Represents a to-do task in the database."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        """Converts the task object to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed
        }

# --- Function to wait for DB and create tables ---
def init_db():
    """
    Waits for the database to be ready and then creates all tables.
    This is important in a containerized environment.
    """
    retries = 5
    while retries > 0:
        try:
            with app.app_context():
                db.create_all()
            print("Database tables created.")
            return
        except OperationalError:
            retries -= 1
            print(f"Database not ready, retrying... ({retries} retries left)")
            time.sleep(5)
    print("Could not connect to the database. Exiting.")
    exit(1)


# --- API Endpoints ---
@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task.
    Expects a JSON payload with a 'title' and optional 'description'."""
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Missing title in request'}), 400

    new_task = Task(
        title=data['title'],
        description=data.get('description', '')
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Retrieves all tasks from the database."""
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks]), 200

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Retrieves a single task by its ID."""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict()), 200

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Updates an existing task.
    Can update 'title', 'description', and 'completed' status."""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)

    db.session.commit()
    return jsonify(task.to_dict()), 200

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Deletes a task by its ID."""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'}), 200

# --- Main Execution ---
if __name__ == '__main__':
    # Initialize the database
    init_db()
    # Run the Flask app
    app.run(host='0.0.0.0', port=5001, debug=True)
