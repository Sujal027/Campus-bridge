from datetime import date,datetime,timedelta
import sqlite3
from flask import current_app,g
from werkzeug.security import generate_password_hash
SCHEMA="""
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL,role TEXT NOT NULL,branch TEXT DEFAULT '',year INTEGER DEFAULT 2027,cgpa REAL DEFAULT 0,backlogs INTEGER DEFAULT 0,phone TEXT DEFAULT '',email_notifications INTEGER NOT NULL DEFAULT 1,enrollment TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS companies(id INTEGER PRIMARY KEY,name TEXT UNIQUE NOT NULL);
CREATE TABLE IF NOT EXISTS drives(id INTEGER PRIMARY KEY,company_id INTEGER REFERENCES companies(id),title TEXT NOT NULL,description TEXT DEFAULT '',ctc TEXT DEFAULT '',branches TEXT DEFAULT '',mincgpa REAL DEFAULT 0,maxbacklogs INTEGER DEFAULT 0,deadline TEXT NOT NULL,drive_date TEXT NOT NULL,venue TEXT DEFAULT '',status TEXT DEFAULT 'Open');
CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY,student_id INTEGER REFERENCES users(id),drive_id INTEGER REFERENCES drives(id),status TEXT DEFAULT 'Applied',applied TEXT NOT NULL,UNIQUE(student_id,drive_id));
CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY,student_id INTEGER REFERENCES users(id),message TEXT NOT NULL,created TEXT NOT NULL,read INTEGER DEFAULT 0);
"""
def get_db():
 if "db" not in g:
  g.db=sqlite3.connect(current_app.config["DATABASE"]);g.db.row_factory=sqlite3.Row;g.db.execute("PRAGMA foreign_keys=ON")
 return g.db
def close_db(e=None):
 c=g.pop("db",None)
 if c:c.close()
def init_db(app):
 with app.app_context():
  c=sqlite3.connect(app.config["DATABASE"]);c.executescript(SCHEMA)
  user_columns={row[1] for row in c.execute("PRAGMA table_info(users)")}
  if "phone" not in user_columns:c.execute("ALTER TABLE users ADD COLUMN phone TEXT DEFAULT ''")
  if "email_notifications" not in user_columns:c.execute("ALTER TABLE users ADD COLUMN email_notifications INTEGER NOT NULL DEFAULT 1")
  if "enrollment" not in user_columns:c.execute("ALTER TABLE users ADD COLUMN enrollment TEXT")
  c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_enrollment ON users(enrollment)")
  c.execute("UPDATE users SET enrollment='23UCS0033',phone='+91 98765 43210' WHERE email='student@college.edu' AND enrollment IS NULL")
  if not c.execute("SELECT count(*) FROM users").fetchone()[0]:seed(c)
  c.commit();c.close()
def seed(c):
 pw=generate_password_hash("demo123")
 c.execute("INSERT INTO users(name,email,password,role,branch,year,cgpa,backlogs,phone,enrollment) VALUES(?,?,?,?,?,?,?,?,?,?)",("Aarav Sharma","student@college.edu",pw,"student","Computer Science",2027,8.2,0,"+91 98765 43210","23UCS0033"))
 c.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",("Placement Admin","admin@college.edu",pw,"admin"))
 for x in ("Northstar Systems","BluePeak Analytics","Meridian Labs"):c.execute("INSERT INTO companies(name) VALUES(?)",(x,))
 ids={r[1]:r[0] for r in c.execute("SELECT id,name FROM companies")};today=date.today()
 items=[("Northstar Systems","Graduate Software Engineer","Build and maintain web products.","₹8-12 LPA","Computer Science;Information Technology",7,0,8,15,"Main Auditorium"),("BluePeak Analytics","Data Analyst Associate","Turn data into useful decisions.","₹6-8 LPA","Computer Science;Information Technology;Electronics",7.5,1,12,20,"Online"),("Meridian Labs","Quality Engineering Intern","Support test automation and release quality.","₹35,000/month","Computer Science;Information Technology",6.5,2,18,25,"Innovation Block")]
 for co,title,desc,ctc,br,cg,bk,dl,day,v in items:c.execute("INSERT INTO drives(company_id,title,description,ctc,branches,mincgpa,maxbacklogs,deadline,drive_date,venue) VALUES(?,?,?,?,?,?,?,?,?,?)",(ids[co],title,desc,ctc,br,cg,bk,(today+timedelta(days=dl)).isoformat(),(today+timedelta(days=day)).isoformat(),v))
 sid=c.execute("SELECT id FROM users WHERE role='student'").fetchone()[0];did=c.execute("SELECT id FROM drives LIMIT 1").fetchone()[0];now=datetime.now().isoformat(timespec="minutes")
 c.execute("INSERT INTO applications(student_id,drive_id,status,applied) VALUES(?,?,?,?)",(sid,did,"Shortlisted",now));c.execute("INSERT INTO notifications(student_id,message,created) VALUES(?,?,?)",(sid,"Shortlisted for Graduate Software Engineer.",now))
