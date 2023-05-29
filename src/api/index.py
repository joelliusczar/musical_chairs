#pyright: reportUnusedFunction=false, reportMissingTypeStubs=false
import uvicorn #pyright: ignore [reportMissingTypeStubs]
import musical_chairs_libs.dtos_and_utilities.logging as logging
import sys
from typing import Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from controllers import (
	stations_controller,
	accounts_controller,
	song_info_controller
)
from musical_chairs_libs.dtos_and_utilities import (
	build_error_obj,
	AlreadyUsedError
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from email_validator import EmailNotValidError #pyright: ignore reportUnknownVariableType

cors_allowed_origins=["https://127.0.0.1", "https://localhost:3000"]

app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=cors_allowed_origins,
	allow_methods=["*"],
	allow_headers=["Authorization", "Cookie"],
	expose_headers=["X-AuthExpired"],
	allow_credentials=True
)
app.include_router(stations_controller.router)
app.include_router(accounts_controller.router)
app.include_router(song_info_controller.router)

def get_cors_origin_or_default(origin: str) -> str:
	allowedOriginSet = set(cors_allowed_origins)
	if origin in allowedOriginSet:
		return origin
	return cors_allowed_origins[0] if len(cors_allowed_origins) else ""

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
	return JSONResponse(
		{ "detail": ex.args[0] },
		status_code=422,
		headers={
			"Access-Control-Allow-Origin": get_cors_origin_or_default(
				request.headers.get("origin", None)
			),
			"access-control-allow-credentials": "true"
		}
	)

@app.exception_handler(EmailNotValidError) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def handle_invalid_email(
	request: Request,
	ex: EmailNotValidError
) -> JSONResponse:
	return JSONResponse(
		{ "detail": ex.args[0] },
		status_code=422,
		headers={
			"Access-Control-Allow-Origin": get_cors_origin_or_default(
				request.headers.get("origin", None)
			),
			"access-control-allow-credentials": "true"
		}
	)


@app.exception_handler(Exception) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def everything_else(
	request: Request,
	ex: Exception
) -> JSONResponse:
	logging.logger.error(ex)
	response = JSONResponse(content=
		{ "detail": [
				build_error_obj("Onk! Caveman error! What do?")
			]
		},
		status_code=500,
		headers={
			"Access-Control-Allow-Origin": get_cors_origin_or_default(
				request.headers.get("origin", None)
			),
			"access-control-allow-credentials": "true"
		}
	)
	return response

if __name__ == "__main__":
	privateKey = sys.argv[1]
	publicKey = sys.argv[2]
	uvicorn.run(
		app, #pyright: ignore [reportGeneralTypeIssues]
		host="0.0.0.0",
		port=8032,
		ssl_keyfile=privateKey,
		ssl_certfile=publicKey
	)