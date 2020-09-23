rm img/kardinalschnittenSchema.pdf
pdflatex --shell-escape  main.tex
ln -fs addText2Img/img/kardinalschnittenSchema.pdf ../
