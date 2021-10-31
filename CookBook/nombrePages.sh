FILENAME="cookbook.pdf"#"$1"

# https://stackoverflow.com/questions/1672580/get-number-of-pages-in-a-pdf-using-a-cmd-batch-file
# Uses pdfinfo to find general information, focusing on the number of pages from which only the number is extracted.
NPAGES=$(pdfinfo "$FILENAME" | grep Pages | sed 's/[^0-9]*//')

# https://root42.blogspot.com/2012/10/counting-color-pages-in-pdf-files.html
# Uses ghostscript to measure any deviation from black in the ink colour used on pages.
GHOSTOUT=$(gs -o - -sDEVICE=inkcov $FILENAME | grep -v "^ 0.00000  0.00000  0.00000" | grep "^ " | wc -l)

# Use echo and sed to grab the number isolated from the other text.
NCOLOURPAGES=$(echo $GHOSTOUT | sed 's/[^0-9]*//')

# Echo all three desired properties
echo -e "Number of pages:\t $NPAGES"
echo -e "Number of b&w: \t\t $((${NPAGES}-${NCOLOURPAGES}))"
echo -e "Number of colour:\t $NCOLOURPAGES"
