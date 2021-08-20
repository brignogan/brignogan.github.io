#/bin/bash
#
set -e 
set -o pipefail
DIRECTORY=`dirname $0`
cd $DIRECTORY
source $PATH_ANACONDA3/bin/activate cookbook
rm -f ./VinData/listVins.gpkg
python generate_vin.py -s True --flag_vin True
python generate_recipe.py --flag_latex False
python generate_vin.py -s True
python generate_recipe.py --flag_latex True

