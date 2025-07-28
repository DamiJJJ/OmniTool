from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Todo
from forms import TodoForm

todo_bp = Blueprint("todo", __name__, template_folder="../templates")


@todo_bp.route("/todo", methods=["GET", "POST"])
@login_required
def todo_list():
    form = TodoForm()

    if form.validate_on_submit():
        task_description = form.description.data
        try:
            new_task = Todo(description=task_description, user_id=current_user.id)
            db.session.add(new_task)
            db.session.commit()
            flash("Task added successfully!", "success")
        except Exception as e:
            flash(f"Error adding task: {e}", "danger")
            db.session.rollback()

        return redirect(url_for("todo.todo_list"))

    todos = (
        Todo.query.filter_by(user_id=current_user.id)
        .order_by(Todo.date_created.desc())
        .all()
    )
    return render_template("todo.html", todos=todos, form=form)


# --- Task Edition --- #
@todo_bp.route("/todo/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_todo(task_id):
    task = Todo.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash("You are not authorized to edit this task.", "danger")
        return redirect(url_for("todo.todo_list"))

    form = TodoForm()

    if form.validate_on_submit():
        task.description = form.description.data
        task.completed = form.completed.data
        try:
            db.session.commit()
            flash("Task updated successfully!", "success")
            return redirect(url_for("todo.todo_list"))
        except Exception as e:
            flash(f"Error updating task: {e}", "danger")
            db.session.rollback()
    elif request.method == "GET":
        form.description.data = task.description
        form.completed.data = task.completed

    return render_template(
        "edit_todo.html", title="Edit Task", form=form, task_id=task.id
    )


# --- Task Completion --- #
@todo_bp.route("/todo/complete/<int:task_id>")
@login_required
def complete_todo(task_id):
    task = Todo.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash("You are not authorized to complete this task.", "danger")
        return redirect(url_for("todo.todo_list"))
    try:
        task.completed = not task.completed
        db.session.commit()
        flash("Task status updated!", "success")
    except Exception as e:
        flash(f"Error updating task status: {e}", "danger")
        db.session.rollback()
    return redirect(url_for("todo.todo_list"))


@todo_bp.route("/todo/delete/<int:task_id>")
@login_required
def delete_todo(task_id):
    task = Todo.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash("You are not authorized to delete this task.", "danger")
        return redirect(url_for("todo.todo_list"))
    try:
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting task: {e}", "danger")
        db.session.rollback()
    return redirect(url_for("todo.todo_list"))
