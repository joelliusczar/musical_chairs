#pyright: reportUnusedFunction=false, reportMissingTypeStubs=false
import uvicorn #pyright: ignore [reportMissingTypeStubs]
import logging
from typing import Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from controllers import stations_controller, accounts_controller
from musical_chairs_libs.simple_functions import build_error_obj
from musical_chairs_libs.errors import AlreadyUsedError
from starlette.exceptions import HTTPException as StarletteHTTPException
from email_validator import EmailNotValidError #pyright: ignore reportUnknownVariableType


app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://127.0.0.1", "http://localhost:3000"],
	allow_methods=["*"],
	allow_headers=["Authorization"]
)
app.include_router(stations_controller.router)
app.include_router(accounts_controller.router)


def transForm_error(err: Any) -> dict[str, Any]:
	msg = err["msg"]
	field = err["loc"][1] if len(err["loc"]) > 1 else None
	return build_error_obj(msg, field)

@app.exception_handler(RequestValidationError) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def change_validation_errors(
	request: Request,
	ex: RequestValidationError
) -> JSONResponse:
	errorList = [transForm_error(e) for e in ex.errors()]
	return JSONResponse({ "detail": errorList }, status_code=422)

@app.exception_handler(StarletteHTTPException) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
async def change_errors(
	request: Request,
	ex: StarletteHTTPException
) -> JSONResponse:
	if type(ex.detail) is str:
		ex.detail = [build_error_obj(ex.detail)] #pyright: ignore [reportGeneralTypeIssues]
	return await http_exception_handler(request, ex)

@app.exception_handler(AlreadyUsedError) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def handle_already_used_values(
	request: Request,
	ex: AlreadyUsedError
) -> JSONResponse:
	return JSONResponse({ "detail": ex.args[0] }, status_code=422)

@app.exception_handler(EmailNotValidError) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def handle_invalid_email(
	request: Request,
	ex: EmailNotValidError
) -> JSONResponse:
	return JSONResponse({ "detail": ex.args[0] }, status_code=422)


@app.exception_handler(Exception) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def everything_else(
	request: Request,
	ex: Exception
) -> JSONResponse:
	logging.basicConfig(
			format="%(asctime)s %(message)s",
			filename="radio.log",
			encoding="utf-8",
			level=logging.INFO
		)
	logging.error(ex)
	return JSONResponse(
		{ "detail": [
				build_error_obj("There was an error processing that request")
			]
		},
		status_code=500
	)

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8032) #pyright: ignore [reportGeneralTypeIssues]
