import csv
import json

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLAlchemy for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workouts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the Workout model
class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    workout_type = db.Column(db.String(50))
    exercises = db.Column(db.Text)  # JSON string storing exercise details

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Utility functions for loading workouts and processing analytics data


def load_workouts():
    workouts = Workout.query.all()
    workout_list = []
    for w in workouts:
        workout_list.append({
            'id': w.id,
            'date': w.date,
            'workout_type': w.workout_type,
            'exercises': w.exercises
        })
    return workout_list


def process_analytics(workouts):
    dates = []
    max_weights = []
    for w in workouts:
        dates.append(w.get('date'))
        max_weight = 0
        if w.get('exercises'):
            try:
                exercises = json.loads(w.get('exercises'))
                for ex in exercises:
                    weight_val = float(ex.get('weight', 0))
                    if weight_val > max_weight:
                        max_weight = weight_val
            except Exception as e:
                print(f'Error processing exercises: {e}')
        max_weights.append(max_weight)
    return {'dates': dates, 'max_weights': max_weights}

# Analytics route


@app.route('/analytics')
def analytics():
    workouts = load_workouts()
    analytics_data = process_analytics(workouts)
    return render_template('analytics.html', analytics=analytics_data)

# ...existing routes...