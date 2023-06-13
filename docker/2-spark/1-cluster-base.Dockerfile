FROM debian:bullseye

RUN mkdir /opt/workspace && \
    apt-get update -y && \
    apt-get install -y curl python3 python3-pip vim && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/* && \
    curl https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz -o openjdk-11.0.2_linux-x64_bin.tar.gz && \
    tar xzfv openjdk-11.0.2_linux-x64_bin.tar.gz && \
    mkdir -p /opt/java && \
    mv jdk-11.0.2 /opt/java && \
    rm openjdk-11.0.2_linux-x64_bin.tar.gz && \
    echo 'export JAVA_HOME="/opt/java/jdk-11.0.2"' >> ~/.bashrc && \ 
    echo 'export PATH="${JAVA_HOME}/bin:${PATH}"' >> ~/.bashrc
    
COPY requirements.txt .

RUN pip3 install -r requirements.txt

VOLUME /opt/workspace
CMD ["/bin/bash"]