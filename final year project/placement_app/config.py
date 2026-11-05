import os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
class Config:
 SECRET_KEY=os.environ.get("PLACEMENT_SECRET_KEY","replace-this-development-secret")
 DATABASE=os.environ.get("PLACEMENT_DATABASE",str(ROOT/"placement.db"))
 STUDENT_REGISTRY_DATABASE=os.environ.get("PLACEMENT_REGISTRY_DATABASE",str(ROOT/"student_registry.db"))
 SMTP_HOST=os.environ.get("PLACEMENT_SMTP_HOST","")
 SMTP_PORT=int(os.environ.get("PLACEMENT_SMTP_PORT","587"))
 SMTP_USERNAME=os.environ.get("PLACEMENT_SMTP_USERNAME","")
 SMTP_PASSWORD=os.environ.get("PLACEMENT_SMTP_PASSWORD","")
 SMTP_FROM=os.environ.get("PLACEMENT_SMTP_FROM","")
