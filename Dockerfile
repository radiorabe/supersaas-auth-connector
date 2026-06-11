FROM ghcr.io/radiorabe/s2i-python:3.4.4@sha256:16aba71b85c5d048a1abb368236a85e758ae8b2e099eb59e0aa6873f8d532826 AS build

COPY ./ /opt/app-root/src

RUN    cd /opt/app-root/src \
    && python -mpip --no-cache-dir install wheel \
    && python -mbuild


FROM ghcr.io/radiorabe/python-minimal:3.3.4@sha256:595d5e42983954707aab8526b7ec39b12d8946a5567869defa9a35abdc139f79 AS app

COPY --from=build /opt/app-root/src/dist/*.whl /tmp/dist/

RUN    microdnf install -y \
         python3.12-pip \
    && python -mpip --no-cache-dir install /tmp/dist/*.whl \
    && microdnf remove -y \
         python3.12-pip \
         python3.12-setuptools \
    && microdnf clean all \
    && rm -rf /tmp/dist/

USER nobody

CMD ["supersaas-auth-connector"]
