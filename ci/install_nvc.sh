#!/bin/bash
set -x
release="1.4.0"
if [ -z $(which nvc) ]; then
path="https://github.com/nickg/nvc/releases/download/r${release}/nvc-${release}.tar.gz"
curl -sL  ${path} | tar -xzf -
pushd nvc-${release}
patch -p1  < ../ci/Fix-IEEE-download-URL.patch
./tools/fetch-ieee.sh
./configure --prefix=${1} --with-llvm=${LLVM_CONFIG}
make
make install
mkdir -p ${HOME}/.nvc/lib
./tools/build-2008-support.rb
popd
fi
