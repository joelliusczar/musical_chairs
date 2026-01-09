#pyright: reportUnusedFunction=false, reportMissingTypeStubs=false
import uvicorn #pyright: ignore [reportMissingTypeStubs]
import musical_chairs_libs.dtos_and_utilities.logging as logging
import sys
from typing import Any
from traceback import TracebackException
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse, Response
from fastapi.requests import Request
from controllers import (
	stations_controller,
	accounts_controller,
	song_info_controller,
	albums_controller,
	artists_controller,
	playlist_controller,
)
from musical_chairs_libs.dtos_and_utilities import (
	build_error_obj,
	build_timespan_msg,
	AlreadyUsedError,
	NotImplementedError,
	NotFoundError,
	NotLoggedInError,
	seconds_to_tuple,
	TooManyRequestsError,
	WrongPermissionsError,
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from email_validator import EmailNotValidError #pyright: ignore reportUnknownVariableType

cors_allowed_origins=[
	"https://127.0.0.1",
	"https://localhost:3000",
	"https://www.musicalchairs.radio.fm"
]

app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=cors_allowed_origins,
	allow_methods=["*"],
	allow_headers=[
		"Authorization",
		"Cookie",
		"Forwarded",
		"True-Client-Ip",
		"Via",
		"X-Client-IP",
		"X-Forwarded-For",
		"X-Real-IP"
	],
	expose_headers=["x-authexpired"],
	allow_credentials=True
)
app.include_router(accounts_controller.router)
app.include_router(albums_controller.router)
app.include_router(artists_controller.router)
app.include_router(playlist_controller.router)
app.include_router(song_info_controller.router)
app.include_router(stations_controller.router)


def get_cors_origin_or_default(origin: str) -> str:
	allowedOriginSet = set(cors_allowed_origins)
	if origin in allowedOriginSet:
		return origin
	return cors_allowed_origins[0] if len(cors_allowed_origins) else ""


def transForm_error(err: Any) -> dict[str, Any]:
	msg = str(err["msg"]).removeprefix("Value error,").strip()
	field = "->".join(f for f in err["loc"]) if len(err["loc"]) > 1 \
		else err["loc"][0] if len(err["loc"]) > 0 else None
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
) -> Response:
	if type(ex.detail) is str:
		ex.detail = [build_error_obj(ex.detail)] #pyright: ignore [reportAttributeAccessIssue]
	return await http_exception_handler(request, ex)


@app.exception_handler(AlreadyUsedError) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def handle_already_used_values(
	request: Request,
	ex: AlreadyUsedError
) -> JSONResponse:
	return JSONResponse(
		{ "detail": ex.args[0] },
		status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
		headers={
			"Access-Control-Allow-Origin": get_cors_origin_or_default(
				request.headers.get("origin", "")
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
		status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
		headers={
			"Access-Control-Allow-Origin": get_cors_origin_or_default(
				request.headers.get("origin", "")
			),
			"access-control-allow-credentials": "true"
		}
	)


@app.exception_handler(NotFoundError) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def not_found(
	request: Request,
	ex: Exception
) -> JSONResponse:
	response = JSONResponse(content=
		{ "detail": ex.args[0] },
		status_code=status.HTTP_404,
		headers={
			"Access-Control-Allow-Origin": get_cors_origin_or_default(
				request.headers.get("origin", "")
			),
			"access-control-allow-credentials": "true"
		}
	)
	return response


@app.exception_handler(NotLoggedInError) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def not_logged_in(
	request: Request,
	ex: Exception
) -> JSONResponse:
	response = JSONResponse(content=
		{ "detail": [build_error_obj("Not authenticated")] },
		status_code=status.HTTP_401_UNAUTHORIZED,
		headers={
			"Access-Control-Allow-Origin": get_cors_origin_or_default(
				request.headers.get("origin", "")
			),
			"WWW-Authenticate": "Bearer"
		}
	)
	return response


@app.exception_handler(TooManyRequestsError) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def too_many_requests(
	request: Request,
	ex: Exception
) -> JSONResponse:
	response = JSONResponse(content=
		{ "detail": [build_error_obj(
				"Please wait "
				f"{build_timespan_msg(seconds_to_tuple(ex.args[0]))} "
				"before trying again"
			)]
		},
		status_code=status.HTTP_429_TOO_MANY_REQUESTS,
		headers={
			"Access-Control-Allow-Origin": get_cors_origin_or_default(
				request.headers.get("origin", "")
			),
			"WWW-Authenticate": "Bearer"
		}
	)
	return response

@app.exception_handler(WrongPermissionsError) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def wrong_permissions(
	request: Request,
	ex: Exception
) -> JSONResponse:
	response = JSONResponse(content=
		{ "detail": [build_error_obj(
				"Insufficient permissions to perform that action"
			)]
		},
		status_code=status.HTTP_403_FORBIDDEN,
		headers={
			"Access-Control-Allow-Origin": get_cors_origin_or_default(
				request.headers.get("origin", "")
			)
		}
	)
	return response


@app.exception_handler(NotImplementedError) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def not_implemented(
	request: Request,
	ex: Exception
) -> JSONResponse:
	response = JSONResponse(content=
		{ "detail": [
				build_error_obj("This functionality has not been implemented")
			]
		},
		status_code=500,
		headers={
			"Access-Control-Allow-Origin": get_cors_origin_or_default(
				request.headers.get("origin", "")
			),
			"access-control-allow-credentials": "true"
		}
	)
	return response


@app.exception_handler(Exception) #pyright: ignore [reportUntypedFunctionDecorator, reportUnknownMemberType]
def everything_else(
	request: Request,
	ex: Exception
) -> JSONResponse:
	logging.logger.error(
		"".join(TracebackException.from_exception(ex).format())
	)
	response = JSONResponse(content=
		{ "detail": [
				build_error_obj("Onk! Caveman error! What do?")
			]
		},
		status_code=500,
		headers={
			"Access-Control-Allow-Origin": get_cors_origin_or_default(
				request.headers.get("origin", "")
			),
			"access-control-allow-credentials": "true"
		}
	)
	return response

@app.get("/canary")
def canary() -> str:
	return "Third Canary"

if __name__ == "__main__":
	if len(sys.argv) > 2:
		privateKey = sys.argv[1]
		publicKey = sys.argv[2]
		uvicorn.run(
			app, #pyright: ignore [reportArgumentType]
			host="0.0.0.0",
			port=8032,
			ssl_keyfile=privateKey,
			ssl_certfile=publicKey
		)
	else:
		uvicorn.run(
			app, #pyright: ignore [reportArgumentType]
			host="0.0.0.0",
			port=8032
		)