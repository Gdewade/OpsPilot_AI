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