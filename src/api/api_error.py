from fastapi import HTTPException, status
from musical_chairs_libs.dtos_and_utilities import (
	build_error_obj,
	seconds_to_tuple,
	build_timespan_msg
)

def build_not_logged_in_error() -> HTTPException:
	return HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail=[build_error_obj("Not authenticated")],
		headers={"WWW-Authenticate": "Bearer"}
	)

def build_not_wrong_credentials_error() -> HTTPException:
	return HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail=[build_error_obj("Could not validate credentials")],
		headers={"WWW-Authenticate": "Bearer"}
	)

def build_expired_credentials_error() -> HTTPException:
	return HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail=[build_error_obj("Credentials are expired")],
		headers={
			"WWW-Authenticate": "Bearer",
			"X-AuthExpired": "true"
		}
	)

def build_wrong_permissions_error() -> HTTPException:
	return HTTPException(
		status_code=status.HTTP_403_FORBIDDEN,
		detail=[build_error_obj(
			"Insufficient permissions to perform that action"
		)],
		headers={"WWW-Authenticate": "Bearer"}
	)

def build_too_many_requests_error(timeleft: int) -> HTTPException:
	return HTTPException(
					status_code=status.HTTP_429_TOO_MANY_REQUESTS,
					detail=[build_error_obj(
						"Please wait "
						f"{build_timespan_msg(seconds_to_tuple(timeleft))} "
						"before trying again")
					]
				)