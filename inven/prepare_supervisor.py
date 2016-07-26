from os import path as path
import os
import infoelems
import yaml




"""
prepare (swname, swtype):
   input value : str(software_name) str(software_type)
   return : SwInfo() with params
"""
def prepare(swname, swtype):

   sw = infoelems.SwInfo()
   sw.name = swname
   sw.type = swtype
   installer_path = os.getcwd()
   swpath = path.join(installer_path,'inven', swname)
   
   try:
      f = open(swpath + '/setting.yaml',"r")
      sw_setting = f.read()
   
   except IOError:
      print "Setting file IOError"\
            "\nIs it in %s?"%swpath
      exit(-1)
   #YAML file load successful
   #Find setting for swtype in yaml configuration file
   default_config = [i for i in yaml.load_all(sw_setting) if i['swtype']=='Default']
   sw_config = [i for i in yaml.load_all(sw_setting) if i['swtype']==swtype]
   if len(sw_config) == 1: #one unique setting for swtype in YAML exists
      print "Found : setting for %s:%s"%(swname,swtype)
      for par in default_config[0]['Parameter']:
         sw.params[par] = default_config[0]['Parameter'][par]
      for par in sw_config[0]['Parameter']:
         sw.params[par] = sw_config[0]['Parameter'][par]
#           print sw.getparams()
 
   elif len(config) == 0: #No setting for swtype
      print "Not Found : setting for %s:%s"%(swname, swtype)
      exit(-1)
   else: #multiple setting for swtype in YAML exists
      print "Error : More than one setting exists for %s:%s"%(swname, swtype) 
      exit(-1)
   return sw
    
   
"""
verify(swname)
   input value : str(software_name)
   return : None
"""
def verify(swname):
   installer_path = os.getcwd()
   inven_dir   = path.join(installer_path,'inven')
   try:
      f = open(inven_dir + "/AVAILABLE_SOFTWARE",'r')
   except IOError:
      print "Failed to open AVAILABLE_SOFTWARE "\
            "\nIs it in %s?"%inven_dir 
      exit(-1)

   sw_list = f.read().splitlines()
   if type(swname) is str:
      if swname not in sw_list:
         print "Software %s is not available"%swname
         exit(-1)
   else:
      print "%s in wrong data type - String required"%boxlist
      print type(boxlist)
      exit(-1)
   
   # Out of loop : All software available
   print "Software available"
