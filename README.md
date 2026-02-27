# SuperSaaS Auth Connector

Create a user in [SuperSaaS](https://www.supersaas.com/) and login them in once identified via OIDC.

* Uses the official SuperSaaS Python library
* Tested with Keycloak 26
* Creates users in SuperSaaS after identifying them via Keycloak
* Forwards users to SuperSaaS once created
* Supports triggering a front-channel logout in Keycloak

The aim is to allow convenient onboarding for users with access to Keycloak, while still allowing
additional cloud-managed users in SuperSaaS itself as needed.

The application is delivered as a simple container images, containing a simple Starlette app that
implements the business logic.

It is strongly recommended that you deploy the service as SuperSaaS Me if you choose to run your own.

## Installation

Run the `ghcr.io/radiorabe/supersaasauthconnector:latest` in your preferred container runtime.

Configuration is done via ENV variables.

| Variable | Default |
| ---- | ---- |
| DEBUG | False |
| SSO_SERVER_URL | https://sso.rabe.ch/auth/ |
| SSO_REALM | rabe |
| SSO_CLIENT_ID | supersaas-auth-connector |
| ERROR_REDIRECT_URL | https://www.rabe.ch |
| LOGOUT_REDIRECT_URL | https://sso.rabe.ch/auth/realms/rabe/protocol/openid-connect/logout?redirect_uri=https%3A%2F%2Fwww.rabe.ch |
| SUPERSAAS_ACCOUNT_NAME | RaBe |
| SUPERSAAS_API_TOKEN | |
| PORT | 8000 |
| HOST | 127.0.0.1 |
| URL | http://localhost:8000 |
| SECRET_KEY | supersecretkey |

If you are not RaBe you will have to override most of these, if you are RaBe only some.

On the Keycloak side the configuration is fairly trivial. The client needs to be public.
We use the email claim from the jwt as well as an additional uid claim that you have to
map in Keycloak. Other than that there are no special requirements and you are free to
implement your own roles and scopes as required.

## Development

```bash
python -mvenv .venv
. .venv/bin/activate

python -mpip install poetry

poetry install

poetry run pytest

ruff check
ruff format
```

## Release Management

The CI/CD setup uses semantic commit messages following the [conventional commits standard](https://www.conventionalcommits.org/en/v1.0.0/).
The workflow is based on the [RaBe shared actions](https://radiorabe.github.io/actions/)
and uses [go-semantic-commit](https://go-semantic-release.xyz/)
to create new releases.

The commit message should be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

The commit contains the following structural elements, to communicate intent to the consumers of your library:

1. **fix:** a commit of the type `fix` patches gets released with a PATCH version bump
1. **feat:** a commit of the type `feat` gets released as a MINOR version bump
1. **BREAKING CHANGE:** a commit that has a footer `BREAKING CHANGE:` gets released as a MAJOR version bump
1. types other than `fix:` and `feat:` are allowed and don't trigger a release

If a commit does not contain a conventional commit style message you can fix
it during the squash and merge operation on the PR.

## Build Process

The CI/CD setup uses [Docker build-push Action](https://github.com/docker/build-push-action)
to publish container images. The workflow is based on the [RaBe shared actions](https://radiorabe.github.io/actions/).

## License

This application is free software: you can redistribute it and/or modify it under the terms of the GNU
Affero General Public License as published by the Free Software Foundation, version 3 of the License.

## Copyright

Copyright (c) 2025 - 2026 Radio Bern RaBe
