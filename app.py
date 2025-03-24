from flask import Flask, request, render_template_string
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import os

app = Flask(__name__)

# HTML template for the input form
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Bar Chart Generator</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
        form { display: inline-block; margin-top: 20px; }
        input { margin: 5px; padding: 8px; width: 300px; }
        button { padding: 10px 20px; background-color: #007BFF; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        img { margin-top: 20px; max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <h1>Bar Chart Generator</h1>
    <form method="POST">
        <input type="text" name="categories" placeholder="Enter categories (comma-separated)" required><br>
        <input type="text" name="values" placeholder="Enter values (comma-separated)" required><br>
        <input type="text" name="widths" placeholder="Enter widths (comma-separated)" required><br>
        <button type="submit">Generate Chart</button>
    </form>
    {% if chart %}
    <h2>Generated Bar Chart:</h2>
    <img src="data:image/png;base64,{{ chart }}" alt="Bar Chart">
    {% endif %}
</body>
</html>
"""

# Route to display the form and generate the chart
@app.route("/", methods=["GET", "POST"])
def index():
    chart = None

    if request.method == "POST":
        try:
            # Get user inputs from the form
            categories = request.form["categories"].split(",")
            values = list(map(float, request.form["values"].split(",")))
            widths = list(map(float, request.form["widths"].split(",")))

            # Validate that inputs have the same length
            if len(categories) != len(values) or len(categories) != len(widths):
                return "Error: The number of categories, values, and widths must be the same."

            # Adjust the x positions so bars touch each other
            x_positions = np.cumsum([0] + widths[:-1])

            # Generate the bar chart
            plt.figure(figsize=(10, 6))
            plt.bar(x_positions, values, width=widths, color='skyblue', align='edge')
            plt.xticks(x_positions + np.array(widths) / 2, categories)
            plt.title("Bar Chart with Touching Variable Widths")
            plt.xlabel("Categories")
            plt.ylabel("Values")

            # Add labels on top of each bar
            for x, y, w in zip(x_positions, values, widths):
                plt.text(x + w / 2, y + (1 if y > 0 else -2), str(y), ha="center", fontsize=10)

            # Save the chart to a BytesIO object and encode as base64
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            chart = base64.b64encode(buf.getvalue()).decode("utf-8")
            buf.close()
            plt.close()
        except Exception as e:
            return f"Error processing your input: {e}"

    return render_template_string(HTML_TEMPLATE, chart=chart)

# Run the application
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Use environment variable for deployment
    app.run(host="0.0.0.0", port=port, debug=True)
