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
        tasks = create_task_list(request.form, 'markcomplete')
        query = "update tasks set complete = True where id in (%s)" % create_db_in_string(tasks)
        db.query(query, *tasks)

    # if we're deleting tasks
    if 'deletetasks' in request.form:
        tasks = create_task_list(request.form, 'deletetasks')
        query = "delete from tasks where id in (%s)" % create_db_in_string(tasks)
        db.query(query, *tasks)
        # old way:
        # for task in request.form:
        #     if task == 'deletetasks':
        #         continue
        #     tasks.append(int(task))
        #     task = int(task)
        #     db.delete('tasks', {'id': task})

    # if we're marking tasks as NOT complete
    if 'marknotcomplete' in request.form:
        tasks = create_task_list(request.form, 'marknotcomplete')
        query = "update tasks set complete = False where id in (%s)" % create_db_in_string(tasks)
        db.query(query, *tasks)

    return redirect('/')

def create_task_list(request_form, action):
    tasks = []
    for task in request_form:
        if task == action:
            continue
        tasks.append(int(task))
    return tasks

def create_db_in_string(tasks):
    string = ''
    for i in xrange(0, len(tasks)):
        string += "$" + str(i + 1) + ", "
    return string.strip(', ')


if __name__ == "__main__":
    app.debug = True
    app.run(debug=True)
