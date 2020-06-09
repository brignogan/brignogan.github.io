#/bin/bash
#
DIRECTORY=`dirname $0`
cd $DIRECTORY
source $PATH_ANACONDA2/bin/activate cookbook
python generate_vin.py -s False
python generate_recipe.py --flag_latex False
python generate_vin.py -s True
python generate_recipe.py --flag_latex True

