from flask import Flask, render_template_string, request, redirect, flash
import base64

app = Flask(__name__)
app.secret_key = "secret123"

# In-memory storage
reports = []

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"
SECURITY_QUESTION = "What is your favorite city?"
SECURITY_ANSWER = "Gorakhpur"


# ---------------- HEADER ----------------

HEADER = """
<header class="bg-gradient-to-r from-black via-blue-900 to-blue-700 shadow-xl">
<div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center text-white">

<h1 class="text-2xl font-bold">🚧 RoadCare Portal</h1>

<nav class="space-x-6 text-sm font-semibold">
<a href="/" class="hover:text-blue-300">Home</a>
<a href="/login" class="hover:text-blue-300">Admin</a>
</nav>

</div>
</header>
"""

# ---------------- FOOTER ----------------

FOOTER = """
<footer class="bg-gradient-to-r from-black via-blue-900 to-black text-gray-300 mt-10">

<div class="max-w-7xl mx-auto px-6 py-10 text-center">

<h2 class="text-xl font-bold text-white">
RoadCare Smart Feedback System
</h2>

<p class="text-sm mt-2 text-blue-200">
Empowering citizens to report road issues
</p>

<p class="text-xs text-gray-400 mt-6">
© 2026 RoadCare Portal
</p>

</div>

</footer>
"""

# ---------------- COMMON STYLE ----------------

STYLE = """
<script src="https://cdn.tailwindcss.com"></script>

<style>

@keyframes float{
0%{transform:translateY(0px);}
50%{transform:translateY(-6px);}
100%{transform:translateY(0px);}
}

.float-btn{
animation:float 3s ease-in-out infinite;
}

</style>
"""

# ---------------- HOME PAGE ----------------

FORM_TEMPLATE = HEADER + """
<!DOCTYPE html>
<html>
<head>
<title>Citizen Feedback</title>
""" + STYLE + """
</head>

<body class="min-h-screen flex flex-col bg-gradient-to-br from-black via-blue-900 to-blue-600 text-white">

<div class="flex-grow flex items-center justify-center">

<div class="bg-gray-900 p-8 rounded-xl shadow-xl border border-blue-500 w-96">

<h2 class="text-2xl font-bold mb-4 text-center">Report Road Issue</h2>

<form method="post" enctype="multipart/form-data" class="space-y-4">

<input name="name" placeholder="Your Name"
class="w-full p-2 bg-black border border-blue-500 rounded" required>

<input name="location" placeholder="Location"
class="w-full p-2 bg-black border border-blue-500 rounded" required>

<textarea name="description"
placeholder="Description"
class="w-full p-2 bg-black border border-blue-500 rounded"
required></textarea>

<input type="file" name="file" required>

<button class="float-btn w-full bg-gradient-to-r from-blue-600 to-blue-400 
hover:from-blue-700 hover:to-blue-500 text-white font-bold py-2 rounded-lg 
shadow-lg transform transition duration-300 
hover:scale-105 hover:shadow-blue-500/50 active:scale-95">

Submit Report

</button>

</form>

{% with messages = get_flashed_messages() %}
{% if messages %}
<div class="mt-3 text-green-400 text-center">
{{messages[0]}}
</div>
{% endif %}
{% endwith %}

<p class="text-center mt-3 text-sm">
Admin? <a href="/login" class="text-blue-300">Login</a>
</p>

</div>

</div>
""" + FOOTER + """

</body>
</html>
"""

# ---------------- LOGIN PAGE ----------------

LOGIN_TEMPLATE = HEADER + """
<!DOCTYPE html>
<html>
<head>
<title>Admin Login</title>
""" + STYLE + """
</head>

<body class="min-h-screen flex flex-col bg-gradient-to-br from-black via-blue-900 to-blue-600 text-white">

<div class="flex-grow flex items-center justify-center">

<div class="bg-gray-900 p-8 rounded-xl shadow-xl border border-blue-500 w-80">

<h2 class="text-xl font-bold text-center mb-4">Admin Login</h2>

<form method="post" class="space-y-4">

<input name="username" placeholder="Username"
class="w-full p-2 bg-black border border-blue-500 rounded" required>

<input type="password" name="password"
placeholder="Password"
class="w-full p-2 bg-black border border-blue-500 rounded" required>

<button class="float-btn w-full bg-gradient-to-r from-blue-700 to-black 
text-white py-2 rounded-lg shadow-lg transform transition duration-300 
hover:scale-105 hover:shadow-blue-400/50 active:scale-95">

Login

</button>

</form>

<p class="text-sm text-center mt-3">
<a href="/forgot" class="text-blue-300">Forgot password?</a>
</p>

{% with messages = get_flashed_messages() %}
{% if messages %}
<div class="text-red-400 text-center mt-3">
{{messages[0]}}
</div>
{% endif %}
{% endwith %}

</div>

</div>
""" + FOOTER + """

</body>
</html>
"""

# ---------------- DASHBOARD ----------------

DASHBOARD_TEMPLATE = HEADER + """
<!DOCTYPE html>
<html>
<head>
<title>Admin Dashboard</title>
""" + STYLE + """
</head>

<body class="min-h-screen flex flex-col bg-gradient-to-br from-black via-blue-900 to-blue-600 text-white">

<div class="flex-grow p-6">

<div class="bg-gray-900 p-6 rounded-xl shadow border border-blue-500">

<h2 class="text-2xl font-bold mb-4">Admin Dashboard</h2>

{% with messages = get_flashed_messages() %}
{% if messages %}
<div class="text-green-400 mb-3">
{{messages[0]}}
</div>
{% endif %}
{% endwith %}

<table class="w-full border border-blue-500">

<tr class="bg-gradient-to-r from-black to-blue-800">
<th class="p-2">Name</th>
<th class="p-2">Location</th>
<th class="p-2">Description</th>
<th class="p-2">Image</th>
<th class="p-2">Action</th>
</tr>

{% for report in reports %}

<tr class="border border-blue-500">

<td class="p-2">{{report.name}}</td>
<td class="p-2">{{report.location}}</td>
<td class="p-2">{{report.description}}</td>

<td class="p-2">
{% if report.image_data %}
<a target="_blank"
href="data:image/png;base64,{{report.image_data}}"
class="text-blue-300 underline">
View
</a>
{% endif %}
</td>

<td class="p-2">

<form action="/delete/{{loop.index0}}" method="post">

<button class="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-white 
transform transition duration-300 
hover:scale-110 hover:shadow-red-500/50 active:scale-95">

Delete

</button>

</form>

</td>

</tr>

{% endfor %}

</table>

</div>

</div>
""" + FOOTER + """

</body>
</html>
"""

# ---------------- ROUTES ----------------

@app.route("/", methods=["GET","POST"])
def index():

    if request.method == "POST":

        name = request.form["name"]
        location = request.form["location"]
        description = request.form["description"]

        file = request.files["file"]
        image_data = None

        if file:
            image_data = base64.b64encode(file.read()).decode()

        reports.append({
            "name":name,
            "location":location,
            "description":description,
            "image_data":image_data
        })

        flash("Report submitted successfully!")

        return redirect("/")

    return render_template_string(FORM_TEMPLATE)


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        if request.form["username"] == ADMIN_USERNAME and request.form["password"] == ADMIN_PASSWORD:
            return redirect("/dashboard")

        flash("Invalid username or password")

        return redirect("/login")

    return render_template_string(LOGIN_TEMPLATE)


@app.route("/dashboard")
def dashboard():

    return render_template_string(DASHBOARD_TEMPLATE, reports=reports)


@app.route("/delete/<int:report_id>", methods=["POST"])
def delete_report(report_id):

    if 0 <= report_id < len(reports):
        reports.pop(report_id)
        flash("Report deleted successfully!")

    return redirect("/dashboard")


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)

