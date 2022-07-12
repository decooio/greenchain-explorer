# base image
FROM python:3.6-buster
ENV PYTHONUNBUFFERED 1

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip3 install --upgrade pip

# add requirements
COPY ./explorer-api/requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip3 install -r requirements.txt

# install requirements of local py-scale-codec
COPY ./py-scale-codec/requirements.txt /usr/src/app/py-scale-codec-requirements.txt
RUN pip3 install -r py-scale-codec-requirements.txt

# install rust for building wheel for `py-bip39-bindings<1,>=0.1.9`
RUN apt-get update
RUN apt-get install -y \
    build-essential \
    curl
RUN apt-get update
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustup install nightly-2022-05-18 && rustup default nightly-2022-05-18 && rustup target add wasm32-unknown-unknown --toolchain nightly-2022-05-18

# install requirements of local py-substrate-interface
COPY ./py-substrate-interface/requirements.txt /usr/src/app/py-substrate-interface-requirements.txt
RUN pip3 install -r py-substrate-interface-requirements.txt

# add app and required packages
COPY explorer-api /usr/src/app
COPY py-scale-codec /usr/src/app/py-scale-codec/
COPY py-substrate-interface /usr/src/app/py-substrate-interface/
