#!/bin/bash

bmks="
sqlite-3.33.0
gawk-5.1.0
grep-3.6
diffutils-3.7
patch-2.7.6
trueprint-5.4
combine-0.4.0
coreutils-8.31
"

bmks_url=(
'https://www.sqlite.org/2020/sqlite-amalgamation-3330000.zip'
'https://ftp.gnu.org/gnu/gawk/gawk-5.1.0.tar.gz' 
'https://ftp.gnu.org/gnu/grep/grep-3.6.tar.gz'
'https://ftp.gnu.org/gnu/diffutils/diffutils-3.7.tar.xz'
'https://ftp.gnu.org/gnu/patch/patch-2.7.6.tar.gz'
'https://ftp.gnu.org/gnu/trueprint/trueprint-5.4.tar.gz'
'https://ftp.gnu.org/gnu/combine/combine-0.4.0.tar.gz'
'https://ftp.gnu.org/gnu/coreutils/coreutils-8.31.tar.xz'
)

bmks_dir=(
'src'
''
'src'
'src'
'src'
'src'
'src'
'src'
)

build_sqlite() {
    base=$PWD
    benchmark=$1
    url=$2
    dir=$3

    mkdir $benchmark
    cd $benchmark
    wget $url
    unzip sqlite-amalgamation-3330000.zip

    cp -r sqlite-amalgamation-3330000 obj-llvm
    cd obj-llvm
    wllvm -g -O1 -Xclang -disable-llvm-passes -D__NO_STRING_INLINES -D_FORTIFY_SOURCE=0 -U__OPTIMIZE__ -DSQLITE_THREADSAFE=0 -DSQLITE_OMIT_LOAD_EXTENSION -DSQLITE_DEFAULT_MEMSTATUS=0 -DSQLITE_MAX_EXPR_DEPTH=0 -DSQLITE_OMIT_DECLTYPE -DSQLITE_OMIT_DEPRECATED -DSQLITE_DEFAULT_PAGE_SIZE=512 -DSQLITE_DEFAULT_CACHE_SIZE=10 -DSQLITE_DISABLE_INTRINSIC -DSQLITE_DISABLE_LFS -DYYSTACKDEPTH=20 -DSQLITE_OMIT_LOOKASIDE -DSQLITE_OMIT_WAL -DSQLITE_OMIT_PROGRESS_CALLBACK -DSQLITE_DEFAULT_LOOKASIDE='64,5' -DSQLITE_OMIT_PROGRESS_CALLBACK -DSQLITE_OMIT_SHARED_CACHE -I. shell.c sqlite3.c -o sqlite3
    find . -executable -type f | xargs -I '{}' extract-bc '{}'
    cd ..

    cp -r sqlite-amalgamation-3330000 obj-gcov
    cd obj-gcov
    gcc -g -fprofile-arcs -ftest-coverage -O0 -DSQLITE_THREADSAFE=0 -DSQLITE_OMIT_LOAD_EXTENSION -DSQLITE_DEFAULT_MEMSTATUS=0 -DSQLITE_MAX_EXPR_DEPTH=0 -DSQLITE_OMIT_DECLTYPE -DSQLITE_OMIT_DEPRECATED -DSQLITE_DEFAULT_PAGE_SIZE=512 -DSQLITE_DEFAULT_CACHE_SIZE=10 -DSQLITE_DISABLE_INTRINSIC -DSQLITE_DISABLE_LFS -DYYSTACKDEPTH=20 -DSQLITE_OMIT_LOOKASIDE -DSQLITE_OMIT_WAL -DSQLITE_OMIT_PROGRESS_CALLBACK -DSQLITE_DEFAULT_LOOKASIDE='64,5' -DSQLITE_OMIT_PROGRESS_CALLBACK -DSQLITE_OMIT_SHARED_CACHE -I. shell.c sqlite3.c -o sqlite3
    cd $base
}

build_others() {
    base=$PWD
    benchmark=$1
    url=$2
    dir=$3

    wget $url
    
    if [[ "$url" =~ tar.xz ]]; then
        tar -xf "${benchmark}.tar.xz"
        rm -rf "${benchmark}.tar.xz"
    else
        tar -zxvf "${benchmark}.tar.gz"
        rm -rf "${benchmark}.tar.gz"
    fi


    mkdir $benchmark/obj-llvm
    cd $benchmark/obj-llvm

    LLVM_COMPILER=clang CC=wllvm ../configure --disable-nls CFLAGS="-g -O1 -Xclang -disable-llvm-passes -D__NO_STRING_INLINES  -D_FORTIFY_SOURCE=0 -U__OPTIMIZE__" && \
    LLVM_COMPILER=clang make

    if [ ! "$benchmark" = "gawk-5.1.0" ]; then
        cd $dir
    fi
    find . -executable -type f | xargs -I '{}' extract-bc '{}'
    if [ ! "$benchmark" = "gawk-5.1.0" ];  then
        cd ..
    fi
    cd ..

    mkdir obj-gcov
    cd obj-gcov
    CFLAGS="-g -fprofile-arcs -ftest-coverage -g -O0" ../configure --disable-nls --disable-largefile --disable-job-server --disable-load
    make
    cd $base
}

build_each() {
    benchmark=$1
    url=$2
    dir=$3
    if [ $benchmark = 'sqlite-3.33.0' ]; then
        build_sqlite $benchmark $url $dir
    else
        build_others $benchmark $url $dir
    fi
}

build_all() {
    m=0
    for each in $bmks; do
        url=${bmks_url[m]}
        dir=${bmks_dir[m]}
        echo $each $url $dir
        build_each $each $url $dir
        m=$(($m+1))
    done
}

benchmark=$1

if [ -z $benchmark ]; then
    build_all
else
    m=0
    for each in $bmks; do
        url=${bmks_url[m]}
        dir=${bmks_dir[m]}
        if [ $each = $benchmark ]; then
            build_each $each $url $dir
            break
        fi 
        m=$(($m+1))
    done
fi
