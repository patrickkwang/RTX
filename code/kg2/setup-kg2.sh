#!/bin/bash
set -euxo pipefail

## setup the shell variables for various directories
BUILD_DIR=~/kg2-build

## create the "build" directory where we will store the KG2 files:
mkdir -p ${BUILD_DIR}

cat >${BUILD_DIR}/master-config.shinc <<EOF
BUILD_DIR=${BUILD_DIR}
VENV_DIR=~/kg2-venv
CODE_DIR=~/kg2-code
S3_REGION=us-west-2
S3_BUCKET=rtx-kg2
EOF

source ${BUILD_DIR}/master-config.shinc

## sym-link into RTX/code/kg2
ln -s ~/RTX/code/kg2 ${CODE_DIR}

## install the Linux distro packages that we need
sudo apt-get update
sudo apt-get install -y python3-minimal \
     python3-pip \
     default-jre \
     awscli \
     zip \
     curl \
     wget \
     flex \
     bison \
     libxml2-dev \
     gtk-doc-tools \
     libtool

## this is for convenience when I am remote working
sudo apt-get install -y emacs

## the only python package we need to install into the native python3 is virtualenv
sudo -H pip3 install virtualenv

## create a virtualenv for building KG2
virtualenv ${VENV_DIR}

## Install python3 packages that we will need (Note: we are not using pymongo
## directly, but installing it silences a runtime warning from ontobio):
${VENV_DIR}/bin/pip3 install ontobio pymongo

## make local copies of the config files in the build dir
cp ${CODE_DIR}/curies-to-categories.yaml ${BUILD_DIR}
cp ${CODE_DIR}/curies-to-urls-lookaside-list.yaml ${BUILD_DIR}
cp ${CODE_DIR}/owl-load-inventory.yaml ${BUILD_DIR}

## install ROBOT (software: ROBOT is an OBO Tool) by downloading the jar file
## distribution and cURLing the startup script
curl -LO -o ${BUILD_DIR}/robot.jar ${BUILD_DIR} https://github.com/RTXteam/robot/releases/download/v1.3.0/robot.jar
curl https://raw.githubusercontent.com/RTXteam/robot/v1.3.0/bin/robot > ${BUILD_DIR}/robot
chmod a+x ${BUILD_DIR}/robot

## setup owltools
curl -LO -o ${BUILD_DIR}/owltools https://github.com/RTXteam/owltools/releases/download/v0.3.0/owltools
chmod a+x ${BUILD_DIR}/owltools

## setup AWS CLI
if ! aws s3 cp --region ${S3_REGION} s3://${S3_BUCKET}/test .; then
    aws configure
else
    rm test
fi

# setup raptor
wget -P ${BUILD_DIR} http://download.librdf.org/source/raptor2-2.0.15.tar.gz
tar xzf -C ${BUILD_DIR} ${BUILD_DIR}/raptor2-2.0.15.tar.gz
cd ${BUILD_DIR}/raptor2-2.0.15
./autogen.sh --prefix=/usr/local
make
make check
sudo make install
sudo ldconfig
cd ${UMLS_DIR}/umls2rdf
./checkOutputSyntax.sh
