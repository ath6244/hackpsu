from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import pytz
import requests
from datetime import datetime, timezone

app = Flask(__name__)

ACCESS_TOKEN = "1050~KGMRBP6xtQaEB9KK2Qhk4KQMFyvX2T8LazKHznEyKuNJEF38W3FXYuJuMV7TK48W"
CANVAS_DOMAIN = "https://psu.instructure.com"
HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

CORS(app)

# Only include assignments due between these dates
SEMESTER_START = datetime(2025, 8, 25, tzinfo=timezone.utc)
SEMESTER_END = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
NY_TZ = pytz.timezone("America/New_York")

HTML_TEMPLATE = """
<h1>Fall 2025 Courses & Assignments</h1>
{% if error %}
    <p style="color:red;">Error: {{ error }}</p>
{% endif %}
<ul>
{% for course in courses %}
    <li>
        <strong>{{ course['name'] }}</strong>
        <ul>
        {% for assignment in course.get('assignments', []) %}
            <li>{{ assignment['name'] }} - Due: {{ assignment.get('due_at', 'N/A') }}</li>
        {% endfor %}
        </ul>
    </li>
{% endfor %}
</ul>
"""

def get_all_pages(url):
    results = []
    while url:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Request failed: {response.status_code} -> {response.text[:100]}")
            break
        try:
            data = response.json()
            if isinstance(data, list):
                results.extend(data)
            else:
                print("Unexpected data format:", data)
                break
        except ValueError:
            print("Failed to parse JSON.")
            break

        links = response.links
        url = links.get("next", {}).get("url") if links else None
    return results

def parse_date(date_str):
    """Parse Canvas date (ISO 8601) safely as timezone-aware UTC datetime."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def assignments_due_on(target_date):
    """Return list of assignments due on the given date (date object) in NY_TZ."""
    results = []
    try:
        course_url = f"{CANVAS_DOMAIN}/api/v1/users/self/courses?per_page=100"
        all_courses = get_all_pages(course_url)

        for course in all_courses:
            course_id = course.get("id")
            if not course_id:
                continue

            assign_url = f"{CANVAS_DOMAIN}/api/v1/courses/{course_id}/assignments?per_page=100"
            assign_data = get_all_pages(assign_url)

            for a in assign_data:
                if not isinstance(a, dict):
                    continue
                due = parse_date(a.get("due_at"))
                if due is None:
                    continue
                # convert due to NY timezone for date comparison
                due_ny = due.astimezone(NY_TZ)
                if due_ny.date() == target_date:
                    results.append({
                        "course_id": course_id,
                        "course_name": course.get("name"),
                        "assignment_id": a.get("id"),
                        "name": a.get("name"),
                        "due_at": a.get("due_at"),
                        "html_url": a.get("html_url"),
                    })
    except requests.exceptions.RequestException:
        # Let caller handle empty/failed responses
        pass

    return results

@app.route("/")
def home():
    error = None
    courses = []

    try:
        # Get all courses
        course_url = f"{CANVAS_DOMAIN}/api/v1/users/self/courses?per_page=100"
        all_courses = get_all_pages(course_url)

        for course in all_courses:
            course_id = course.get("id")
            if not course_id:
                continue

            assign_url = f"{CANVAS_DOMAIN}/api/v1/courses/{course_id}/assignments?per_page=100"
            assign_data = get_all_pages(assign_url)

            # Filter assignments by due date range
            filtered_assignments = []
            for a in assign_data:
                if not isinstance(a, dict):
                    continue
                due = parse_date(a.get("due_at"))
                if due and SEMESTER_START <= due <= SEMESTER_END:
                    filtered_assignments.append(a)

            # Only include courses that actually have assignments in this window
            if filtered_assignments:
                course["assignments"] = filtered_assignments
                courses.append(course)

    except requests.exceptions.RequestException as e:
        error = f"Connection error: {e}"

    return render_template_string(HTML_TEMPLATE, courses=courses, error=error)


@app.route("/api/assignments/today")
def api_assignments_today():
    """Return JSON list of assignments due for a given date (query param `date=YYYY-MM-DD`) or today in NY timezone."""
    date_str = request.args.get("date")
    if date_str:
        try:
            target_date = datetime.fromisoformat(date_str).date()
        except Exception:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    else:
        target_date = datetime.now(NY_TZ).date()

    assignments = assignments_due_on(target_date)
    return jsonify({"date": target_date.isoformat(), "assignments": assignments})


@app.route('/api/assignments/<int:course_id>/<int:assignment_id>/complete', methods=['POST'])
def api_mark_assignment_complete(course_id, assignment_id):
    """Mark an assignment as submitted for the current user by creating a simple online_text_entry submission.

    This uses the Canvas submissions API and requires the provided ACCESS_TOKEN to have student permissions.
    """
    try:
        submit_url = f"{CANVAS_DOMAIN}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions"
        payload = {
            "submission[submission_type]": "online_text_entry",
            "submission[body]": f"Marked complete via app on {datetime.now(NY_TZ).isoformat()}"
        }
        resp = requests.post(submit_url, headers=HEADERS, data=payload, timeout=10)
        if resp.status_code in (200, 201):
            return jsonify({"success": True, "message": "Assignment marked complete."})
        else:
            return jsonify({"success": False, "status_code": resp.status_code, "detail": resp.text}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
