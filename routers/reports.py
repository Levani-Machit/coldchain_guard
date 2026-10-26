from fastapi import APIRouter
from coldchain_guard.database import get_connection
from coldchain_guard.models import ViolationReportResponse

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

@router.get(
    "/violations",
    response_model=list[ViolationReportResponse]
)
def get_violation_report():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
	                v.id AS violation_id,
	                v.violation_type,
	                b.product_name,
	                tr.temperature,
	                s.name AS sensor_name,
	                b.batch_number,
	                tr.recorded_at
                FROM violations AS v
                INNER JOIN batches AS b
	                ON v.batch_id = b.id
                INNER JOIN temperature_readings AS tr
	                ON v.temperature_reading_id = tr.id
                INNER JOIN sensors AS s
	                ON tr.sensor_id = s.id
                ORDER BY tr.recorded_at DESC, violation_id DESC;
                """
            )
            all_rows = cursor.fetchall()
    return all_rows
