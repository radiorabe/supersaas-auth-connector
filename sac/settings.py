"""Settings for the SuperSaaS Auth Connector application."""

from starlette.config import Config
from starlette.datastructures import Secret

config = Config()

DEBUG = config("DEBUG", cast=bool, default=False)

SSO_SERVER_URL = config("SSO_SERVER_URL", default="https://sso.rabe.ch/auth/")
SSO_REALM = config("SSO_REALM", default="rabe")
SSO_CLIENT_ID = config("SSO_CLIENT_ID", default="supersaas-auth-connector")

ERROR_REDIRECT_URL = config("ERROR_REDIRECT_URL", default="https://www.rabe.ch")
LOGOUT_REDIRECT_URL = config(
    "LOGOUT_REDIRECT_URL",
    default="https://sso.rabe.ch/auth/realms/rabe/protocol/openid-connect/logout?redirect_uri=https%3A%2F%2Fwww.rabe.ch",
)

SUPERSAAS_ACCOUNT_NAME = config("SUPERSAAS_ACCOUNT_NAME", default="RaBe")
SUPERSAAS_API_TOKEN = config("SUPERSAAS_API_TOKEN", cast=Secret, default="")

PORT: int = config("PORT", default=8000)
HOST: str = config("HOST", default="127.0.0.1")
URL = config("URL", default="http://localhost:8000")
SECRET_KEY = config("SECRET_KEY", cast=Secret, default="supersecretkey")
