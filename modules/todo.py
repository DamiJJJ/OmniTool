from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from models import Todo

todo_bp = Blueprint('todo', __name__, template_folder='../templates')

@todo_bp.route('/todo', methods=['GET', 'POST'])
def todo_list():
    if request.method == 'POST':
        task_description = request.form.get('task')
        if task_description:
            new_task = Todo(description=task_description)
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for('todo.todo_list'))
    
    todos = Todo.query.all()
    return render_template('todo.html', todos=todos)

@todo_bp.route('/todo/complete/<int:task_id>')
def complete_todo(task_id):
    task = Todo.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('todo.todo_list'))

@todo_bp.route('/todo/delete/<int:task_id>')
def delete_todo(task_id):
    task = Todo.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('todo.todo_list'))