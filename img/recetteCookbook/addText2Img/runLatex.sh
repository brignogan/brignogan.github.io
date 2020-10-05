set -e
set -o pipefail
DIRECTORY=`dirname $0`
cd $DIRECTORY
[ -e  img/kardinalschnittenSchema.pdf ] && rm img/kardinalschnittenSchema.pdf
[ -e  img/sachertorteglacage2.pdf ] && rm img/sachertorteglacage2.pdf
pdflatex --shell-escape  main.tex
ln -fs addText2Img/img/kardinalschnittenSchema.pdf ../
ln -fs addText2Img/img/sachertorteglacage2.pdf ../sachertorteglacage.pdf
