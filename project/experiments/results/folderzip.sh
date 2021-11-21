#!/bin/bash

for f in *; do
    if [ -d "$f" ]; then
        # f is a dir
        echo "$f"
        zip -r "$f.zip" "$f"
    fi
done