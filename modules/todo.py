import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from extensions import db
from models import Todo
from forms import TodoForm

logger = logging.getLogger(__name__)

todo_bp = Blueprint("todo", __name__, template_folder="../templates")


def _get_user_task_or_403(task_id):
    """Pobiera zadanie należące do bieżącego użytkownika lub zwraca 404/403."""
    task = db.get_or_404(Todo, task_id)
    if task.user_id != current_user.id:
        abort(403)
    return task


@todo_bp.route("/todo", methods=["GET", "POST"])
@login_required
def todo_list():
    form = TodoForm()

    if form.validate_on_submit():
        try:
            new_task = Todo(
                description=form.description.data,
                user_id=current_user.id,
                deadline=form.deadline.data,
                priority=form.priority.data,
            )
            db.session.add(new_task)
            db.session.commit()
            flash("Task added successfully!", "success")
        except Exception as e:
            logger.exception("Error adding task")
            flash(f"Error adding task: {e}", "danger")
            db.session.rollback()
        return redirect(url_for("todo.todo_list"))

    todos = (
        Todo.query.filter_by(user_id=current_user.id)
        .order_by(Todo.date_created.desc())
        .all()
    )
    return render_template("todo.html", todos=todos, form=form)


@todo_bp.route("/todo/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_todo(task_id):
    task = _get_user_task_or_403(task_id)
    form = TodoForm()

    if form.validate_on_submit():
        task.description = form.description.data
        task.completed = form.completed.data
        task.deadline = form.deadline.data
        task.priority = form.priority.data
        try:
            db.session.commit()
            flash("Task updated successfully!", "success")
            return redirect(url_for("todo.todo_list"))
        except Exception as e:
            logger.exception("Error updating task")
            flash(f"Error updating task: {e}", "danger")
            db.session.rollback()
    elif request.method == "GET":
        form.description.data = task.description
        form.completed.data = task.completed
        form.deadline.data = task.deadline
        form.priority.data = task.priority

    return render_template(
        "edit_todo.html", title="Edit Task", form=form, task_id=task.id
    )


@todo_bp.route("/todo/complete/<int:task_id>", methods=["POST"])
@login_required
def complete_todo(task_id):
    task = _get_user_task_or_403(task_id)
    try:
        task.completed = not task.completed
        db.session.commit()
        flash("Task status updated!", "success")
    except Exception as e:
        logger.exception("Error updating task status")
        flash(f"Error updating task status: {e}", "danger")
        db.session.rollback()
    return redirect(url_for("todo.todo_list"))


@todo_bp.route("/todo/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_todo(task_id):
    task = _get_user_task_or_403(task_id)
    try:
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted successfully!", "success")
    except Exception as e:
        logger.exception("Error deleting task")
        flash(f"Error deleting task: {e}", "danger")
        db.session.rollback()
    return redirect(url_for("todo.todo_list"))
