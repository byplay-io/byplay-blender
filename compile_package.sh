#!/bin/bash

echo "VERSION = '$1'.split('/')[-1]" > byplay/version.py
zip -r package.zip byplay/*.py byplay/**/*.py