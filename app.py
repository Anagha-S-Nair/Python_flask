from flask import Flask, render_template, redirect, url_for, request, session, flash
import uuid

app = Flask(__name__)
app.secret_key = "replace-with-a-long-random-secret-key"


# -------------------------------------------------
# Helper: ensure todos exist in session
# -------------------------------------------------
def ensure_todos():
    if "todos" not in session:
        session["todos"] = []


# -------------------------------------------------
# Home / Landing
# -------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------------------------
# Registration (Username only)
# Redirects straight to /todos — NO LOGIN REQUIRED
# -------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()

        if not username:
            flash("Name is required.", "danger")
            return render_template("register.html")

        # Store username in session
        session["user"] = username

        # Initialize todos
        ensure_todos()

        flash("Welcome! Your account is ready.", "success")
        return redirect(url_for("todos"))

    return render_template("register.html")


# -------------------------------------------------
# Todo Page (No login required anymore)
# -------------------------------------------------
@app.route("/todos")
def todos():
    # If user not registered, force them to register first
    if "user" not in session:
        return redirect(url_for("register"))

    ensure_todos()
    return render_template("todos.html", todos=session["todos"], user=session["user"])


@app.route("/todos/add", methods=["POST"])
def add_todo():
    if "user" not in session:
        return redirect(url_for("register"))

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
def toggle(tid):
    if "user" not in session:
        return redirect(url_for("register"))

    ensure_todos()
    todos = session["todos"]

    for t in todos:
        if t["id"] == tid:
            t["done"] = True
            session["todos"] = todos
            break

    return redirect(url_for("todos"))


@app.route("/todos/delete/<tid>", methods=["POST"])
def delete(tid):
    if "user" not in session:
        return redirect(url_for("register"))

    ensure_todos()
    session["todos"] = [t for t in session["todos"] if t["id"] != tid]
    return redirect(url_for("todos"))


@app.route("/todos/export")
def export():
    if "user" not in session:
        return redirect(url_for("register"))

    ensure_todos()
    return {"todos": session["todos"]}


# -------------------------------------------------
# Run App
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
