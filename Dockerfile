FROM python:2.7

# see: https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/#build-cache#run
RUN apt-get update \
  && apt-get install -y --no-install-recommends freetds-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /code
ADD Makefile ./

# add requirements.txt before rest of repo so Docker will cache pip install
ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD README.md setup.cfg setup.py ./
ADD stethoscope ./stethoscope/
ADD instance ./instance/
ADD config ./config/

RUN make install-editable-package
