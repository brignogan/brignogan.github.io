#!/bin/bash
#
bw=`gs -q  -o - -sDEVICE=inkcov cookbook.pdf  | grep '^ 0.00000  0.00000  0.00000' | wc -l`
color=`gs -q  -o - -sDEVICE=inkcov cookbook.pdf  | grep -v '^ 0.00000  0.00000  0.00000' | wc -l`
echo $bw ' pages en noir et blanc'
echo $color ' pages en couleur'
