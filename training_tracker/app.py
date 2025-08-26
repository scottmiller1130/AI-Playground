
import csv
import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_FILE = os.path.join(os.getcwd(), 'data', 'workouts.csv')

# Ensure data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
    writer.writerow(['id', 'date', 'type', 'distance_miles', 'duration', 'exercises', 'notes'])

@app.route('/')
def dashboard():
    workouts = []
    with open(DATA_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            workouts.append(row)
    total_workouts = len(workouts)
    total_distance = sum(float(w['distance_miles']) for w in workouts if w.get('distance_miles'))
    return render_template('dashboard.html', workouts=workouts, total_workouts=total_workouts, total_distance=total_distance)

@app.route('/log')
def workout_log():
    workouts = []
    with open(DATA_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            workouts.append(row)
    return render_template('log.html', workouts=workouts)

@app.route('/add', methods=['GET', 'POST'])
def add_workout():
    if request.method == 'POST':
        exercises = []
        if request.form['type'] in ['Strength', 'Hybrid']:
            # Parse exercises from form
            exercise_names = request.form.getlist('exercise_name')
            sets = request.form.getlist('sets')
            reps = request.form.getlist('reps')
            weights = request.form.getlist('weight_lbs')
            ex_notes = request.form.getlist('exercise_notes')
            for i in range(len(exercise_names)):
                if exercise_names[i]:
                    exercises.append({
                        'name': exercise_names[i],
                        'sets': sets[i],
                        'reps': reps[i],
                        'weight_lbs': weights[i],
                        'notes': ex_notes[i]
                    })
        with open(DATA_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                request.form.get('id', ''),
                request.form['date'],
                request.form['type'],
                request.form.get('distance_miles', ''),
                request.form.get('duration', ''),
                json.dumps(exercises),
                request.form.get('notes', '')
            ])
        return redirect(url_for('workout_log'))
    return render_template('add.html')

@app.route('/edit/<int:idx>', methods=['GET', 'POST'])
def edit_workout(idx):
    workouts = []
    with open(DATA_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            workouts.append(row)
    if request.method == 'POST':
        # Update the workout
        workouts[idx]['date'] = request.form['date']
        workouts[idx]['type'] = request.form['type']
        workouts[idx]['distance_miles'] = request.form.get('distance_miles', '')
        workouts[idx]['duration'] = request.form.get('duration', '')
        exercises = []
        if request.form['type'] in ['Strength', 'Hybrid']:
            exercise_names = request.form.getlist('exercise_name')
            sets = request.form.getlist('sets')
            reps = request.form.getlist('reps')
            weights = request.form.getlist('weight_lbs')
            ex_notes = request.form.getlist('exercise_notes')
            for i in range(len(exercise_names)):
                if exercise_names[i]:
                    exercises.append({
                        'name': exercise_names[i],
                        'sets': sets[i],
                        'reps': reps[i],
                        'weight_lbs': weights[i],
                        'notes': ex_notes[i]
                    })
        workouts[idx]['exercises'] = json.dumps(exercises)
        workouts[idx]['notes'] = request.form.get('notes', '')
        # Write back to CSV
        with open(DATA_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=workouts[0].keys())
            writer.writeheader()
            writer.writerows(workouts)
        return redirect(url_for('workout_log'))
    workout = workouts[idx]
    # Parse exercises for editing
    if workout['type'] in ['Strength', 'Hybrid'] and workout.get('exercises'):
        workout['exercises'] = json.loads(workout['exercises'])
    else:
        workout['exercises'] = []
    return render_template('edit.html', workout=workout, idx=idx)

@app.route('/delete/<int:idx>')
def delete_workout(idx):
    workouts = []
    with open(DATA_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            workouts.append(row)
    if 0 <= idx < len(workouts):
        del workouts[idx]
        with open(DATA_FILE, 'w', newline='') as f:
            if workouts:
                writer = csv.DictWriter(f, fieldnames=workouts[0].keys())
                writer.writeheader()
                writer.writerows(workouts)
            else:
                writer = csv.writer(f)
                writer.writerow(['id', 'date', 'type', 'distance', 'duration', 'notes'])
    return redirect(url_for('workout_log'))

@app.route('/analytics')
def analytics():
    # Placeholder for analytics
    return render_template('analytics.html')

if __name__ == '__main__':
    app.run(debug=True)
