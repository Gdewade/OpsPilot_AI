from app.db.connection import get_connection


def create_incident(incident_data: dict):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO incidents
                    (title, description, severity, log_text)
                VALUES (%s, %s, %s, %s)
                RETURNING id, title, description, severity,
                          log_text, status, created_at
                """,
                (
                    incident_data["title"],
                    incident_data["description"],
                    incident_data["severity"],
                    incident_data["log_text"],
                ),
            )

            row = cur.fetchone()
            conn.commit()

            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "severity": row[3],
                "log_text": row[4],
                "status": row[5],
                "created_at": row[6].isoformat(),
            }
    finally:
        conn.close()


def get_all_incidents():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, description, severity,
                       log_text, status, created_at
                FROM incidents
                ORDER BY id DESC
                """
            )

            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "severity": row[3],
                    "log_text": row[4],
                    "status": row[5],
                    "created_at": row[6].isoformat(),
                }
                for row in rows
            ]
    finally:
        conn.close()



def get_incident_by_id(incident_id: int):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, description, severity,
                       log_text, status, created_at
                FROM incidents
                WHERE id = %s
                """,
                (incident_id,),
            )

            row = cur.fetchone()

            if row is None:
                return None

            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "severity": row[3],
                "log_text": row[4],
                "status": row[5],
                "created_at": row[6].isoformat(),
            }
    finally:
        conn.close()


def update_incident_status(incident_id: int, status: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE incidents
                SET status = %s
                WHERE id = %s
                RETURNING id, title, status
                """,
                (status, incident_id),
            )
            row = cur.fetchone()
            conn.commit()

            if row is None:
                return None

            return {
                "id": row[0],
                "title": row[1],
                "status": row[2],
            }
    finally:
        conn.close()


def create_audit_log(
    incident_id: int,
    action: str,
    performed_by: str,
    details: str = None,
):
    query = """
        INSERT INTO audit_logs
        (incident_id, action, performed_by, details)
        VALUES (%s, %s, %s, %s)
        RETURNING id, incident_id, action, performed_by, details, created_at;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (incident_id, action, performed_by, details),
            )
            result = cur.fetchone()

            return {
                "id": result[0],
                "incident_id": result[1],
                "action": result[2],
                "performed_by": result[3],
                "details": result[4],
                "created_at": result[5],
            }



def get_audit_logs(incident_id: int):
    query = """
        SELECT id, incident_id, action, performed_by, details, created_at
        FROM audit_logs
        WHERE incident_id = %s
        ORDER BY created_at DESC;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (incident_id,))
            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "incident_id": row[1],
                    "action": row[2],
                    "performed_by": row[3],
                    "details": row[4],
                    "created_at": row[5],
                }
                for row in rows
            ]


def create_approval_request(approval_data: dict):
    query = """
        INSERT INTO approval_requests
        (incident_id, action, requested_by)
        VALUES (%s, %s, %s)
        RETURNING *;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    approval_data["incident_id"],
                    approval_data["action"],
                    approval_data["requested_by"],
                ),
            )
            result = cur.fetchone()

            columns = [desc.name for desc in cur.description]
            return dict(zip(columns, result))


def get_approval_request(approval_id: int):
    query = """
        SELECT *
        FROM approval_requests
        WHERE id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (approval_id,))
            result = cur.fetchone()

            if result is None:
                return None

            columns = [desc.name for desc in cur.description]
            return dict(zip(columns, result))


def update_approval_decision(
    approval_id: int,
    decision: str,
    reviewed_by: str,
    comments: str | None = None,
):
    query = """
        UPDATE approval_requests
        SET
            decision = %s,
            reviewed_by = %s,
            comments = %s,
            reviewed_at = CURRENT_TIMESTAMP
        WHERE id = %s
          AND decision = 'pending'
        RETURNING *;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (decision, reviewed_by, comments, approval_id),
            )

            result = cur.fetchone()

            if result is None:
                return None

            columns = [desc.name for desc in cur.description]
            return dict(zip(columns, result))

