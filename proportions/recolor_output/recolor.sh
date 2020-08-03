#!/bin/bash

mkdir recolored_images /
for f in *;
    do gdaldem color-relief $f col.txt ./recolored_images/$f -nearest_color_entry;
    done

