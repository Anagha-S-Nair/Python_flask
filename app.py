from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import uuid

app = Flask(__name__)
app.secret_key = "replace-with-a-long-random-secret-key"


# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def ensure_todos():
    if "todos" not in session:
        session["todos"] = []


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in to access your to-dos.", "info")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated


# -------------------------------------------------
# Home / Landing
# -------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------------------------
# Registration (Username + Password)
# -------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Both fields are required.", "danger")
            return render_template("register.html")

        # Save user in session
        session["registered_user"] = username
        session["registered_pass"] = password

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# -------------------------------------------------
# Login (Checks password)
# -------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    next_page = request.args.get("next", url_for("todos"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # No user registered
        if "registered_user" not in session:
            flash("No user registered. Please sign up first.", "warning")
            return redirect(url_for("register"))

        # Check login
        if username == session["registered_user"] and password == session["registered_pass"]:
            session["logged_in"] = True
            session["user"] = username
            ensure_todos()
            return redirect(next_page)

        flash("Incorrect username or password!", "danger")

    return render_template("login.html", next=next_page)


# -------------------------------------------------
# Logout
# -------------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("index"))


# -------------------------------------------------
# Todo Pages
# -------------------------------------------------
@app.route("/todos")
@login_required
def todos():
    ensure_todos()
    return render_template("todos.html", todos=session["todos"], user=session["user"])


@app.route("/todos/add", methods=["POST"])
@login_required
def add_todo():
    ensure_todos()
    title = request.form.get("title", "").strip()

    if title:
        task = {"id": str(uuid.uuid4()), "title": title, "done": False}
        todos = session["todos"]
        todos.insert(0, task)
        session["todos"] = todos
    else:
        flash("Please enter a task.", "danger")

    return redirect(url_for("todos"))


@app.route("/todos/toggle/<tid>", methods=["POST"])
@login_required
def toggle(tid):
    ensure_todos()
    todos = session["todos"]

    for t in todos:
        if t["id"] == tid:
            t["done"] = True
            session["todos"] = todos
            break

    return redirect(url_for("todos"))


@app.route("/todos/delete/<tid>", methods=["POST"])
@login_required
def delete(tid):
    ensure_todos()
    session["todos"] = [t for t in session["todos"] if t["id"] != tid]
    return redirect(url_for("todos"))


@app.route("/todos/export")
@login_required
def export():
    ensure_todos()
    return {"todos": session["todos"]}


if __name__ == "__main__":
    app.run(debug=True)