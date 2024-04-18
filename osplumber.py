#!/usr/bin/python3

import os
import sys
import libs.executor
import libs.executor.executor
import libs.utils
import urllib.request
import zipfile
import shutil
import time
import json
import pprint

global location
location = __file__[:int(__file__.rfind("/")+1)]

global path
if len(sys.argv) > 2:
    path = sys.argv[2]

global conf
conf = []

#sys.tracebacklimit = 0


def configuration_list():
    try:
        tmp_dict = open(path + "/configuration.py", "r")
        try:
                local = dict()
                tmp = tmp_dict.read()
                tmp = tmp.replace("\n", "")
                tmp = tmp.replace("\t", "")
                exec("k = " + str(tmp), dict(), local)
                configuration = local["k"]
        except:
                print("Could not parse configuration.py.\n")
                exit(0)
    except:
        print("Could not read configuration.py.")
    finally:
        tmp_dict.close()
    return configuration


def arrange_modules(manifests: dict, arranged_modules: list):
    
    rem_m = list()

    if len(manifests) == 0:
        return arranged_modules
    
    elif len(arranged_modules) == 0:
        for k in manifests:
            if len(manifests[k]["after"]) == 0:
                arranged_modules.append(str(k))
                rem_m.append(k)

    else:
        for k in manifests:
            for a in arranged_modules:
                for m in manifests[k]["after"]:
                    #print(k["name"])
                    if a == m:
                        #print(k["name"])
                        arranged_modules.append(str(k)) #Only single
                        rem_m.append(k)
    
    for k in rem_m:
        manifests.pop(k)
    arrange_modules(manifests, arranged_modules)

def arranged_modules_list():
    try:
        modules_list = open(path + "/modules.py", "r")
    except:
        print("Coud not read modules.py.")
    else:
        tmp=""
        for l in modules_list.readlines():
            if not l.startswith('#'):
                tmp=tmp+l
        tmp = tmp.replace("\t", "")
        tmp = tmp.replace("\n", "")
    finally:
        modules_list.close()
    
    locals = dict()
    try:
        exec("k = " + str(tmp), dict(), locals)
    except:
        print("Could not parse modules.py.")

    modules = locals["k"]

    manifests = dict()
    for module in modules:
        print(module)
        try:
            tmp_dict = open(location + "/modules/" + str(module)  + "/manifest.py")
            local = dict()
            exec("k = " + str(tmp_dict.read()), dict(), local)
            manifests[str(module)] = local["k"]
        except:
            print("Could not parse manifest.py.\n" + 
            "Path: " + location + "modules/" + str(module)  + "/manifest.py\n" +
            "Is either marlformed or unreadable.")
        finally:
            tmp_dict.close()

    arranged_modules = list()
    arrange_modules(manifests, arranged_modules) # Change Algo
    return arranged_modules

#

def main():
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\n" + 
             "Please try again, this time using 'sudo'. Exiting.")

    if sys.argv[1] == "update":
        update()
    elif sys.argv[1] == "init":
        init()
    elif sys.argv[1] == "mkpipeline":
        make_pipeline()
    elif sys.argv[1] == "create":
        create()
    elif sys.argv[1] == "sync":
        sync()
    else:
        help()


def update():
    print("Downloading Modules")
    if os.path.isdir(location + "modules"):
        shutil.rmtree(location + "modules")
    
    try:
        repo_handler = open(location + "repos.txt", "r")
        os.mkdir(location + "download")
        os.mkdir(location + "zip")
    except:
        print("Could not read from repos.txt")
    else:
        for repo in repo_handler.readlines():
            try:
                name = str(time.time().as_integer_ratio()[0])
                urllib.request.urlretrieve(repo, location + "download/" + name + ".zip")
                print("Downloaded repo(URL): " + repo[:-1])
            except:
                print("Could not download modules.\n" + 
                    "Check internet connection or URL.")
                exit(1)
            else:
                with zipfile.ZipFile(location + "download/" + name + ".zip", 'r') as zip_file:
                    zip_file.extractall(location + "zip/")
                    
                for dir in os.listdir(location + "zip/"):
                    shutil.copytree( location + "zip/" + dir + "/", location + "modules/")
    finally:
        libs.utils.exec_bash("chmod -R 777 " + location + "modules")
        shutil.rmtree(location + "download/")
        shutil.rmtree(location + "zip/")
        repo_handler.close()

        print("Done.")


def init():
    print("Creating pipeline template.")
    os.mkdir(path)
    try:
        pipeline_template = open(path + "/modules.py", "w")
        pipeline_template.writelines("# Add modules from the modules folder.\n")
        pipeline_template.writelines("# Seperate with a comma. Order does not matter.\n")
        pipeline_template.writelines("# Then execute mkpipeline. Example:\n")
        pipeline_template.writelines("#  'generic/module_one',\n")
        pipeline_template.writelines("#  'arch/module_two'\n")
        pipeline_template.writelines("[\n")
        pipeline_template.writelines("]\n")
    except:
        print("Could not write template to storage.")
        exit(1)
    else:
        libs.utils.exec_bash("chmod -R 777 " + path)
        print("Done")
    finally:
        pipeline_template.close()


def make_pipeline():
    print("Creating options")

    arranged_modules = arranged_modules_list()


    try:
        config = open(path + "/configuration.py", "w")
    except:
        print("Could not read configuration.py.")
    else:
        config.writelines("[\n")
        for module in arranged_modules:
            try:
                tmp_dict = open(location + "modules/" + str(module) + "/conf.py")
            except:
                print("Could not parse configuration.py: \n" + 
                location + "modules/" + str(module) + "conf.py\n" +
                "It is not a dict or  missing.")
            if not arranged_modules[len(arranged_modules)-1] == module:
                config.write(tmp_dict.read() + ",")
            else:
                config.write(tmp_dict.read())
        config.writelines("\n]\n")
    finally:
        config.close()
    
    libs.utils.exec_bash("chmod -R 777 " + path + "/configuration.py")
    print("Done")


def create():
    print("Create OS")
    configuration = configuration_list()
    manifests = []
    for module_name in configuration:
        try:
            tmp_dict = open(location + "modules/" + str(list(module_name)[0]) + "/manifest.py")
            local = dict()
            try:
                exec("k = " + str(tmp_dict.read()), dict(), local)
                manifests.append(local["k"])
            except:
                print("Could not parse manifest.\n" + 
                    "Path: " + location + "modules/" + str(list(module_name)[0]) + "/manifest.py" +
                    "It is not a dict.")
        except:
            print("Could not read manifest.py")
        finally:
            tmp_dict.close()


    for manifest in manifests:
        for dir in manifest["folders"]:
            if not os.path.isdir(path + "/" + dir):
                os.mkdir(path + "/" + dir)
                libs.utils.exec_bash("chmod -R 777 " + path + "/" + dir)
    
    libs.executor.executor.execute(configuration, manifests)
    
    print("Done")


def sync():

    new_modules = arranged_modules_list()
    old_configuration = configuration_list()

    old_modules = list()
    for d in old_configuration:
        old_modules.append(list(d)[0])
    
    for m in new_modules:
        

    try:
        new_conf = open( path + "/configuration.py", "w")
    except:
        print("Could not write configuration.py.")
    else:
        new_conf.write("[\n")
        for d in configuration:
            j = json.dumps(d, indent=10)
            new_conf.write(j)
            if configuration[len(configuration)-1] != d:
                new_conf.write(",\n")
        new_conf.write("\n]")
    finally:
        new_conf.close()

    libs.utils.exec_bash("chmod -R 777 " + path + "/configuration.py")


def help():
    pass


if __name__ == "__main__":
    main()
