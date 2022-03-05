
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import stations_controller


app = FastAPI()
app.add_middleware(
	CORSMiddleware, 
	allow_origins=["*"],
	allow_methods=["*"]
)
app.include_router(stations_controller.router)


if __name__ == '__main__':
	uvicorn.run(app, host="0.0.0.0", port=8032)
