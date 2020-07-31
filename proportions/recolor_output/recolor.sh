#!/bin/bash

mkdir recolor/
for f in *;
    do gdaldem color-relief $f col.txt ./recolor/$f;
    done

