#!/bin/bash
set -x
function escape_slashes {
    sed 's/\//\\\//g'
}
if [ -z $(which nvc) ]
then
path="https://github.com/nickg/nvc/releases/download/r1.1.0/nvc-1.1.0.tar.gz"
wget -q -N ${path}
tar -xzvf nvc-1.1.0.tar.gz
pushd nvc-1.1
fetch_ieee="./tools/fetch-ieee.sh"
gna_path=$(echo "http://svn.gna.org/svn/ghdl/trunk/libraries/vital2000" | escape_slashes)
github_path=$(echo "https://raw.githubusercontent.com/tgingold/ghdl/master/libraries/vital2000" | escape_slashes)
echo "gna_path: ${gna_path}"
echo "github_path: ${github_path}"
sed -i 's/'"${gna_path}"'/'"${github_path}"'/' ${fetch_ieee}
sed -i 's/03878edc834050f67ec5d3e0b49bef883065dc429700a174e93850274c63e458/507163c4530ffe894929caf604437c9a24dd8f4b347f0c01949d230fdfcd2825/' ${fetch_ieee}

./tools/fetch-ieee.sh && ./configure --prefix=$HOME
make && make install
mkdir -p $HOME/.nvc/lib
./tools/build-2008-support.rb
popd
fi
