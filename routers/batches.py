from fastapi import APIRouter, HTTPException, status
from coldchain_guard.database import get_connection
from coldchain_guard.models import BatchCreate, BatchResponse, BatchUpdate
from coldchain_guard.utils import build_update_clause
from psycopg.errors import UniqueViolation, ForeignKeyViolation, CheckViolation, RestrictViolation

router = APIRouter(
    prefix="/batches",
    tags=["Batches"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=BatchResponse
)
def create_batch(new_batch: BatchCreate):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO batches
                    (product_name, batch_number, storage_location_id, min_temperature, max_temperature)
                    VALUES
                    (%s, %s, %s, %s, %s)
                    RETURNING *;
                    """,
                    (new_batch.product_name, new_batch.batch_number, new_batch.storage_location_id, new_batch.min_temperature, new_batch.max_temperature)
                )
                new_row = cursor.fetchone()
    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Batch number already exists"
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Storage location doesn't exist"
        )
    except CheckViolation:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Minimum temperature is greater than or equal to maximum"
        )
    return new_row

@router.get(
    "",
    response_model=list[BatchResponse]
)
def get_batches():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM batches
                ORDER BY id;
                """
            )
            all_rows = cursor.fetchall()
    return all_rows

@router.get(
    "/{batch_id}",
    response_model=BatchResponse
)
def get_batch(batch_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM batches
                WHERE id = %s;
                """,
                (batch_id,)
            )
            wanted_row = cursor.fetchone()
        if wanted_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch wasn't found"
            )
    return wanted_row

@router.patch(
    "/{batch_id}",
    response_model=BatchResponse
)
def update_batch(
    batch_id: int,
    updated_batch: BatchUpdate
):
    update_data = updated_batch.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for an update"
        )

    set_clause, values = build_update_clause(update_data)

    values.append(batch_id)

    query = f"""
            UPDATE batches
            SET {set_clause}
            WHERE id = %s
            RETURNING *;
            """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                updated_row = cursor.fetchone()
            if updated_row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Batch not found"
                )
    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Batch number already exists"
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Storage location doesn't exist"
        )
    except CheckViolation:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Minimum temperature should be less than maximum"
        )
    
    return updated_row

@router.delete(
    "/{batch_id}",
    response_model=BatchResponse
)
def delete_batch(batch_id: int):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM batches
                    WHERE id = %s
                    RETURNING *;
                    """,
                    (batch_id,)
                )
                deleted_row = cursor.fetchone()
            if deleted_row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Batch not found"
                )
    except RestrictViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a batch that has associated violation records"
        )
    
    return deleted_row
