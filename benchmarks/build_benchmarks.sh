#!/bin/bash

benchmark=$1

if [ -z $benchmark ]; then   
    python3 build_others.py --benchmark=all
    bash build_sqlite.sh
else
    case $1 in
    "sqlite-3.33.0") bash build_sqlite.sh;;
    "gawk-5.1.0")  python3 build_others.py --benchmark=$benchmark;;
    "grep-3.6")  python3 build_others.py --benchmark=$benchmark;;
    "patch-2.7.6")  python3 build_others.py --benchmark=$benchmark;;
    "diffutils-3.7")  python3 build_others.py --benchmark=$benchmark;;
    "coreutils-8.31") python3 build_others.py --benchmark=$benchmark;;
    "trueprint-5.4")  python3 build_others.py --benchmark=$benchmark;;
    "combine-0.4.0")  python3 build_others.py --benchmark=$benchmark;;
    *) echo "Not Found benchmark: $1";;
    esac
fi