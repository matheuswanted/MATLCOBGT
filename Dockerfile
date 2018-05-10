FROM ubuntu:16.04

LABEL Description="Dockerised Simulation of Urban MObility(SUMO)"

ENV SUMO_VERSION 0.32.0
ENV SUMO_HOME /opt/sumo
ENV SUMO_USER=$USER

# Install system dependencies.
RUN apt-get update && apt-get -qq install \
    wget \
    g++ \
    make \
    libxerces-c-dev \
    libfox-1.6-0 libfox-1.6-dev \
    python2.7 \
    vim

# Download and extract source code
RUN wget http://downloads.sourceforge.net/project/sumo/sumo/version%20$SUMO_VERSION/sumo-src-$SUMO_VERSION.tar.gz
RUN tar xzf sumo-src-$SUMO_VERSION.tar.gz && \
    mv sumo-$SUMO_VERSION $SUMO_HOME && \
    rm sumo-src-$SUMO_VERSION.tar.gz

# Configure and build from source.
RUN cd $SUMO_HOME && ./configure && make install
RUN chmod -R 777 $SUMO_HOME
RUN adduser $SUMO_USER --disabled-password

#workdir $SUMO_HOME/docs/tutorial/traci_tls
WORKDIR app
CMD python2.7 runner.py --nogui && cat tripinfo.xml
# CMD sumo-gui