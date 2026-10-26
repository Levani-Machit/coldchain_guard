from fastapi import APIRouter, HTTPException, status
from coldchain_guard.models import TemperatureReadingCreate, TemperatureReadingResponse
from coldchain_guard.database import get_connection
from coldchain_guard.services.violations import detect_and_save_violations
from psycopg.errors import ForeignKeyViolation

router = APIRouter(
    prefix="/readings",
    tags=["Temperature Readings"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=TemperatureReadingResponse
)
def create_reading(new_reading: TemperatureReadingCreate):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        s.storage_location_id,
                        s.is_active AS sensor_active,
                        sl.is_active AS location_active
                    FROM sensors AS s
                    INNER JOIN storage_locations AS sl
                        ON s.storage_location_id = sl.id
                    WHERE s.id = %s;
                    """,
                    (new_reading.sensor_id,)
                )
                sensor_row = cursor.fetchone()
                if sensor_row is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Sensor not found"
                    )
                if not sensor_row["sensor_active"]:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Cannot record readings from an inactive sensor"
                    )
                if not sensor_row["location_active"]:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Cannot record readings in an inactive storage location"
                    )
                storage_location_id = sensor_row["storage_location_id"]
                cursor.execute(
                    """
                    INSERT INTO temperature_readings 
                    (sensor_id, temperature)
                    VALUES 
                    (%s, %s)
                    RETURNING *;
                    """,
                    (new_reading.sensor_id, new_reading.temperature)
                )
                temperature_row = cursor.fetchone()
                temperature = temperature_row["temperature"]
                detect_and_save_violations(
                    cursor,
                    storage_location_id,
                    temperature_row["id"],
                    temperature
                )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sensor doesn't exist"
        )
    return temperature_row

@router.get(
    "",
    response_model=list[TemperatureReadingResponse]
)
def get_readings(
    sensor_id: int | None = None
):
    query = "SELECT * FROM temperature_readings"
    value = []
    if sensor_id is not None:
        query += " WHERE sensor_id = %s"
        value.append(sensor_id)
    query += " ORDER BY recorded_at DESC, id DESC;"
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, value)
            all_rows = cursor.fetchall()
    return all_rows

@router.get(
    "/{reading_id}",
    response_model=TemperatureReadingResponse
)
def get_reading(reading_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM temperature_readings
                WHERE id = %s;
                """,
                (reading_id,)
            )
            wanted_row = cursor.fetchone()
        if wanted_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reading not found"
            )
    return wanted_row
