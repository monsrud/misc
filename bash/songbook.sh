#!/bin/bash

# Make an indexed songbook pdf out of doc/docx/chordrpo files and/or any pdf files in a directory too.

# requires lowriter ; apt install libreoffice-writer 
# requires pdftk ;  apt install pdftk
# requires pdfinfo ;  apt install poppler-utils
# requres libwx-perl; apt install libwx-perl
# sudo apt install libreoffice-writer pdftk poppler-utils libwx-perl

# requres chordpro
# sudo cpan install chordpro

rm -f 000_SongBook.pdf
rm -f /tmp/data

#lowriter --headless --convert-to pdf *.docx
#lowriter --headless --convert-to pdf *.doc
#for i in *.pro; do
#    chordpro --generate=PDF --no-csv $i
#done


# chordpro --generate=PDF --output=filename.pdf --no-csv filename.pro

tempdata="/tmp/data"

pagenumber=1

for i in *.pdf; do

    # get the number of pages
    pages=$(pdfinfo "$i" | awk '/^Pages:/ {print $2}')
    if [ $pages -gt 1 ]; then
        echo "Skipping $i $pages is more than 1 page long."
        continue
    fi

    # remove bookmarks from files
    pdftk A="${i}" cat A1-end output "${i}.tmp" 
    mv "${i}.tmp" "$i"

    printf "BookmarkBegin\nBookmarkTitle: %s\nBookmarkLevel: 1\nBookmarkPageNumber: ${pagenumber}\n" "${i%.*}">> "$tempdata"

    pagenumber=$((++pagenumber))

done

# print the book
pdftk *.pdf cat output 000_SongBook.tmp.pdf

# add the new bookmarks
pdftk 000_SongBook.tmp.pdf update_info "$tempdata" output 000_SongBook.pdf 
rm -f 000_SongBook.tmp.pdf


