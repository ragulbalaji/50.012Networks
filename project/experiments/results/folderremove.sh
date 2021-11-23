#!/bin/bash

for f in *; do
    if [ -d "$f" ]; then
        # f is a dir
        echo "$f"
        sudo rm -rf "$f"
    fi
done