from app.db.repository import create_audit_log

result = create_audit_log(
    incident_id=1,
    action="STATUS_UPDATED",
    performed_by="Admin",
    details="Incident status changed to investigating",
)

print("Audit log created successfully!")
print(result)