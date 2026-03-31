# Configuration

All settings are loaded from **environment variables** using
[Starlette Config](https://www.starlette.io/config/).
You can also place them in a `.env` file in the working directory.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DEBUG` | `False` | Enable Starlette debug mode (never use in production) |
| `SSO_SERVER_URL` | `https://sso.rabe.ch/auth/` | Base URL of your Keycloak server |
| `SSO_REALM` | `rabe` | Keycloak realm name |
| `SSO_CLIENT_ID` | `supersaas-auth-connector` | Keycloak client ID (must be public) |
| `ERROR_REDIRECT_URL` | `https://www.rabe.ch` | Where to send users when authentication fails |
| `LOGOUT_REDIRECT_URL` | *(see below)* | Front-channel logout URL including `redirect_uri` parameter |
| `SUPERSAAS_ACCOUNT_NAME` | `RaBe` | Your SuperSaaS account name |
| `SUPERSAAS_API_TOKEN` | *(empty)* | SuperSaaS API token — **required** in production |
| `PORT` | `8000` | TCP port the application binds to |
| `HOST` | `127.0.0.1` | Host address the application binds to |
| `URL` | `http://localhost:8000` | Public base URL of this connector (used to build the OIDC callback URI) |
| `SECRET_KEY` | `supersecretkey` | Secret used to sign the session cookie — **change this in production** |

Default value for `LOGOUT_REDIRECT_URL`:

```
https://sso.rabe.ch/auth/realms/rabe/protocol/openid-connect/logout
  ?redirect_uri=https%3A%2F%2Fwww.rabe.ch
```

## Keycloak Variables

### `SSO_SERVER_URL`

The full URL to your Keycloak server **including the `/auth/` path component** (required for
Keycloak ≥ 17 when the legacy `/auth` prefix is still active) or without it for newer
deployments. Check your Keycloak version's expected base URL format.

```
SSO_SERVER_URL=https://sso.example.com/auth/
```

### `SSO_REALM`

The name of the Keycloak realm that contains your users and the OIDC client.

```
SSO_REALM=myrealm
```

### `SSO_CLIENT_ID`

The client ID registered in Keycloak. The client must be configured as **public** (no client
secret). Set the **Valid Redirect URIs** in Keycloak to `${URL}/oidc/callback`.

```
SSO_CLIENT_ID=supersaas-auth-connector
```

## SuperSaaS Variables

### `SUPERSAAS_ACCOUNT_NAME`

Your SuperSaaS account name, visible in your SuperSaaS dashboard URL
(`https://www.supersaas.com/accounts/<name>/...`).

```
SUPERSAAS_ACCOUNT_NAME=mycompany
```

### `SUPERSAAS_API_TOKEN`

Your SuperSaaS API token. Find it under **Account → API** in the SuperSaaS settings.
Treat this value as a secret — pass it via an environment variable or secrets manager,
never bake it into an image or commit it to source control.

```
SUPERSAAS_API_TOKEN=abc123...
```

## Application Variables

### `URL`

The publicly reachable base URL of this connector. This is used to construct the OIDC
callback redirect URI (`${URL}/oidc/callback`) that is registered in Keycloak and sent
during the authorization-code flow.

```
URL=https://auth.example.com
```

### `SECRET_KEY`

The secret key used to sign the session cookie (via
[itsdangerous](https://itsdangerous.palletsprojects.com/)). Generate a strong random value:

```bash
openssl rand -hex 32
```

!!! warning
    The default value `supersecretkey` is intentionally insecure and must be changed in
    any production deployment.

### `ERROR_REDIRECT_URL`

Users are redirected here when an OIDC error is returned by Keycloak (e.g. the user
cancelled the login). Typically your main website URL.

```
ERROR_REDIRECT_URL=https://www.example.com
```

### `LOGOUT_REDIRECT_URL`

The full Keycloak front-channel logout URL. After the session is cleared, users are
redirected to this URL. Include the `redirect_uri` query parameter to send users to
a specific page after logout.

```
LOGOUT_REDIRECT_URL=https://sso.example.com/auth/realms/myrealm/protocol/openid-connect/logout?redirect_uri=https%3A%2F%2Fwww.example.com
```

## Runtime Variables

| Variable | Default | Notes |
|---|---|---|
| `HOST` | `127.0.0.1` | Bind address. Set to `0.0.0.0` inside a container. The container image already sets this. |
| `PORT` | `8000` | Bind port. |
| `DEBUG` | `False` | Enables Starlette's interactive debugger. **Never enable in production.** |
