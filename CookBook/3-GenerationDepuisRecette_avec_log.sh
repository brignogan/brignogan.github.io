#/bin/bash
#
set -e
set -o pipefail
DIRECTORY=`dirname $0`
cd $DIRECTORY
source $PATH_ANACONDA2/bin/activate cookbook
./2-GenerationDepuisRecette.sh >& output.txt
