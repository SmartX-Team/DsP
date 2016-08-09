from os import path as path
import os
import infoelems
import yaml
import logging


class InventoryManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(InventoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

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
            self._logger.error("Setting file IOError")
            self._logger.error('Is it in %s?', swpath)
            exit(-1)

        # YAML file load successful
        # Find setting for swtype in yaml configuration file
        if not swtype:
            sw_config = list()
            sw_config.append((yaml.load_all(sw_setting)).next())
            swtype = sw_config[0]['swtype']
        else:
            sw_config = [i for i in yaml.load_all(sw_setting)
                         if i['swtype'] == swtype]

        if len(sw_config) == 1:
            self._logger.info('Found: Setting for %s: %s', swname, swtype)
            sw.name = swname
            sw.type = swtype
            # sw.path = os.path.join(swpath, sw_config[0]['execfile'])
            sw.path = sw_config[0]['execfile']
            for par in sw_config[0]['parameter']:
                sw.params[par] = sw_config[0]['parameter'][par]
        elif len(sw_config) == 0:  # No setting for swtype
            self._logger.error('Not Found: Setting for %s:%s', swname, swtype)
            exit(-1)
        else:  # multiple setting for swtype in YAML exists
            self._logger.error('Error: More than one setting exists for %s:%s',
                               swname, swtype)
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
            self._logger.error('Directory for SW %s is not exist in Installer Inventory', swname)
            exit(-1)

        if not os.path.exists(path.join(inven_dir, swname, "setting.yaml")):
            self._logger.error('Failed to find setting.yaml for SW %s', swname)
            self._logger.error('Is it in %s?', inven_dir)
            exit(-1)

        # Out of loop : All software available
        self._logger.info('Software Available')
        return True
