FROM python:3.10-slim-bookworm
# https://github.com/imranq2/docker.spark_python
USER root

COPY Pipfile* /src/
WORKDIR /src

RUN python3 -m pip install --upgrade pip && python -m pip install --no-cache-dir pipenv
RUN pipenv lock && pipenv sync --dev --system && pipenv-setup sync --pipfile

COPY . /src

# run pre-commit once so it installs all the hooks and subsequent runs are fast
#RUN cd /src && pre-commit install

# USER 1001
