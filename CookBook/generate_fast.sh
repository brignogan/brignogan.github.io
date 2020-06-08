#/bin/bash
#
source ~/anaconda2/bin/activate cookbook
python generate_recipe.py --flag_latex False
python generate_vin.py -s True
python generate_recipe.py --flag_latex True

