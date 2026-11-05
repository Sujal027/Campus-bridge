from datetime import datetime

from .database import get_db
from .email_service import send_notification_email


def is_eligible(student,drive):
 branches=[x.strip().lower() for x in drive["branches"].split(";") if x.strip()]
 return (not branches or student["branch"].lower() in branches) and student["cgpa"]>=drive["mincgpa"] and student["backlogs"]<=drive["maxbacklogs"]


def create_notification(student_id, message):
 connection = get_db()
 timestamp = datetime.now().isoformat(timespec="minutes")
 connection.execute(
  "INSERT INTO notifications(student_id,message,created) VALUES(?,?,?)",
  (student_id, message, timestamp),
 )
 connection.commit()
 send_notification_email(student_id, message)
