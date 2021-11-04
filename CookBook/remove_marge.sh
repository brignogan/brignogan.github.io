#!/bin/bash
#
pdftk A=cookbook.pdf cat Aeven output tmp_even.pdf 
pdftk A=cookbook.pdf cat Aodd output  tmp_odd.pdf 

pdfjam --fitpaper true --trim "0 0 3mm 0" tmp_odd.pdf -o tmp_odd_marge.pdf
pdfjam --fitpaper true --trim "3mm 0 0 0" tmp_even.pdf -o tmp_even_marge.pdf

pdftk A=tmp_odd_marge.pdf B=tmp_even_marge.pdf shuffle A B output cookbook_Nomarge.pdf
rm tmp_*.pdf
