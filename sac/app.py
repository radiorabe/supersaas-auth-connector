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
    path: str
    params: str
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
            path="/api/login",
            params="",
            query=urlencode(query_params),
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
        (access_token, error) = self._handle_oidc(request)

        if error:
            logger.error("Error during OIDC handling: %s", error)
            return RedirectResponse(url=settings.ERROR_REDIRECT_URL)

        if request.url.path == "/logout":
            return await self._handle_next(request, call_next)

        if not access_token:
            logger.warning("No access token found, redirecting to auth")
            return self._auth()

        try:
            request.state.user = self.kc.userinfo(access_token)
        except KeycloakAuthenticationError:  # pragma: no cover
            logger.exception("Failed to fetch userinfo, redirecting to auth")
            request.session.pop("access_token", None)
            return self._auth()

        return await self._handle_next(request, call_next)

    def _handle_oidc(self, request: Request) -> tuple[str, str | None]:
        access_token: str = ""
        if request.url.path == "/oidc/callback":  # pragma: no cover
            if "error" in request.query_params:
                error = request.query_params["error"]
                logger.error("Error returned from OIDC provider: %s", error)
                return ("", error)
            access_token_response = self.kc.token(
                grant_type="authorization_code",
                code=request.query_params["code"],
                redirect_uri=f"{settings.URL}/oidc/callback",
            )
            request.session.setdefault(
                "access_token", access_token_response["access_token"]
            )
            access_token = str(access_token_response["access_token"])

        return (access_token or str(request.session.get("access_token") or ""), None)

    async def _handle_next(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        return await call_next(request)

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


def logout_redirect(_: Request) -> Response:
    """Logout user by redirecting to logout URL (front-channel logout)."""
    return RedirectResponse(url=settings.LOGOUT_REDIRECT_URL)


app = Starlette(
    debug=settings.DEBUG,
    routes=[
        Route("/", endpoint=catchall_page),
        Route("/oidc/callback", endpoint=catchall_page),
        Route("/supersaas", endpoint=supersaas_redirect),
        Route("/logout", endpoint=logout_redirect),
    ],
)

# Add auth middleware
app.add_middleware(
    _AuthenticationMiddleware,
    kc=KeycloakOpenID(
        server_url=settings.SSO_SERVER_URL,
        client_id=settings.SSO_CLIENT_ID,
        realm_name=settings.SSO_REALM,
    ),
)
# Add context and session middlewares
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
    # Configure SuperSaaS client
    Client.configure(
        api_key=settings.SUPERSAAS_API_TOKEN,
        account_name=settings.SUPERSAAS_ACCOUNT_NAME,
    )
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)


if __name__ == "__main__":  # pragma: no cover
    main()
