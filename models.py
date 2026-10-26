from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime

class StorageLocationCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"  
    )

    name: str = Field(min_length=1)
    description: str | None = None
    is_active: bool = True

class StorageLocationResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool

class StorageLocationUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    name: str = Field(default=None, min_length=1)
    description: str | None = None
    is_active: bool = None

class SensorCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    storage_location_id: int = Field(gt=0, strict=True)
    name: str = Field(min_length=1)
    identifier: str = Field(min_length=1)
    is_active: bool = True

class SensorResponse(BaseModel):
    id: int
    storage_location_id: int
    name: str
    identifier: str
    is_active: bool
    installed_at: datetime

class SensorUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    storage_location_id: int = Field(default=None, gt=0, strict=True)
    name: str = Field(default=None, min_length=1)
    identifier: str = Field(default=None, min_length=1)
    is_active: bool = None

class BatchCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    product_name: str = Field(min_length=1)
    batch_number: str = Field(min_length=1)
    storage_location_id: int = Field(gt=0, strict=True)
    min_temperature: float = Field(allow_inf_nan=False)
    max_temperature: float = Field(allow_inf_nan=False)

    @model_validator(mode="after")
    def validate_data(self):
        if self.min_temperature >= self.max_temperature:
            raise ValueError(
                "Minimum must be less than maximum"
            )
        return self

class BatchResponse(BaseModel):
    id: int
    product_name: str
    batch_number: str
    storage_location_id: int
    min_temperature: float
    max_temperature: float
    stored_at: datetime

class BatchUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    product_name: str = Field(default=None, min_length=1)
    batch_number: str = Field(default=None, min_length=1)
    storage_location_id: int = Field(default=None, gt=0, strict=True)
    min_temperature: float = Field(default=None, allow_inf_nan=False)
    max_temperature: float = Field(default=None, allow_inf_nan=False)

class TemperatureReadingCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    sensor_id: int = Field(gt=0, strict=True)
    temperature: float = Field(allow_inf_nan=False)

class TemperatureReadingResponse(BaseModel):
    id: int
    sensor_id: int
    temperature: float
    recorded_at: datetime

class ViolationResponse(BaseModel):
    id: int
    batch_id: int
    temperature_reading_id: int
    violation_type: str

class ViolationReportResponse(BaseModel):
    violation_id: int
    batch_number: str
    product_name: str
    sensor_name: str
    temperature: float
    violation_type: str
    recorded_at: datetime
