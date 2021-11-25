FROM python:3.9-slim-bullseye
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y\
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends pandoc proj-bin

# RUN  update-alternatives --install /usr/bin/python python /usr/bin/python3 1
RUN pip3 install --upgrade pip3

RUN pip3 install \
    numpy \
    pandas \
    tqdm \
    networkx \
    fastparquet \
    matplotlib \
    Shapely \
    pyproj \
    Rtree \
    geopandas \
    sphinx \
    nbsphinx \
    recommonmark \
    SWMM_xsections_shape_generator \
    pydata_sphinx_theme


RUN useradd -ms /bin/bash mp;
RUN chmod g+rw /home && \
    mkdir -p /home/mp && \
    chown -R mp:mp /home/mp

ENV HOME /home/mp
WORKDIR /home/mp

ENV SHELL /bin/bash

USER mp
