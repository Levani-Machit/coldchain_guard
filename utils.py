def build_update_clause(update_data: dict) -> tuple[str, list]:

    set_parts = []
    values = []

    for key, value in update_data.items():
        set_parts.append(f"{key} = %s")
        values.append(value)

    set_clause = ", ".join(set_parts)
    
    return set_clause, values
