from fastapi import APIRouter, HTTPException, status
from coldchain_guard.models import SensorCreate, SensorResponse, SensorUpdate
from coldchain_guard.database import get_connection
from coldchain_guard.utils import build_update_clause
from psycopg.errors import UniqueViolation, ForeignKeyViolation, RestrictViolation

router = APIRouter(
    prefix="/sensors",
    tags=["Sensors"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SensorResponse
)
def create_sensor(new_sensor: SensorCreate):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO sensors
                    (storage_location_id, name, identifier, is_active)
                    VALUES
                    (%s, %s, %s, %s)
                    RETURNING *;
                    """,
                    (new_sensor.storage_location_id, new_sensor.name, new_sensor.identifier, new_sensor.is_active)
                )
                new_row = cursor.fetchone()
    except(UniqueViolation):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sensor identifier already exists"
        )
    except(ForeignKeyViolation):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Storage location doesn't exist"
        )
    return new_row

@router.get(
    "",
    response_model=list[SensorResponse]
)
def get_sensors():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM sensors
                ORDER BY id;
                """
            )
            all_rows = cursor.fetchall()
    return all_rows

@router.get(
    "/{sensor_id}",
    response_model=SensorResponse
)
def get_sensor(sensor_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM sensors
                WHERE id = %s;
                """,
                (sensor_id,)
            )
            wanted_row = cursor.fetchone()
        if wanted_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sensor not found"
            )
    return wanted_row

@router.patch(
    "/{sensor_id}",
    response_model=SensorResponse
)
def update_sensor(
    sensor_id: int,
    updated_sensor: SensorUpdate
):
    update_data = updated_sensor.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )
    
    set_clause, values = build_update_clause(update_data)
    
    values.append(sensor_id)

    query = f"""
            UPDATE sensors
            SET {set_clause}
            WHERE id = %s
            RETURNING *;
            """
    
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                if "storage_location_id" in update_data:
                    cursor.execute(
                        """
                        SELECT storage_location_id
                        FROM sensors
                        WHERE id = %s;
                        """,
                        (sensor_id,)
                    )
                    current_sensor = cursor.fetchone()
                    if current_sensor is None:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="Sensor not found"
                        )
                    if update_data["storage_location_id"] != current_sensor["storage_location_id"]:
                        cursor.execute(
                            """
                            SELECT EXISTS (
                                SELECT 1
                                FROM temperature_readings
                                WHERE sensor_id = %s
                            ) AS has_readings;
                            """,
                            (sensor_id,)
                        )
                        result = cursor.fetchone()
                        has_readings = result["has_readings"]
                        if has_readings:
                            raise HTTPException(
                                status_code=status.HTTP_409_CONFLICT,
                                detail="Cannot relocate a sensor with existing temperature readings"
                            )
                cursor.execute(query, values)
                updated_row = cursor.fetchone()
            if updated_row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sensor ID doesn't exist"
                )
    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Identifier already belongs to another sensor"
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="New storage location doesn't exist"
        )
    
    return updated_row

@router.delete(
    "/{sensor_id}",
    response_model=SensorResponse
)
def delete_sensor(sensor_id: int):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM sensors
                    WHERE id = %s
                    RETURNING *;
                    """,
                    (sensor_id,)
                )
                deleted_row = cursor.fetchone()
            if deleted_row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sensor not found"
                )
    except RestrictViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a sensor that has associated temperature readings"
        )
    
    return deleted_row
