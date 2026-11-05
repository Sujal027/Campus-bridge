from flask import Blueprint,render_template
from .security import login_required
from .database import get_db
bp=Blueprint("reports",__name__,url_prefix="/admin/reports")
@bp.get("/")
@login_required("admin")
def index():
 c=get_db();total=c.execute("SELECT count(*) FROM users WHERE role='student'").fetchone()[0];placed=c.execute("SELECT count(DISTINCT student_id) FROM applications WHERE status='Selected'").fetchone()[0]
 branches=c.execute("SELECT u.branch,count(DISTINCT u.id) students,count(DISTINCT CASE WHEN a.status='Selected' THEN u.id END) placed FROM users u LEFT JOIN applications a ON a.student_id=u.id WHERE u.role='student' GROUP BY u.branch").fetchall()
 return render_template("admin/reports.html",total=total,placed=placed,branches=branches,placement_rate=round(100*placed/total,1) if total else 0)
