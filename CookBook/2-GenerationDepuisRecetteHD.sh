#/bin/bash
#
set -e 
set -o pipefail
DIRECTORY=`dirname $0`
cd $DIRECTORY
export flagHD=True
source $PATH_ANACONDA3/bin/activate cookbook
python generate_recipe.py --flag_latex False -hd $flagHD
python generate_vin.py -s True
python generate_recipe.py --flag_latex True -hd $flagHD
