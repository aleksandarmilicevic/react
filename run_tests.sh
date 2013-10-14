#!/bin/bash

for f in `find src/react/tests -name "test*py"`
do 
    python $f
done
