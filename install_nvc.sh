#!/bin/bash
set -x
release="1.2.1"
if [ -z $(which nvc) ]
then
path="https://github.com/nickg/nvc/releases/download/r${release}/nvc-${release}.tar.gz"
wget -q -N ${path}
tar -xzvf nvc-${release}.tar.gz
pushd nvc-${release}
./tools/fetch-ieee.sh && ./configure --prefix=$HOME
make && make install
mkdir -p $HOME/.nvc/lib
./tools/build-2008-support.rb
popd
fi
