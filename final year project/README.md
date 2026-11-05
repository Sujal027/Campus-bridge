# College Placement Tracker

Flask and SQLite project organized around the placement proposal use cases.

## Run locally
Open PowerShell in this folder:
1. Activate the prepared environment: .\.venv\Scripts\Activate.ps1
2. Install or refresh dependencies: pip install -r requirements.txt
3. Start the app: python app.py
4. Visit http://localhost:5000

## Demo accounts
Student: student@college.edu / demo123
Placement admin: admin@college.edu / demo123

## Project layout
- app.py: app entry point bound to 127.0.0.1:5000
- placement_app/: configuration, database, authentication/security, student, placement, notification, report, and eligibility logic
- templates/auth/: sign-in
- templates/student/: dashboard, profile, opportunities, and application history
- templates/admin/: dashboard, drive management, application management, and reports
- templates/shared/: notification feed and error page
- static/: shared styles

Student and admin flows use the same SQLite database. Application status changes create student notifications. Admin announcements are broadcast to student notification feeds. Resume uploads and real email/SMS delivery are future work. Change the development secret and demo credentials before deployment.

## Student contact and email notifications
Student profiles support an email address, phone number, and an email-notification preference. Notifications remain in SQLite. To send email alerts for new unread notifications, configure these environment variables before starting Flask: PLACEMENT_SMTP_HOST, PLACEMENT_SMTP_PORT (587 for STARTTLS or 465 for SSL), PLACEMENT_SMTP_USERNAME, PLACEMENT_SMTP_PASSWORD, and PLACEMENT_SMTP_FROM. Without SMTP settings, in-app notifications still work and email is skipped. SMTP credentials should be set in the hosting environment and not committed to the repository. Students can delete their own notifications; notifications with application history are otherwise retained unless their owner removes them.

## Student self-registration
The public registration form verifies enrollment number, email, and phone against a separate SQLite roster at student_registry.db (override with PLACEMENT_REGISTRY_DATABASE). The demo roster is seeded with sample records. For example: enrollment 24UCS0001, email 
ewstudent@college.edu, phone +91 98765 43211. Use any name and a password of at least 8 characters. Successful registration creates a student account with a hashed password and uses the branch and graduation year from the roster. Replace the dummy roster with the college's authorized student data before real use. Enrollment numbers follow two year digits, a 2–4 letter branch code, and four digits, such as 23UCS0033.
