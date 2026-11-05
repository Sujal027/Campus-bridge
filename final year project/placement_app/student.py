from datetime import date,datetime
import re
import sqlite3
from flask import Blueprint,abort,flash,redirect,render_template,request,url_for
from .auth import get_current_user
from .security import login_required
from .database import get_db
from .services import create_notification,is_eligible
bp=Blueprint("student",__name__)
@bp.get("/student")
@login_required("student")
def dashboard():
 u=get_current_user();c=get_db()
 drives=[d for d in c.execute("SELECT d.*,c.name company FROM drives d JOIN companies c ON c.id=d.company_id WHERE d.status='Open' ORDER BY d.drive_date").fetchall() if is_eligible(u,d)]
 apps=c.execute("SELECT a.*,d.title,d.drive_date,c.name company FROM applications a JOIN drives d ON d.id=a.drive_id JOIN companies c ON c.id=d.company_id WHERE a.student_id=? ORDER BY a.applied DESC",(u["id"],)).fetchall()
 notes=c.execute("SELECT * FROM notifications WHERE student_id=? ORDER BY created DESC LIMIT 4",(u["id"],)).fetchall()
 return render_template("student/dashboard.html",student=u,drives=drives[:4],applications=apps[:5],notifications=notes)
@bp.get("/opportunities")
@login_required("student")
def opportunities():
 u=get_current_user();c=get_db();drives=c.execute("SELECT d.*,c.name company FROM drives d JOIN companies c ON c.id=d.company_id WHERE d.status='Open' ORDER BY d.drive_date").fetchall()
 applied={x[0] for x in c.execute("SELECT drive_id FROM applications WHERE student_id=?",(u["id"],))}
 return render_template("student/opportunities.html",student=u,drives=drives,applied_ids=applied,is_eligible=is_eligible)
@bp.post("/opportunities/<int:drive_id>/apply")
@login_required("student")
def apply(drive_id):
 u=get_current_user();c=get_db();d=c.execute("SELECT * FROM drives WHERE id=?",(drive_id,)).fetchone()
 if not d:abort(404)
 if d["status"]!="Open" or d["deadline"]<date.today().isoformat():flash("Applications are closed.","error")
 elif not is_eligible(u,d):flash("Your profile does not meet eligibility criteria.","error")
 else:
  now=datetime.now().isoformat(timespec="minutes")
  try:
   c.execute("INSERT INTO applications(student_id,drive_id,status,applied) VALUES(?,?,?,?)",(u["id"],drive_id,"Applied",now));create_notification(u["id"],"Application submitted for "+d["title"]);flash("Application submitted.","success")
  except sqlite3.IntegrityError:flash("You already applied.","error")
 return redirect(url_for("student.opportunities"))
@bp.route("/profile",methods=["GET","POST"])
@login_required("student")
def profile():
 u=get_current_user()
 if request.method=="POST":
  try:
   cg=float(request.form["cgpa"]);bk=int(request.form["backlogs"]);yr=int(request.form["graduation_year"])
   name=request.form["name"].strip();email=request.form["email"].strip().lower();branch=request.form["branch"].strip();phone=request.form.get("phone","").strip()
   valid_phone=not phone or bool(re.fullmatch(r"[+\d\s().-]{7,20}",phone))
   if not name or not branch or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",email) or not valid_phone or not 0<=cg<=10 or bk<0 or not 2020<=yr<=2040:raise ValueError
  except (ValueError,KeyError):flash("Enter valid profile and contact details.","error");return redirect(url_for("student.profile"))
  try:
   get_db().execute("UPDATE users SET name=?,email=?,phone=?,email_notifications=?,branch=?,cgpa=?,backlogs=?,year=? WHERE id=?",(name,email,phone,int("email_notifications" in request.form),branch,cg,bk,yr,u["id"]));get_db().commit()
  except sqlite3.IntegrityError:
   get_db().rollback();flash("That email address is already in use.","error");return redirect(url_for("student.profile"))
  flash("Profile updated.","success");return redirect(url_for("student.profile"))
 return render_template("student/profile.html",student=u)
@bp.get("/applications")
@login_required("student")
def applications():
 u=get_current_user();rows=get_db().execute("SELECT a.*,d.title,d.drive_date,c.name company FROM applications a JOIN drives d ON d.id=a.drive_id JOIN companies c ON c.id=d.company_id WHERE a.student_id=? ORDER BY a.applied DESC",(u["id"],)).fetchall()
 return render_template("student/applications.html",applications=rows)

