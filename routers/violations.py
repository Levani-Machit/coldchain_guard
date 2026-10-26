from fastapi import APIRouter, HTTPException, status
from coldchain_guard.database import get_connection
from coldchain_guard.models import ViolationResponse

router = APIRouter(
    prefix="/violations",
    tags=["Violations"]
)

@router.get(
    "",
    response_model=list[ViolationResponse]
)
def get_violations(
    batch_id: int | None = None,
    temperature_reading_id: int | None = None,
    violation_type: str | None = None
):
    conditions = []
    values = []
    query = "SELECT * FROM violations"
    if batch_id is not None:
        conditions.append("batch_id = %s")
        values.append(batch_id)
    if temperature_reading_id is not None:
        conditions.append("temperature_reading_id = %s")
        values.append(temperature_reading_id)
    if violation_type is not None:
        conditions.append("violation_type = %s")
        values.append(violation_type)
    if conditions:
        where_clause = " AND ".join(conditions)
        query += f" WHERE {where_clause}"
    query += " ORDER BY id;"
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            all_rows = cursor.fetchall()
    return all_rows

@router.get(
    "/{violation_id}",
    response_model=ViolationResponse
)
def get_violation(violation_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM violations
                WHERE id = %s;
                """,
                (violation_id,)
            )
            retrieved_row = cursor.fetchone()
        if retrieved_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Violation not found"
            )
    return retrieved_row
