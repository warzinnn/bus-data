#!/bin/bash

# CONFIGURING VM IN GOOGLE COMPUTE ENGINE

sudo apt-get update &&
sudo apt-get install -y docker.io &&
mkdir ${HOME}/bin &&
wget https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-linux-x86_64 -O docker-compose &&
chmod +x docker-compose &&
mv docker-compose ${HOME}/bin/ &&
chmod +x ${HOME}/bin/docker-compose &&
echo 'export PATH="${HOME}/bin:${PATH}"' >> ~/.bashrc &&
source ${HOME}/.bashrc &&
sudo groupadd docker &&
sudo gpasswd -a $USER docker &&
sudo service docker restart