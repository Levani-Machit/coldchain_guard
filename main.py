from fastapi import FastAPI
from coldchain_guard.routers.storage_locations import router as storage_locations_router
from coldchain_guard.routers.sensors import router as sensors_router
from coldchain_guard.routers.batches import router as batches_router
from coldchain_guard.routers.readings import router as temperature_readings_router
from coldchain_guard.routers.violations import router as violations_router
from coldchain_guard.routers.reports import router as reports_router

app = FastAPI()

app.include_router(storage_locations_router)
app.include_router(sensors_router)
app.include_router(batches_router)
app.include_router(temperature_readings_router)
app.include_router(violations_router)
app.include_router(reports_router)
