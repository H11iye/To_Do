#Backend/app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# APP _ initialization 

app = Flask(__name__)
CORS(app) #Enable cross-origin resource sharing 

#Data-base configuration 
# Specifies the path to the database file 

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tasks.db')

#Disables a feature that signals the application every time a change is about to be made in the database.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
#database model 

class Task(db.Model):
    """ Task Model 
    Represents a to-do task in the database."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        """converts the task objects to a dictionnary for JSON serialization."""
        return {
            'id' : self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed

        }
    
# API Endpoints

@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task.
    Expects a JSON payload with a 'title' and optional 'description' ."""

    data = request.get_json()
    if not data or not 'title' in data:
        return jsonify({'error': 'Missing title request'}), 400 
    
    new_task = Task(
        title = data['title'],
        description = data.get('description', '')
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201 

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Retrives all tasks from the database."""
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks]), 200
@app.route('/tasks/<int:task_id>', methos=['GET'])
def update_task(task_id):
    """ Rettrieves a single task by its ID."""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict()), 200 

@app.route('/tasks/<int:task_id>', methods=['PUT'])

def update_task(task_id):
    """Updates an existing task.
    Can update 'title', 'description' and 'completed' status.
    """
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed =  data.get('completed', task.completed)

    db.session.commit()
    return jsonify(task.to_dict()), 200 

@app.route('/tasks/<int:task_id>', methods=['DELETE'])

def delete_task(task_id):
    """Deletes a task by its ID."""
    task = Task.query.get_or_404(task_id)

    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'}), 200 

# ____Main Execution___
if __name__ == '__main__':
    #create the database and tables if they don't exist 
    with app.app_context():
        db.create_all()
    #Run the Flask app
    app.run(host='0.0.0.0', port=5001, debug=True)



