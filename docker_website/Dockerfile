FROM python:slim-bullseye
ENV DEBIAN_FRONTEND noninteractive

RUN apt install pandoc proj-bin -y

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
    sphinx-rtd-theme \
    recommonmark \
    SWMM_xsections_shape_generator


RUN useradd -ms /bin/bash mp;
RUN chmod g+rw /home && \
    mkdir -p /home/mp && \
    chown -R mp:mp /home/mp

ENV HOME /home/mp
WORKDIR /home/mp

ENV SHELL /bin/bash

USER mp
