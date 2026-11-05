from flask import Blueprint,abort,flash,redirect,render_template,request,url_for
from .security import login_required
from .database import get_db
from .services import create_notification
bp=Blueprint("placement",__name__,url_prefix="/admin")
STAGES=("Applied","Shortlisted","Test/Interview","Selected","Rejected")
@bp.get("/")
@login_required("admin")
def dashboard():
 c=get_db();metrics={"students":c.execute("SELECT count(*) FROM users WHERE role='student'").fetchone()[0],"placed":c.execute("SELECT count(DISTINCT student_id) FROM applications WHERE status='Selected'").fetchone()[0],"companies":c.execute("SELECT count(*) FROM companies").fetchone()[0],"drives":c.execute("SELECT count(*) FROM drives").fetchone()[0]}
 applications=c.execute("SELECT a.*,u.name student,u.enrollment,d.title,c.name company FROM applications a JOIN users u ON u.id=a.student_id JOIN drives d ON d.id=a.drive_id JOIN companies c ON c.id=d.company_id ORDER BY a.applied DESC LIMIT 8").fetchall()
 return render_template("admin/dashboard.html",metrics=metrics,applications=applications)
@bp.route("/drives",methods=["GET","POST"])
@login_required("admin")
def drives():
 c=get_db()
 if request.method=="POST":
  try:
   company=request.form["company"].strip();title=request.form["title"].strip();cg=float(request.form.get("min_cgpa",0));bk=int(request.form.get("max_backlogs",0));deadline=request.form["deadline"];day=request.form["drive_date"]
   if not company or not title:raise ValueError
  except (ValueError,KeyError):flash("Complete required fields with valid values.","error");return redirect(url_for("placement.drives"))
  c.execute("INSERT OR IGNORE INTO companies(name) VALUES(?)",(company,));cid=c.execute("SELECT id FROM companies WHERE name=?",(company,)).fetchone()["id"];branches=";".join(x.strip() for x in request.form.get("branches","").split(",") if x.strip())
  c.execute("INSERT INTO drives(company_id,title,description,ctc,branches,mincgpa,maxbacklogs,deadline,drive_date,venue,status) VALUES(?,?,?,?,?,?,?,?,?,?,?)",(cid,title,request.form.get("description",""),request.form.get("ctc",""),branches,cg,bk,deadline,day,request.form.get("venue",""),request.form.get("status","Open")));c.commit();flash("Drive created.","success");return redirect(url_for("placement.drives"))
 rows=c.execute("SELECT d.*,c.name company,(SELECT count(*) FROM applications a WHERE a.drive_id=d.id) applicants FROM drives d JOIN companies c ON c.id=d.company_id ORDER BY d.drive_date").fetchall()
 return render_template("admin/drives.html",drives=rows,edit_drive=None)

@bp.route("/drives/<int:drive_id>/edit",methods=["GET","POST"])
@login_required("admin")
def edit_drive(drive_id):
 c=get_db()
 drive=c.execute("SELECT d.*,c.name company FROM drives d JOIN companies c ON c.id=d.company_id WHERE d.id=?",(drive_id,)).fetchone()
 if not drive:abort(404)
 if request.method=="POST":
  try:
   company=request.form["company"].strip();title=request.form["title"].strip();cg=float(request.form.get("min_cgpa",0));bk=int(request.form.get("max_backlogs",0));deadline=request.form["deadline"];day=request.form["drive_date"];status=request.form["status"]
   if not company or not title or not 0<=cg<=10 or bk<0 or status not in ("Open","Closed","Draft"):raise ValueError
  except (ValueError,KeyError):
   flash("Complete required fields with valid values.","error")
   return redirect(url_for("placement.edit_drive",drive_id=drive_id))
  c.execute("INSERT OR IGNORE INTO companies(name) VALUES(?)",(company,))
  company_id=c.execute("SELECT id FROM companies WHERE name=?",(company,)).fetchone()["id"]
  branches=";".join(x.strip() for x in request.form.get("branches","").split(",") if x.strip())
  c.execute("""UPDATE drives SET company_id=?,title=?,description=?,ctc=?,branches=?,mincgpa=?,maxbacklogs=?,deadline=?,drive_date=?,venue=?,status=? WHERE id=?""",
   (company_id,title,request.form.get("description",""),request.form.get("ctc",""),branches,cg,bk,deadline,day,request.form.get("venue",""),status,drive_id))
  c.commit()
  flash("Placement drive updated.","success")
  return redirect(url_for("placement.drives"))
 rows=c.execute("SELECT d.*,(SELECT count(*) FROM applications a WHERE a.drive_id=d.id) applicants,c.name company FROM drives d JOIN companies c ON c.id=d.company_id ORDER BY d.drive_date").fetchall()
 return render_template("admin/drives.html",drives=rows,edit_drive=drive)
@bp.post("/drives/<int:drive_id>/delete")
@login_required("admin")
def delete_drive(drive_id):
 c=get_db()
 drive=c.execute("SELECT id,title FROM drives WHERE id=?",(drive_id,)).fetchone()
 if not drive:abort(404)
 applications=c.execute("SELECT count(*) FROM applications WHERE drive_id=?",(drive_id,)).fetchone()[0]
 if applications:
  flash("This drive has applications and cannot be deleted. Close it instead to preserve application history.","error")
  return redirect(url_for("placement.drives"))
 c.execute("DELETE FROM drives WHERE id=?",(drive_id,))
 c.commit()
 flash("Placement drive deleted.","success")
 return redirect(url_for("placement.drives"))

@bp.route("/applications",methods=["GET","POST"])
@login_required("admin")
def applications():
 c=get_db()
 if request.method=="POST":
  aid=request.form.get("application_id",type=int);status=request.form.get("status")
  if status not in STAGES:abort(400)
  row=c.execute("SELECT a.student_id,d.title FROM applications a JOIN drives d ON d.id=a.drive_id WHERE a.id=?",(aid,)).fetchone()
  if not row:abort(404)
  c.execute("UPDATE applications SET status=? WHERE id=?",(status,aid));create_notification(row["student_id"],"Application update for "+row["title"]+": "+status);flash("Status updated and student notified.","success");return redirect(url_for("placement.applications"))
 rows=c.execute("SELECT a.*,u.name student,u.email,u.enrollment,d.title,c.name company FROM applications a JOIN users u ON u.id=a.student_id JOIN drives d ON d.id=a.drive_id JOIN companies c ON c.id=d.company_id ORDER BY a.applied DESC").fetchall()
 return render_template("admin/applications.html",applications=rows,statuses=STAGES)

