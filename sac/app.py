"""Main application file for the SuperSaaS authentication connector."""

from __future__ import annotations

import hashlib
import logging
from typing import TYPE_CHECKING, NamedTuple
from urllib.parse import urlencode, urlunparse

import uvicorn
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route
from starlette_context import plugins
from starlette_context.middleware import ContextMiddleware
from SuperSaaS import Client  # type: ignore[import-untyped]

from sac import settings

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.types import ASGIApp


class _URIComponents(NamedTuple):
    scheme: str
    netloc: str
    url: str
    path: str
    query: str
    fragment: str


logger = logging.getLogger("supersaas-auth-connector")
logger.setLevel(logging.DEBUG)


def _create_user(name: str, user_id: str) -> None:  # pragma: no cover
    Client.instance().users.create(attributes={"name": name}, user_id=f"{user_id}fk")


def _generate_supersaas_login_url(name: str) -> str:
    checksum = hashlib.md5(  # noqa: S324
        (
            f"{settings.SUPERSAAS_ACCOUNT_NAME}{settings.SUPERSAAS_API_TOKEN}{name}"
        ).encode()
    ).hexdigest()

    query_params = {
        "account": settings.SUPERSAAS_ACCOUNT_NAME,
        "user[name]": name,
        "checksum": checksum,
    }

    return urlunparse(
        _URIComponents(
            scheme="https",
            netloc="www.supersaas.com",
            query=urlencode(query_params),
            path="",
            url="/api/login",
            fragment="",
        )
    )


class _AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, kc: KeycloakOpenID) -> None:
        super().__init__(app)
        self.kc = kc

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        access_token = self._handle_oidc(request)

        if not access_token:
            logger.warning("No access token found, redirecting to auth")
            return self._auth()

        try:
            request.state.user = self.kc.userinfo(access_token)
        except KeycloakAuthenticationError:  # pragma: no cover
            logger.exception("Failed to fetch userinfo, redirecting to auth")
            request.session.pop("access_token", None)
            return self._auth()

        try:
            response = await call_next(request)
        except BaseException as e:  # pragma: no cover
            raise e from None
        return response

    def _handle_oidc(self, request: Request) -> str:
        access_token: str = ""
        if request.url.path == "/oidc/callback":  # pragma: no cover
            access_token_response = self.kc.token(
                grant_type="authorization_code",
                code=request.query_params["code"],
                redirect_uri=f"{settings.URL}/oidc/callback",
            )
            request.session.setdefault(
                "access_token", access_token_response["access_token"]
            )
            access_token = str(access_token_response["access_token"])

        return access_token or str(request.session.get("access_token") or "")

    def _auth(self) -> Response:
        return Response(
            status_code=307,
            headers={
                "Location": self.kc.auth_url(
                    redirect_uri=f"{settings.URL}/oidc/callback",
                )
            },
        )


def catchall_page(_: Request) -> Response:  # pragma: no cover
    """Redirect to /supersaas for user creation and redirection to SuperSaaS."""
    return RedirectResponse(url="/supersaas")


def supersaas_redirect(request: Request) -> Response:
    """Create user in SuperSaaS if not exists and redirect to SuperSaaS login URL."""
    name = request.state.user.get("email")
    _create_user(name=name, user_id=request.state.user.get("uid"))
    return RedirectResponse(url=_generate_supersaas_login_url(name))


app = Starlette(
    debug=settings.DEBUG,
    routes=[
        Route("/", endpoint=catchall_page),
        Route("/oidc/callback", endpoint=catchall_page),
        Route("/supersaas", endpoint=supersaas_redirect),
    ],
)

## Add auth middleware
app.add_middleware(
    _AuthenticationMiddleware,
    kc=KeycloakOpenID(
        server_url=settings.SSO_SERVER_URL,
        client_id=settings.SSO_CLIENT_ID,
        realm_name=settings.SSO_REALM,
    ),
)
## Add context and session middlewares
app.add_middleware(
    ContextMiddleware,
    plugins=(
        plugins.RequestIdPlugin(),
        plugins.CorrelationIdPlugin(),
    ),
)
app.add_middleware(SessionMiddleware, secret_key=str(settings.SECRET_KEY))


def main() -> None:  # pragma: no cover
    """Run the application with Uvicorn."""
    ## Configure SuperSaaS client
    Client.configure(
        api_key=settings.SUPERSAAS_API_TOKEN,
        account_name=settings.SUPERSAAS_ACCOUNT_NAME,
    )
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)


if __name__ == "__main__":  # pragma: no cover
    main()
