ARG PYTHON_VERSION=3.8
FROM ubuntu:latest as base
WORKDIR /application
ARG PYTHON_VERSION
RUN apt-get update
RUN apt-get install -y python${PYTHON_VERSION}

FROM base as version3.8
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-pip
RUN pip3 install pytest
RUN pip3 install pylint

FROM base as version2.7
RUN apt-get install -y python-dev
RUN apt-get install -y g++
RUN apt-get install -y curl 
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN ["python2.7","get-pip.py"]
RUN pip install pytest
RUN pip install pylint

FROM version${PYTHON_VERSION} as final

