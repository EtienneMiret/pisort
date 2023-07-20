#!/bin/sh

I=0

for FILE in *.JPG
do
  I=$((I + 1))
  mv -n "$FILE" "$I.jpg"
done
