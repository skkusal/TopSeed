import os, argparse
from multiprocessing import Process

script_dir = os.path.abspath(os.getcwd()) 
pgm_url = {
    'gawk-5.1.0' : 'https://ftp.gnu.org/gnu/gawk/gawk-5.1.0.tar.gz',
    'grep-3.6' : 'https://ftp.gnu.org/gnu/grep/grep-3.6.tar.gz', 
    'diffutils-3.7' : 'https://ftp.gnu.org/gnu/diffutils/diffutils-3.7.tar.xz',
    'patch-2.7.6' : 'https://ftp.gnu.org/gnu/patch/patch-2.7.6.tar.gz',
    'coreutils-8.31' : 'https://ftp.gnu.org/gnu/coreutils/coreutils-8.31.tar.xz',
    'trueprint-5.4' : 'https://ftp.gnu.org/gnu/trueprint/trueprint-5.4.tar.gz',
    'combine-0.4.0' : 'https://ftp.gnu.org/gnu/combine/combine-0.4.0.tar.gz',
}

pgm_dir = {
    'gawk-5.1.0' : '',  
    'grep-3.6' : 'src',
    'diffutils-3.7' : 'src',
    'patch-2.7.6' : 'src',
    'coreutils-8.31' : 'src',
    'trueprint-5.4' : 'src',
    'combine-0.4.0' : 'src',
}

def download(pgm):
    cmd = pgm_url[pgm]
    os.system("wget " + cmd)

    if "tar.xz" in pgm_url[pgm]:
        tar_cmd = "tar -xf " + pgm + ".tar.xz"
    elif "tar.gz" in pgm_url[pgm]:
        if "sqlite" in pgm:
            tar_cmd = "tar -zvxf " + pgm_url[pgm].split("/")[-1]
        else:
            tar_cmd = "tar -zxvf " + pgm + ".tar.gz"

    os.system(tar_cmd)

def build_llvm(pgm, dirs):
    os.chdir(script_dir + "/" + pgm)

    dir_name = "obj-llvm"
    
    os.mkdir(dir_name)
    os.chdir(script_dir + "/" + pgm + "/" + dir_name)

    cmd1 = "CC=wllvm CFLAGS=\"-g -O1 -Xclang -disable-llvm-passes -D__NO_STRING_INLINES -D_FORTIFY_SOURCE=0 -U__OPTIMIZE__\" ../configure --disable-nls --disable-largefile --disable-job-server --disable-load"

    os.system(cmd1)
    os.system("make")
    os.system("extract-bc make")
    
    if dirs != "":
        os.chdir(dirs)
    
    cmd2 = "find . -executable -type f | xargs -I \'{}\' extract-bc \'{}\'" 
    os.system(cmd2)
 
def build_gcov(pgm, dirs):
    os.chdir(script_dir + "/" + pgm)

    dir_name = "obj-gcov"
    
    os.mkdir(dir_name)
    os.chdir(script_dir + "/" + pgm + "/" + dir_name)
    os.system("CFLAGS=\"-g -fprofile-arcs -ftest-coverage -g -O0\" ../configure --disable-nls --disable-largefile --disable-job-server --disable-load")
    os.system("make")
    os.chdir(script_dir + "/"+pgm)

def build_all():
    procs = []

    #download
    for pgm in pgm_url:
        download(pgm)

        #build
        procs = []

        proc = Process(target=build_llvm, args=(pgm, pgm_dir[pgm]))
        procs.append(proc)
        proc.start()

        proc = Process(target=build_gcov, args=(pgm, pgm_dir[pgm]))
        procs.append(proc)
        proc.start()
        os.chdir(script_dir)

    for proc in procs:
        proc.join()

def build_each(pgm):
    #download
    download(pgm)

    #build
    build_llvm(pgm, pgm_dir[pgm])
    build_gcov(pgm, pgm_dir[pgm])
    os.chdir(script_dir)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", required=False, default="all")
    
    args = parser.parse_args()

    if args.benchmark == "all":
        build_all()
    else:
        build_each(args.benchmark)