FROM ghcr.io/radiorabe/s2i-python:3.5.0@sha256:8c020bc0808b8fac25cad6a1e849d0d4c305417ebcdeb9d9ac0fe4c6e430eb23 AS build

COPY ./ /opt/app-root/src

RUN    cd /opt/app-root/src \
    && python -mpip --no-cache-dir install wheel \
    && python -mbuild


FROM ghcr.io/radiorabe/python-minimal:3.4.0@sha256:371258ed70856e017b60c95201643cedaeae7a97bb78fc134be845a09dfb2dcf AS app

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
