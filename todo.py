from flask import Flask, render_template, request, redirect, session
import pg

db = pg.DB(dbname='todolist')

app = Flask('todolist')

# display tasks
@app.route('/')
def display():
    # only display if user is logged in
    if 'user' in session:
        tasks = db.query('''
            select
                tasks.id, tasks.name, tasks.user_id, tasks.complete
            from
                tasks
            inner join
                user_table on tasks.user_id = user_table.id
            where user_table.id = $1 order by tasks.complete, tasks.name''', session['user'])
        tasks_not_complete = db.query('''
            select
                count(tasks.id) as numtasks
            from
                tasks
            inner join
                user_table on tasks.user_id = user_table.id
            where tasks.complete = False and user_table.id = $1''', session['user'])

        return render_template('display.html',
            tasks = tasks.namedresult(),
            tasksnotcomplete = tasks_not_complete.namedresult(),
            title = 'ToDoList')
    else:
        return redirect('/login')

# display login form
@app.route('/login')
def login():
    return render_template('login.html', title="Login")

# process login
@app.route('/process_login', methods=['POST'])
def process_login():
    username = request.form['username']
    user = db.query('select id, username from user_table where username = $1', username).namedresult()
    if user:
        session['name'] = user[0].username
        session['user'] = user[0].id
        return redirect('/')
    else:
        return redirect('/login')

# add task
@app.route('/addtask', methods=['POST'])
def addtask():
    if 'user' in session:
        taskname = request.form['taskname']
        # insert into database
        db.insert('tasks', name=taskname, complete=False, user_id=session['user'])
        return redirect('/')
    else:
        return redirect('/login')

# mark task as complete, or delete task
@app.route('/processtasks', methods=['POST'])
def processtasks():
    if 'user' in session:
        # check to see if any tasks were selected
        if len(request.form) >= 2:
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
    else:
        return redirect('/login')

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

# Secret key for session
app.secret_key = 'CSF686CCF85C6FRTCHQDBJDXHBHC1G478C86GCFTDCR'

if __name__ == "__main__":
    app.debug = True
    app.run(debug=True)
