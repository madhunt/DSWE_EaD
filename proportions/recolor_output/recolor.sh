#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

mkdir recolored_images
for file in *; do
    if [[ $file = *'nonwater'* ]]; then
        gdaldem color-relief "$file" "$DIR"/col_nonwater.txt ./recolored_images/"$file";
    elif [[ $file = *'open_sw'* ]]; then
        gdaldem color-relief "$file" "$DIR"/col_open_sw.txt ./recolored_images/"$file";
    elif [[ $file = *'partial_sw'* ]]; then
        gdaldem color-relief "$file" "$DIR"/col_partial_sw.txt ./recolored_images/"$file";
    fi

done
