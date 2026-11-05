import secrets
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, session, url_for

from .database import close_db, init_db
from .registry import init_registry


def create_app():
    """Create the Flask app and connect every feature blueprint."""
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    app.config.from_object("placement_app.config.Config")

    # Initialize the shared database connection and close it after each request.
    init_db(app)
    init_registry(app)
    app.teardown_appcontext(close_db)

    # Each feature owns its routes; registering these blueprints wires them
    # into the single Flask application served by app.py.
    from .auth import bp as auth_bp, get_current_user
    from .notifications import bp as notifications_bp
    from .placement import bp as placement_bp
    from .reports import bp as reports_bp
    from .student import bp as student_bp

    for blueprint in (
        auth_bp,
        student_bp,
        placement_bp,
        notifications_bp,
        reports_bp,
    ):
        app.register_blueprint(blueprint)

    @app.before_request
    def protect_post_requests_with_csrf():
        if request.method == "POST":
            token = session.get("csrf")
            submitted_token = request.form.get("_csrf_token", "")
            if not token or not secrets.compare_digest(token, submitted_token):
                abort(400)

    @app.context_processor
    def inject_common_template_values():
        if "csrf" not in session:
            session["csrf"] = secrets.token_urlsafe(32)
        return {
            "current_user": get_current_user(),
            "csrf_token": session["csrf"],
        }

    @app.get("/")
    def home():
        user = get_current_user()
        if user is None:
            return redirect(url_for("auth.login"))
        if user["role"] == "admin":
            return redirect(url_for("placement.dashboard"))
        return redirect(url_for("student.dashboard"))

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template(
            "shared/error.html",
            code=403,
            message="You do not have access to this page.",
        ), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template(
            "shared/error.html",
            code=404,
            message="Page not found.",
        ), 404

    return app
