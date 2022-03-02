
import uvicorn
from fastapi import FastAPI
from controllers import stations_controller
from typing import Any, Dict

app = FastAPI()
app.include_router(stations_controller.router)


if __name__ == '__main__':
	uvicorn.run(app, host="0.0.0.0", port=8032)
