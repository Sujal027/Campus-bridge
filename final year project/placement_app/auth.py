import re
import sqlite3
from flask import Blueprint,flash,redirect,render_template,request,session,url_for
from werkzeug.security import check_password_hash,generate_password_hash
from .database import get_db
from .registry import verify_student_record
from .security import login_required

bp=Blueprint("auth",__name__)

def get_current_user():
    user_id=session.get("user_id")
    if user_id is None:
        return None
    return get_db().execute("SELECT * FROM users WHERE id=?",(user_id,)).fetchone()

@bp.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email","").strip().lower()
        user=get_db().execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
        if user and check_password_hash(user["password"],request.form.get("password","")):
            session.clear()
            session["user_id"]=user["id"]
            return redirect(url_for("home"))
        flash("Email or password is incorrect.","error")
    return render_template("auth/login.html")

@bp.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form.get("name","").strip()
        enrollment=request.form.get("enrollment","").strip().upper()
        email=request.form.get("email","").strip().lower()
        phone=request.form.get("phone","").strip()
        password=request.form.get("password","")
        confirmation=request.form.get("confirm_password","")
        if not name or not re.fullmatch(r"\d{2}[A-Z]{2,4}\d{4}",enrollment):
            flash("Enter your name and an enrollment number in the format 23UCS0033.","error")
            return redirect(url_for("auth.register"))
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",email) or not re.fullmatch(r"[+\d\s().-]{7,20}",phone):
            flash("Enter a valid college email address and phone number.","error")
            return redirect(url_for("auth.register"))
        if len(password)<8 or password!=confirmation:
            flash("Use a password of at least 8 characters and make sure both password fields match.","error")
            return redirect(url_for("auth.register"))

        student_record=verify_student_record(enrollment,email,phone)
        if not student_record:
            flash("We could not verify those details in the college student registry.","error")
            return redirect(url_for("auth.register"))
        try:
            cursor=get_db().execute(
                "INSERT INTO users(name,email,password,role,branch,year,phone,enrollment) VALUES(?,?,?,'student',?,?,?,?)",
                (name,email,generate_password_hash(password),student_record["branch"],student_record["graduation_year"],phone,enrollment),
            )
            get_db().commit()
        except sqlite3.IntegrityError:
            get_db().rollback()
            flash("An account already exists for this email or enrollment number.","error")
            return redirect(url_for("auth.register"))

        session.clear()
        session["user_id"]=cursor.lastrowid
        flash("Registration complete. Welcome to CampusBridge.","success")
        return redirect(url_for("student.dashboard"))
    return render_template("auth/register.html")

@bp.post("/logout")
@login_required()
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
