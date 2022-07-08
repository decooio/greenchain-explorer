# base image
FROM python:3.8-buster
ENV PYTHONUNBUFFERED 1

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip3 install --upgrade pip

# add requirements
COPY ./harvester/requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com


# install requirements of local py-scale-codec
COPY ./py-scale-codec/requirements.txt /usr/src/app/py-scale-codec-requirements.txt
RUN pip3 install -r py-scale-codec-requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com

# install requirements of local py-substrate-interface
COPY ./py-substrate-interface/requirements.txt /usr/src/app/py-substrate-interface-requirements.txt
RUN pip3 install -r py-substrate-interface-requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com

# add app
COPY harvester /usr/src/app
COPY py-scale-codec /usr/src/app/py-scale-codec/
COPY py-substrate-interface /usr/src/app/py-substrate-interface/
