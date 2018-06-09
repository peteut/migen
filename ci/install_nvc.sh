#!/bin/bash
set -x
release="1.3.1"
if [ -z $(which nvc) ]
then
path="https://github.com/nickg/nvc/releases/download/r${release}/nvc-${release}.tar.gz"
curl -sL  ${path} | tar -xzf -
pushd nvc-${release}
patch -p1 < ../ci/ieee-download-webpage-has-changed-375.patch
./tools/fetch-ieee.sh && ./configure --prefix=${HOME} --with-llvm=${LLVM_CONFIG}
make && make install
mkdir -p ${HOME}/.nvc/lib
./tools/build-2008-support.rb
popd
fi
