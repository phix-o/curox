from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware

from src.core.auth.backend import BearerTokenAuthBackend
from src.core.exceptions import handle_http_exception, handle_validation_error
from src.features.auth.v1 import router as auth_router
from src.features.companies.v1 import router as companies_router
from src.features.events.v1 import router as events_router
from fastapi.staticfiles import StaticFiles

# Run some setup
from . import setup

v1_router = APIRouter(prefix='/api/v1')
v1_router.include_router(auth_router.router)
v1_router.include_router(companies_router.router)
v1_router.include_router(events_router.router)

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

app.add_middleware(
    CORSMiddleware,
    # FIXME: Change for production
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.add_middleware(AuthenticationMiddleware, backend=BearerTokenAuthBackend())

app.add_exception_handler(HTTPException, handle_http_exception)
app.add_exception_handler(RequestValidationError, handle_validation_error)

app.include_router(v1_router)

@app.get("/")
def root():
    return {'msg': 'Welcome to the api'}
