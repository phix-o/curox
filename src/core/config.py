from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.logger import configure_for_dev, configure_for_prod

BASE_DIR = Path(__file__).parent.parent
default_company_logo_path = (
    BASE_DIR.parent / "static" / "images" / "default_company_logo.png"
)


class Settings(BaseSettings):
    db_url: str
    debug: bool = Field(False, description="Whether the app is in debug mode")
    web_url: str = Field(
        "http://localhost:5173", description="The url of the main frontend app"
    )
    static_url: str = Field(
        "http://localhost:7000", description="The static url for file system storage"
    )
    static_path: str = Field(
        "/static", description="The path where static files are uploaded"
    )

    secret_key: str = Field(
        "kindlyreplaceme",
        description="The secret key used to sign and verify auth tokens",
    )
    jwt_algorithm: str = Field("HS256", description="Algorithm used to sign JWT tokens")
    jwt_access_expiry: int = Field(15, description="JWT Token expiry in minutes")
    jwt_refresh_expiry: int = Field(60 * 24, description="JWT Token expiry in minutes")

    # email
    mail_username: str = Field("", description="The email username")
    mail_password: str = Field("", description="The email password")
    mail_server: str = Field("localhost", description="The email server ip")
    mail_port: int = Field(1025, description="The email server port")
    mail_use_credentials: bool = Field(
        False, description="Whether to log in to the smtp server"
    )
    mail_start_tls: bool = Field(False)
    mail_use_tls: bool = Field(False, description="Whether to connect over tls")
    mail_from: str = Field("events@company.com", description="The sender's email")
    mail_from_name: str = Field("Company Events", description="The sender's name")

    model_config = SettingsConfigDict(env_file=".env")

    # This is here to remove the warning where instantiating the
    # settings class causes a lint error
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
if settings.debug:
    # from pprint import pprint
    #
    # pprint(settings.model_dump(), indent=4)

    configure_for_dev()
else:
    configure_for_prod()
