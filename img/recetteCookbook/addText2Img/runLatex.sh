set -e
set -o pipefail
DIRECTORY=`dirname $0`
cd $DIRECTORY
[ -e  img/kardinalschnittenSchema.pdf ] && rm img/kardinalschnittenSchema.pdf
[ -e  img/sachertorteglacage.pdf ] && rm img/sachertorteglacage.pdf
pdflatex --shell-escape  main.tex
ln -fs addText2Img/img/kardinalschnittenSchema.pdf ../
ln -fs addText2Img/img/sachertorteglacage.pdf ../
