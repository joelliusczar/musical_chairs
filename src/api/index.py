
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import stations_controller


app = FastAPI()
app.add_middleware(
	CORSMiddleware, 
	allow_origins=["127.0.0.1"],
	allow_methods=["*"]
)
app.include_router(stations_controller.router)

