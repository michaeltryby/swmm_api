FROM debian:buster-slim
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y\
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3 python3-pip \
    python3-setuptools python3-wheel gcc python3-dev git

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

RUN apt install pandoc -y

RUN pip3 install \
    numpy \
    pandas \
    networkx \
    tqdm \
    swmmtoolbox \
    fastparquet \
    sphinx \
    nbsphinx \
    sphinx-rtd-theme \
    recommonmark


RUN useradd -ms /bin/bash mp;
RUN chmod g+rw /home && \
    mkdir -p /home/mp && \
    chown -R mp:mp /home/mp

ENV HOME /home/mp
WORKDIR /home/mp

ENV SHELL /bin/bash

USER mp
