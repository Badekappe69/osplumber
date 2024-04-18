   print("Adding new module(s).")

    modules = arranged_modules_list()
    
    configuration: list = configuration_list()

    index = 0
    for module in modules:
        conf = dict()
        try:
            tmp_dict = open(location + "modules/" + str(module) + "/conf.py")
        except:
            print("Can not read conf.py\n" + 
                "Path: " + location + "modules/" + str(module) + "/conf.py")
        finally:
            tmp = tmp_dict.read()
            tmp_dict.close()

            #tmp = tmp.replace("\t", "")
            #tmp = tmp.replace("\n", "")
            #pprint.pp(tmp)

        try:
            local = dict()
            exec("k = " + tmp, dict(), local)
            conf = local["k"]
        except:
            print("Could not parse conf.py.\n" + 
                "Path: " + location + "modules/" + str(module) + "/conf.py")

        if len(configuration) > index:
            configuration.append(conf)
        else:
            configuration.insert(index + 1, conf)

        index = index + 1