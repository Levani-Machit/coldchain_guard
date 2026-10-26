from decimal import Decimal

def detect_and_save_violations(
        cursor,
        storage_location_id: int,
        reading_id: int,
        temperature: Decimal
) -> None:
    cursor.execute(
        """
        SELECT id, min_temperature, max_temperature
        FROM batches
        WHERE storage_location_id = %s;
        """,
        (storage_location_id,)
    )
    batches = cursor.fetchall()
    for batch in batches:
        violation_type = None
        if temperature < batch["min_temperature"]:
            violation_type = "too_low"
        elif temperature > batch["max_temperature"]:
            violation_type = "too_high"
        if violation_type is not None:
            cursor.execute(
                """
                INSERT INTO violations
                (batch_id, temperature_reading_id, violation_type)
                VALUES
                (%s, %s, %s);
                """,
                (batch["id"], reading_id, violation_type)
            )
