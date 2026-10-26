from fastapi import APIRouter, HTTPException, status
from coldchain_guard.models import StorageLocationCreate, StorageLocationResponse, StorageLocationUpdate
from coldchain_guard.database import get_connection
from coldchain_guard.utils import build_update_clause
from psycopg.errors import UniqueViolation, RestrictViolation

router = APIRouter(
    prefix="/storage-locations",
    tags=["Storage Locations"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=StorageLocationResponse
)
def create_storage_location(new_storage: StorageLocationCreate):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO storage_locations (name, description, is_active)
                    VALUES (%s, %s, %s)
                    RETURNING *;
                    """,
                    (new_storage.name, new_storage.description, new_storage.is_active)
                )
                new_row = cursor.fetchone()
    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A storage location with this name already exists"
        )
    
    return new_row

@router.get(
    "",
    response_model=list[StorageLocationResponse]
)
def get_storage_locations():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM storage_locations
                ORDER BY id;
                """
            )
            all_rows = cursor.fetchall()

    return all_rows

@router.get(
    "/{location_id}",
    response_model=StorageLocationResponse    
)
def get_storage_location(location_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM storage_locations
                WHERE id = %s;
                """,
                (location_id,)
            )
            wanted_row = cursor.fetchone()

        if wanted_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Storage location not found"
            )
    
    return wanted_row

@router.patch(
    "/{location_id}",
    response_model=StorageLocationResponse
)
def update_storage_location(
    location_id: int,
    updated_location: StorageLocationUpdate
):
    updated_data = updated_location.model_dump(exclude_unset=True)
    if not updated_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for an update"
        )

    set_clause, values = build_update_clause(updated_data)
    
    values.append(location_id)

    query = f"""
            UPDATE storage_locations
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
                    detail="Storage location not found"
                )
    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A storage location with this name already exists"
        )
    
    return updated_row

@router.delete(
    "/{location_id}",
    response_model=StorageLocationResponse
)
def delete_storage_location(location_id: int):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM storage_locations
                    WHERE id = %s
                    RETURNING *;
                    """,
                    (location_id,)
                )
                deleted_row = cursor.fetchone()
            
            if deleted_row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Storage location not found"
                )
    except RestrictViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a storage location that has associated sensors or batches"
        )
    
    return deleted_row
