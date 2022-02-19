#!/usr/bin/env bash

cp ../examples/inp_file_reader.ipynb ./examples/inp_file_reader.ipynb
cp ../examples/rpt_file_reader.ipynb ./examples/rpt_file_reader.ipynb
cp ../examples/out_file_reader.ipynb ./examples/out_file_reader.ipynb
cp ../examples/inp_file_macros.ipynb ./examples/inp_file_macros.ipynb
cp ../examples/inp_file_structure.ipynb ./examples/inp_file_structure.ipynb
cp ../examples/hotstart_file_reader.ipynb ./examples/hotstart_file_reader.ipynb

cp ../README.md ./README.md
cp ../CHANGES.md ./CHANGES.md
#ln -s ../README.md ./README.md
sed -i "s/This is an API for reading, manipulating and running SWMM-Projects/Getting started/" ./README.md

make html
