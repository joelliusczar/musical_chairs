#pyright: reportUnusedFunction=false, reportMissingTypeStubs=false
import uvicorn #pyright: ignore [reportMissingTypeStubs]
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from controllers import stations_controller, accounts_controller
from musical_chairs_libs.simple_functions import build_error_obj


app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://127.0.0.1", "http://localhost:3000"],
	allow_methods=["*"]
)
app.include_router(stations_controller.router)
app.include_router(accounts_controller.router)

@app.exception_handler(RequestValidationError) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def change_validation_errors(
	request: Request,
	ex: RequestValidationError
) -> JSONResponse:
	errorList = list(map(
		lambda e: build_error_obj(e["msg"], e["loc"][1]), #pyright: ignore [reportGeneralTypeIssues]
		ex.errors())
	)
	return JSONResponse({ "detail": errorList }, status_code=422)



if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8032) #pyright: ignore [reportGeneralTypeIssues]
