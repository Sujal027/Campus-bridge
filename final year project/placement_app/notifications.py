from flask import Blueprint,abort,flash,redirect,render_template,request,url_for
from .auth import get_current_user
from .database import get_db
from .security import login_required
from .services import create_notification

bp=Blueprint("notifications",__name__)

@bp.route("/notifications",methods=["GET","POST"])
@login_required()
def index():
    user=get_current_user()
    connection=get_db()
    if request.method=="POST":
        if user["role"]!="admin":
            abort(403)
        message=request.form.get("message","").strip()
        if not message:
            flash("Enter an announcement before sending.","error")
        elif len(message)>500:
            flash("Announcements must be 500 characters or fewer.","error")
        else:
            students=connection.execute("SELECT id FROM users WHERE role='student'").fetchall()
            for student in students:
                create_notification(student["id"],message)
            flash(f"Announcement sent to {len(students)} students.","success")
            return redirect(url_for("notifications.index"))
    if user["role"]=="student":
        notifications=connection.execute(
            "SELECT * FROM notifications WHERE student_id=? ORDER BY created DESC",
            (user["id"],),
        ).fetchall()
        connection.execute("UPDATE notifications SET read=1 WHERE student_id=?",(user["id"],))
        connection.commit()
    else:
        notifications=connection.execute(
            """SELECT n.*,u.name FROM notifications n JOIN users u ON u.id=n.student_id
               ORDER BY n.created DESC LIMIT 100"""
        ).fetchall()
    return render_template("shared/notifications.html",notifications=notifications)

@bp.post("/notifications/<int:notification_id>/delete")
@login_required("student")
def delete(notification_id):
    connection=get_db()
    result=connection.execute(
        "DELETE FROM notifications WHERE id=? AND student_id=?",
        (notification_id,get_current_user()["id"]),
    )
    connection.commit()
    if not result.rowcount:
        abort(404)
    flash("Notification deleted.","success")
    return redirect(url_for("notifications.index"))
