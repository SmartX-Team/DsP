from os import path as path
import os
import infoelems
import yaml


"""
a = infoelems.BoxInfo()
a.setname("aa")
print a.getswinfo()

test = path.join('/home/koko','wing')
print test
print os.getcwd()
a_list = ['name1','name2']
testname = 'name1'
print testname not in a_list
print "aa""bb"
print type(a_list) is list
"""


"""
prepare (boxlist):
	input value : list(BoxInfo)
	with BoxInfo, filled with swname, swtype.
"""
def prepare(boxlist):

	installer_path = os.getcwd()
	ret_list = []
	if type(boxlist) is list:
		for box in boxlist:
			for sw in box.getswinfo():
				swname = sw.getname()
				swpath = path.join(installer_path,'inven', swname)
				swtype = sw.gettype()
	
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
						sw.setparam(par,default_config[0]['Parameter'][par])
					for par in sw_config[0]['Parameter']:
						sw.setparam(par,sw_config[0]['Parameter'][par])
	#				print sw.getparams()
	
				elif len(config) == 0: #No setting for swtype
					print "Not Found : setting for %s:%s"%(swname, swtype)
					exit(-1)
				else: #multiple setting for swtype in YAML exists
					print "Error : More than one setting exists for %s:%s"%(swname, swtype) 
					exit(-1)
		return boxlist
	elif isinstance (boxlist,infoelems.BoxInfo):
		print 'TBI - currently, only works for list(BoxInfo)'
		
	



def verify(boxlist):

	"""
	Currently, location of AVAILABLE_SOFTWARE is 
	$(current directory)/
	"""
	installer_path = os.getcwd()
	repo_dir	= path.join(installer_path,'')
	try:
		f = open(repo_dir + "/AVAILABLE_SOFTWARE",'r')
	except IOError:
		print "Failed to open AVAILABLE_SOFTWARE "\
				"\nIs it in %s?"%repo_dir	
		exit(-1)

	sw_list = f.read().splitlines()
	print "SW list : "+ ', '.join(sw_list)

	if type(boxlist) is list:
		for box in boxlist:
			for boxsw in box.getswinfo():
				if boxsw.getname() not in sw_list:
					print "Software %s is not available"%boxsw
					exit(-1)
	
	elif isinstance (boxlist,infoelems.BoxInfo):
		for boxsw in boxlist.getswinfo():
			if boxsw.getname() not in sw_list:
				print "Software %s is not available"%boxsw
				exit(-1)
	
	else:
		print "%s in wrong data type - not BoxInfo nor list"%boxlist
		print type(boxlist)
		exit(-1)
	
	# Out of loop : All software available
	print boxlist.getswinfo()[0]._param
	print "All available"
