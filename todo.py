from flask import Flask, render_template, request, redirect
import pg

db = pg.DB(dbname='todolist')

app = Flask('todolist')

# display tasks
@app.route('/')
def display():
    tasks = db.query('select * from tasks order by complete, name')
    tasks_not_complete = db.query('select count(id) as numtasks from tasks where complete = False')

    return render_template('display.html',
        tasks = tasks.namedresult(),
        tasksnotcomplete = tasks_not_complete.namedresult(),
        title = 'ToDoList')

# add task
@app.route('/addtask', methods=['POST'])
def addtask():
    taskname = request.form['taskname']
    # insert into database
    db.insert('tasks', name=taskname, complete=False)
    return redirect('/')

# mark task as complete, or delete task
@app.route('/processtasks', methods=['POST'])
def processtasks():
    # if we're marking tasks as complete
    if 'markcomplete' in request.form:
        for task in request.form:
            if task == 'markcomplete':
                continue
            task = int(task)
            db.update('tasks', {'id': task, 'complete': True})

    # if we're deleting tasks
    if 'deletetasks' in request.form:
        for task in request.form:
            if task == 'deletetasks':
                continue
            task = int(task)
            db.delete('tasks', {'id': task})

    # if we're marking tasks as not complete from complete
    if 'marknotcomplete' in request.form:
        for task in request.form:
            if task == 'marknotcomplete':
                continue
            task = int(task)
            db.update('tasks', {'id': task, 'complete': False})

    return redirect('/')

if __name__ == "__main__":
    app.debug = True
    app.run(debug=True)
