from os import path as path
import os
import infoelems
import yaml


class InventoryManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(InventoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def prepare(self, swname, swtype):
        """
        prepare (swname, swtype):
           input value : str(software_name) str(software_type)
           return : SwInfo() with params
        """
        installer_path = os.getcwd()
        swpath = path.join(installer_path, 'inven', swname)
        sw = infoelems.SwInfo()

        try:
            f = open(swpath + '/setting.yaml', "r")
            sw_setting = f.read()
        except IOError:
            print "Setting file IOError" \
                  "\nIs it in %s?" % swpath
            exit(-1)

        # YAML file load successful
        # Find setting for swtype in yaml configuration file
        if not swtype:
            swtype = 'Default'
        sw_config = [i for i in yaml.load_all(sw_setting) if i['swtype'] == swtype]

        if len(sw_config) == 1:
            print "Found : setting for %s:%s" % (swname, swtype)
            sw.name = swname
            sw.type = swtype
            for par in sw_config[0]['Parameter']:
                sw.params[par] = sw_config[0]['Parameter'][par]
        elif len(sw_config) == 0:  # No setting for swtype
            print "Not Found : setting for %s:%s" % (swname, swtype)
            exit(-1)
        else:  # multiple setting for swtype in YAML exists
            print "Error : More than one setting exists for %s:%s" % (swname, swtype)
            exit(-1)

        return sw

    def verify(self, swname):
        """
        verify(swname)
           input value : str(software_name)
           return : None
        """
        installer_path = os.getcwd()
        inven_dir = path.join(installer_path, 'inven')

        (_, dirnames, _) = next(os.walk(inven_dir), (None, [], None))

        if swname not in dirnames:
            print "Directory for SW %s is not exist in Installer Inventory" % swname
            exit(-1)

        if not os.path.exists(path.join(inven_dir, swname, "setting.yaml")):
            print "Failed to find setting.yaml for SW %s" % swname
            print "Is it in %s?" % inven_dir
            exit(-1)

        # Out of loop : All software available
        print "Software available"
        return True
