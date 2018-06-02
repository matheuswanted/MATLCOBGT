FROM ubuntu:16.04 as envi

LABEL Description="Dockerised Simulation of Urban MObility(SUMO)"

ENV SUMO_VERSION 0.32.0
ENV SUMO_HOME /opt/sumo

# Install system dependencies.
RUN apt-get update && apt-get -qq install \
    wget \
    g++ \
    make \
    libxerces-c-dev \
    libfox-1.6-0 libfox-1.6-dev \
    vim

RUN apt-get -qq install \
    python2.7 \
    python-numpy \ 
    python-scipy 

# Download and extract source code
RUN wget http://downloads.sourceforge.net/project/sumo/sumo/version%20$SUMO_VERSION/sumo-src-$SUMO_VERSION.tar.gz
RUN tar xzf sumo-src-$SUMO_VERSION.tar.gz && \
    mv sumo-$SUMO_VERSION $SUMO_HOME && \
    rm sumo-src-$SUMO_VERSION.tar.gz

# Configure and build from source.
RUN cd $SUMO_HOME && ./configure && make install
RUN chmod -R 777 $SUMO_HOME 
RUN adduser ${USER:-matheus_souza1} --disabled-password

#RUN apt-get -qq install python-pip
FROM envi as tests
CMD python2.7 tests.py

#RUN pip install numpy scipy

FROM envi

RUN apt-get -qq install \
    python-pip

RUN pip install \
     ptvsd

EXPOSE 3000
WORKDIR app
#CMD python2.7 -u runner.py --nogui 
CMD BASH