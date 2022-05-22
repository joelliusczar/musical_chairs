#pyright: reportUnusedFunction=false, reportMissingTypeStubs=false
import uvicorn #pyright: ignore [reportMissingTypeStubs]
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from controllers import stations_controller
from fastapi.security import OAuth2PasswordRequestForm
from api_dependencies import accounts_service
from musical_chairs_libs.accounts_service import AccountsService


app = FastAPI()
app.add_middleware(
	CORSMiddleware, 
	allow_origins=["127.0.0.1"],
	allow_methods=["*"]
)
app.include_router(stations_controller.router)


@app.post("/token")
def login(
	formData: OAuth2PasswordRequestForm=Depends(), 
	accountService: AccountsService=Depends(accounts_service)):
	user = accountService.authenticate_user(
		formData.username, 
		formData.password.encode()
	)
	if not user or not user.isAuthenticated:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"}
		)
	token = accountService.create_access_token(user.userName)
	return { "access_token": token, "token_type": "bearer" }

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8032) #pyright: ignore [reportGeneralTypeIssues]
