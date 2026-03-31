# Getting Started

SuperSaaS Auth Connector bridges [Keycloak](https://www.keycloak.org/) OIDC authentication
with [SuperSaaS](https://www.supersaas.com/) user management.
This guide walks you through deploying the connector for the first time.

## Prerequisites

| Requirement | Notes |
|---|---|
| Container runtime | Docker, Podman, or any OCI-compatible runtime |
| Keycloak ≥ 26 | A public OIDC client configured (see [Keycloak Setup](#keycloak-setup)) |
| SuperSaaS account | An API token with permission to create users |

## Quick Start

Pull and run the latest image:

```bash
podman run --rm \
  -e SSO_SERVER_URL=https://sso.example.com/auth/ \
  -e SSO_REALM=myrealm \
  -e SSO_CLIENT_ID=supersaas-auth-connector \
  -e SUPERSAAS_ACCOUNT_NAME=myaccount \
  -e SUPERSAAS_API_TOKEN=mysecrettoken \
  -e URL=https://auth.example.com \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  -p 8000:8000 \
  ghcr.io/radiorabe/supersaasauthconnector:latest
```

The service listens on port `8000` by default.
Point your Keycloak client's redirect URI to `https://auth.example.com/oidc/callback`.

## Keycloak Setup

1. Create a new **public** client (no client secret required).
2. Set the **Valid Redirect URIs** to `https://auth.example.com/oidc/callback`.
3. Add a **Protocol Mapper** to the client (or the realm's user profile) that maps the
   internal Keycloak user attribute `uid` to the `uid` token claim:
   - **Mapper type**: User Attribute
   - **User Attribute**: `uid` (or the LDAP/federated attribute name you use)
   - **Token Claim Name**: `uid`
   - **Claim JSON Type**: String
   - **Add to userinfo**: ✅ enabled

!!! tip
    The `uid` claim is used as the SuperSaaS user identifier (suffixed with `fk`).
    Map it to a stable, unique attribute in Keycloak — for example the internal Keycloak
    user UUID or an LDAP `uidNumber`.

## Compose Example

```yaml title="compose.yaml"
services:
  supersaas-auth-connector:
    image: ghcr.io/radiorabe/supersaasauthconnector:latest
    restart: unless-stopped
    environment:
      SSO_SERVER_URL: https://sso.example.com/auth/
      SSO_REALM: myrealm
      SSO_CLIENT_ID: supersaas-auth-connector
      SUPERSAAS_ACCOUNT_NAME: myaccount
      SUPERSAAS_API_TOKEN: ${SUPERSAAS_API_TOKEN}
      URL: https://auth.example.com
      SECRET_KEY: ${SECRET_KEY}
      ERROR_REDIRECT_URL: https://www.example.com
      LOGOUT_REDIRECT_URL: >-
        https://sso.example.com/auth/realms/myrealm/protocol/openid-connect/logout
        ?redirect_uri=https%3A%2F%2Fwww.example.com
    ports:
      - "8000:8000"
```

Store `SUPERSAAS_API_TOKEN` and `SECRET_KEY` in a `.env` file or your secrets manager —
never commit them to source control.

## Next Steps

- Read the full [Configuration Reference](configuration.md) for every available variable.
- Understand the [Architecture](architecture.md) to see how requests flow through the system.
- Set up a [Development Environment](development.md) to contribute or customise the connector.
