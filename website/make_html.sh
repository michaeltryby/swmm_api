#!/usr/bin/env bash

cp ../examples/inp_file_reader.ipynb ./examples/inp_file_reader.ipynb
cp ../examples/rpt_file_reader.ipynb ./examples/rpt_file_reader.ipynb
cp ../examples/out_file_reader.ipynb ./examples/out_file_reader.ipynb

make html

ln -s ../README.md README.md