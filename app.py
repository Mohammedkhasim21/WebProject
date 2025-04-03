from flask import Flask, request, render_template_string, redirect, url_for, session
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import os
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Secret key for session management

# Simulated user database (for demonstration purposes)
users = {"admin": "password123"}

# HTML template for login and registration
AUTH_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <title>Login / Register</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        form { display: inline-block; text-align: left; }
        input, button { display: block; margin-top: 10px; }
    </style>
</head>
<body>
    <h2>{{ title }}</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Submit</button>
    </form>
    <p>{{ message }}</p>
</body>
</html>
"""

# HTML template for the input form
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Marginal Abatement Cost Curve (MACC)</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; }
        form { display: inline-block; margin-top: 20px; text-align: left; }
        input, button { display: block; margin-top: 5px; padding: 8px; width: 300px; }
        button { background-color: #007BFF; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        img { margin-top: 20px; max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <h1>Marginal Abatement Cost Curve (MACC)</h1>
    <form method="POST">
        <input type="text" name="project_name" placeholder="Project Name" required><br>
        <input type="text" name="categories" placeholder="Enter categories (comma-separated)" required><br>
        <input type="text" name="values" placeholder="Enter MACC Value (USD/Tonne)" required><br>
        <input type="text" name="widths" placeholder="Enter Abatement Value (Tonne)" required><br>
        <button type="submit">Generate Chart</button>
    </form>
    {% if chart %}
    <h2>Generated MACC Chart:</h2>
    <img src="data:image/png;base64,{{ chart }}" alt="MACC Chart">
    {% endif %}
</body>
</html>
"""

# Authentication Routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("index"))
        return render_template_string(AUTH_TEMPLATE, title="Login", message="Invalid credentials.")
    return render_template_string(AUTH_TEMPLATE, title="Login", message="")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users:
            return render_template_string(AUTH_TEMPLATE, title="Register", message="User already exists.")
        users[username] = password
        return redirect(url_for("login"))
    return render_template_string(AUTH_TEMPLATE, title="Register", message="")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# Route to display the form and generate the chart
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    
    chart = None
    if request.method == "POST":
        try:
            project_name = request.form["project_name"]
            categories = request.form["categories"].split(",")
            values = list(map(float, request.form["values"].split(",")))
            widths = list(map(float, request.form["widths"].split(",")))

            if len(categories) != len(values) or len(categories) != len(widths):
                return "Error: The number of categories, values, and widths must be the same."

            x_positions = np.cumsum([0] + widths[:-1])
            colors = ["#" + ''.join(random.choices('0123456789ABCDEF', k=6)) for _ in range(len(categories))]

            plt.figure(figsize=(10, 6))
            plt.bar(x_positions, values, width=widths, color=colors, edgecolor='black', align='edge')
            plt.xticks(x_positions + np.array(widths) / 2, categories, rotation=90)
            plt.title(f"Marginal Abatement Cost Curve (MACC) - {project_name}")
            plt.xlabel("Categories")
            plt.ylabel("MACC Value (USD/Tonne)")
            
            for x, y, w in zip(x_positions, values, widths):
                plt.text(x + w / 2, y + (1 if y > 0 else -2), f"{y}\n({w})", ha="center", fontsize=10)

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            chart = base64.b64encode(buf.getvalue()).decode("utf-8")
            buf.close()
            plt.close()
        except Exception as e:
            return f"Error processing your input: {e}"

    return render_template_string(HTML_TEMPLATE, chart=chart)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
