FROM ghcr.io/radiorabe/s2i-python:3.4.0 AS build

COPY ./ /opt/app-root/src

RUN    cd /opt/app-root/src \
    && python -mpip --no-cache-dir install wheel \
    && python -mbuild


FROM ghcr.io/radiorabe/python-minimal:3.3.0 AS app

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
