from unittest.mock import patch

from starlette.testclient import TestClient

from sac.app import app


def test_no_auth():
    client = TestClient(app, root_path="/", follow_redirects=False)
    response = client.get("/supersaas")
    assert response.status_code == 307  # noqa: PLR2004
    assert response.headers["Location"].startswith("https://sso.rabe.ch")


@patch("sac.app._AuthenticationMiddleware._handle_oidc")
@patch("keycloak.keycloak_openid.KeycloakOpenID.userinfo")
@patch("sac.app._create_user")
def test_supersaas_auth(create_mock, userinfo_mock, oidc_mock):
    oidc_mock.return_value = ("valid_token", None)
    userinfo_mock.return_value = {"email": "testuser@example.org", "uid": "1000"}
    create_mock.return_value = None

    client = TestClient(app, follow_redirects=False)
    response = client.get("/supersaas")
    assert response.status_code == 307  # noqa: PLR2004
    assert response.headers["Location"].startswith("https://www.supersaas.com")


@patch("sac.app._AuthenticationMiddleware._handle_oidc")
@patch("keycloak.keycloak_openid.KeycloakOpenID.userinfo")
@patch("sac.app._create_user")
def test_supersaas_no_consent(create_mock, userinfo_mock, oidc_mock):
    oidc_mock.return_value = ("", "access_denied")

    client = TestClient(app, follow_redirects=False)
    response = client.get("/supersaas")
    assert response.status_code == 307  # noqa: PLR2004
    assert response.headers["Location"] == "https://www.rabe.ch"
    assert not userinfo_mock.called
    assert not create_mock.called
