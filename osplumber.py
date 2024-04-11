#!/usr/bin/python3

import os
import sys
import libs.utils
import urllib.request
import zipfile
import shutil
import pprint

global location
location = __file__[:-14]

global path
path = sys.argv[2]

global conf
conf = []

def arrange_modules(manifests: dict, arranged_modules: list):
    
    rem_m = list()

    if len(manifests) == 0:
        return arrange_modules
    
    elif len(arranged_modules) == 0:
        for k in manifests:
            if len(manifests[k]["after"]) == 0:
                arranged_modules.append(str(k))
                rem_m.append(k)

    else:
        for k in manifests:
            for a in arranged_modules:
                for m in manifests[k]["after"]:
                    if a == m:
                        arranged_modules.append(str(k)) #Only single
                        rem_m.append(k)
    
    for k in rem_m:
        manifests.pop(k)
    arrange_modules(manifests, arranged_modules)

#

def main():
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

    if sys.argv[1] == "update":
        update()
    elif sys.argv[1] == "init":
        init()
    elif sys.argv[1] == "mkpipeline":
        make_pipeline()
    elif sys.argv[1] == "create":
        create()
    elif sys.argv[1] == "add":
        add()
    else:
        help()


def update():
    print("Downloading Modules")
    shutil.rmtree(location + "/modules/")
    urllib.request.urlretrieve("https://github.com/Badekappe69/osplumber_modules/archive/refs/heads/main.zip", "modules.zip")
    with zipfile.ZipFile("modules.zip", 'r') as zip_ref:
        zip_ref.extractall(location)
    shutil.copytree( location + "/osplumber_modules-main/", location + "modules")
    shutil.rmtree( location + "/osplumber_modules-main/")
    os.remove("modules.zip")
    libs.utils.exec_bash("chmod -R 777 " + location + "modules")
    print("Done.")


def init():
    print("Creating pipeline template")
    os.mkdir(path)
    pipeline_template = open(path + "/modules.py", "w")
    pipeline_template.writelines("# Add modules from the modules folder.\n")
    pipeline_template.writelines("# Seperate with a comma. Order does not matter.\n")
    pipeline_template.writelines("# Then execute make_pipeline. Example:\n")
    pipeline_template.writelines("#  'generic/module_one',\n")
    pipeline_template.writelines("#  'arch/module_two'\n")
    pipeline_template.writelines("[\n")
    pipeline_template.writelines("]\n")
    pipeline_template.close()
    libs.utils.exec_bash("chmod -R 777 " + path)
    print("Done")


def make_pipeline():
    print("Creating options")
    modules_list = open(path + "/modules.py", "r")
    tmp=""
    for l in modules_list.readlines():
        if not l.startswith('#'):
            tmp=tmp+l

    local = dict()
    exec("k = " + str(tmp), dict(), local)
    modules = local["k"]
    modules_list.close()

    manifests = dict()
    for i in modules:
        print(i)
        tmp_dict = open(location + "modules/" + str(i) + "/manifest.py")
        local = dict()
        exec("k = " + str(tmp_dict.read()), dict(), local)
        manifests[str(i)] = local["k"]
        tmp_dict.close()

    arranged_modules = list()
    arrange_modules(manifests, arranged_modules)

    config = open(path + "/configuration.py", "w")
    config.writelines("[\n")

    for c in arranged_modules:
        tmp_dict = open(location + "modules/" + str(c) + "/conf.py")
        if not arranged_modules[len(arranged_modules)-1] == c:
            config.write(tmp_dict.read() + ",")
        else:
            config.write(tmp_dict.read())

    config.writelines("]\n")
    config.close()

    libs.utils.exec_bash("chmod -R 777 " + path + "/configuration.py")

    print("Done")


def create():
    print("Create OS")
    conf_dict = open(path + "/configuration.py", "r")
    local = dict()
    exec("k = " + str(conf_dict.read()), dict(), local)
    conf = local["k"]
    conf_dict.close()
    
    modules = []
    for i in conf:
        for j in i:
            modules.append(j)
    
    manifests = []
    for m in modules:
        tmp_dict = open(location + "modules/" + str(m) + "/manifest.py")
        local = dict()
        exec("k = " + str(tmp_dict.read()), dict(), local)
        manifests.append(local["k"])
        tmp_dict.close()


    for m in manifests:
        for dir in m["folders"]:
            if not os.path.isdir(path + "/" + dir):
                os.mkdir(path + "/" + dir)
                libs.utils.exec_bash("chmod -R 777 " + path + "/" + dir)


    i = 0
    for m in modules:
        print("Starting module: " + m)
        tmp_code = open(location + "modules/" + str(m) + "/mod.py", "r")
        insert = dict()
        insert["conf"] = conf[i][m]
        exec(tmp_code.read(), insert, dict())
        i=i+1
        print("Finished module: " + m)
    
    print("Done")


def add():
    pass


def help():
    pass


if __name__ == "__main__":
    main()
