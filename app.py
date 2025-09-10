from flask import Flask, render_template_string, request, redirect, url_for, flash
import base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# In-memory data storage (clears on restart)
reports = []

# Hard-coded credentials for demonstration
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"
SECURITY_QUESTION = "What is your favorite city?"
SECURITY_ANSWER = "Gorakhpur"

# --- HTML Templates ---

# Main user feedback form and success message
FORM_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Road Maintenance Feedback</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f0f4f8; }
        .modal { transition: opacity 0.3s ease, visibility 0.3s ease; }
        .modal-content { transform: scale(0.95); transition: transform 0.3s ease; }
        .modal-open .modal-content { transform: scale(1); }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">

    <div id="main-form" class="bg-white p-8 rounded-2xl shadow-xl max-w-lg w-full">
        <h1 class="text-3xl font-bold text-center text-gray-800 mb-6">Citizen Feedback Form</h1>
        <p class="text-center text-gray-500 mb-8">Report issues to help improve our roads.</p>

        <form action="/" method="post" enctype="multipart/form-data" class="space-y-6">
            <div>
                <label for="name" class="block text-gray-700 font-semibold mb-2">Your Name</label>
                <input type="text" id="name" name="name" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Enter your name" required>
            </div>
            <div>
                <label for="location" class="block text-gray-700 font-semibold mb-2">Location</label>
                <input type="text" id="location" name="location" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g., Main St, Sector 15" required>
            </div>
            <div>
                <label for="description" class="block text-gray-700 font-semibold mb-2">Description of Issue</label>
                <textarea id="description" name="description" rows="4" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Describe the issue in detail" required></textarea>
            </div>
            <div>
                <label for="file" class="block text-gray-700 font-semibold mb-2">Upload Image</label>
                <input type="file" id="file" name="file" accept="image/*" class="w-full text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" required>
            </div>
            <button type="submit" class="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-colors">Submit Report</button>
        </form>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="mt-6">
                {% for category, message in messages %}
                    {% if category == 'success' %}
                        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative" role="alert">
                            <span class="block sm:inline">{{ message }}</span>
                        </div>
                    {% endif %}
                {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        <p class="text-sm text-center text-gray-400 mt-6">
            Are you an admin?
            <a href="/login" class="text-blue-500 hover:underline">Log in here</a>
        </p>
    </div>
</body>
</html>
"""

# Admin login form
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style> body { font-family: 'Inter', sans-serif; background-color: #f0f4f8; } </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">
    <div class="bg-white p-8 rounded-2xl shadow-xl max-w-sm w-full">
        <h3 class="text-2xl font-bold text-center text-gray-800 mb-6">Admin Login</h3>
        <form action="/login" method="post" class="space-y-4">
            <div>
                <label for="admin-user" class="block text-gray-700 font-semibold mb-2">Username</label>
                <input type="text" id="admin-user" name="username" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
            </div>
            <div>
                <label for="admin-pass" class="block text-gray-700 font-semibold mb-2">Password</label>
                <input type="password" id="admin-pass" name="password" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
            </div>
            <button type="submit" class="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors">Login</button>
        </form>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    {% if category == 'error' %}
                        <div class="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                            <span class="block sm:inline">{{ message }}</span>
                        </div>
                    {% endif %}
                {% endfor %}
            {% endif %}
        {% endwith %}
        <p class="text-sm text-center text-gray-400 mt-4">
            <a href="/forgot" class="text-blue-500 hover:underline">Forgot password?</a>
        </p>
    </div>
</body>
</html>
"""

# Forgot password page
FORGOT_PASSWORD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Forgot Password</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style> body { font-family: 'Inter', sans-serif; background-color: #f0f4f8; } </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">
    <div class="bg-white p-8 rounded-2xl shadow-xl max-w-sm w-full">
        <h3 class="text-2xl font-bold text-center text-gray-800 mb-6">Forgot Password</h3>
        <p class="text-center text-gray-600 mb-4">
            Please enter the security answer to reset your password.
        </p>
        <p class="text-center text-gray-800 font-semibold mb-4">
            {{ security_question }}
        </p>
        <form action="/forgot" method="post" class="space-y-4">
            <div>
                <input type="text" id="security-answer" name="answer" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
            </div>
            <button type="submit" class="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors">Submit</button>
        </form>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    {% if category == 'error' %}
                        <div class="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                            <span class="block sm:inline">{{ message }}</span>
                        </div>
                    {% endif %}
                {% endfor %}
            {% endif %}
        {% endwith %}
        <p class="text-sm text-center text-gray-400 mt-4">
            <a href="/login" class="text-blue-500 hover:underline">Back to Login</a>
        </p>
    </div>
</body>
</html>
"""

# Admin dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style> body { font-family: 'Inter', sans-serif; background-color: #f0f4f8; } </style>
</head>
<body class="p-4">
    <div class="bg-white p-8 rounded-2xl shadow-xl max-w-full lg:max-w-6xl mx-auto flex flex-col min-h-screen">
        <div class="flex-shrink-0">
            <h3 class="text-2xl font-bold text-gray-800 mb-4">Admin Dashboard</h3>
            <p class="text-gray-500 mb-6">List of all submitted road maintenance reports.</p>
        </div>
        
        <div class="overflow-x-auto overflow-y-auto flex-grow rounded-lg border border-gray-200">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Image</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    {% for report in reports %}
                    <tr class="hover:bg-gray-100 transition-colors">
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ report.get('name', 'N/A') }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ report.get('location', 'N/A') }}</td>
                        <td class="px-6 py-4 text-sm text-gray-500">{{ report.get('description', 'N/A') }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-blue-500">
                            {% if report.get('image_data') %}
                                <a href="data:image/png;base64,{{ report.get('image_data') }}" target="_blank" class="hover:underline">View Image</a>
                            {% else %}
                                No Image
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="flex-shrink-0 mt-6 flex justify-end">
            <form action="/dashboard/submit_action" method="post">
                <button type="submit" class="bg-blue-600 text-white font-bold py-2 px-6 rounded-lg hover:bg-blue-700 transition-colors">Submit Changes</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# --- Flask Routes ---

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        location = request.form.get("location")
        description = request.form.get("description")
        
        file = request.files.get("file")
        image_data = None
        if file and file.filename != '':
            # Read image data and encode it in base64
            image_stream = BytesIO(file.read())
            image_data = base64.b64encode(image_stream.getvalue()).decode('utf-8')

        report = {
            "name": name,
            "location": location,
            "description": description,
            "image_data": image_data
        }
        reports.append(report)
        flash("✅ Thank you for your response! Your issue has been reported.", 'success')
        return redirect(url_for('index'))
    return render_template_string(FORM_TEMPLATE)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", 'error')
            return redirect(url_for('login'))
    return render_template_string(LOGIN_TEMPLATE)

@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        answer = request.form.get("answer")
        if answer.lower() == SECURITY_ANSWER.lower():
            flash(f"Your new password is: {ADMIN_PASSWORD}", 'success')
            return redirect(url_for('login'))
        else:
            flash("Incorrect answer.", 'error')
            return redirect(url_for('forgot_password'))
    return render_template_string(FORGOT_PASSWORD_TEMPLATE, security_question=SECURITY_QUESTION)

@app.route("/dashboard")
def dashboard():
    return render_template_string(DASHBOARD_TEMPLATE, reports=reports)

@app.route("/dashboard/submit_action", methods=["POST"])
def dashboard_submit_action():
    flash("Admin action submitted! This button can be linked to process reports or save changes.", 'success')
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)
