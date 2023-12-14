import os

from setuptools import find_packages, setup

with open("requirements.txt") as f: 
	requirements = f.readlines() 

data_path = "fdg/data/"
data_files = [os.path.join(data_path, file) for file in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, file))]

long_description = "Small python utility to generate dummy data in database tables" 

setup( 
	name ="fake-db-generator", 
	version ="1.0.0", 
	author ="Devendra Pratap", 
	author_email ="dps.manit@gmail.com", 
	url ="https://github.com/devendrapratap02/fake-db-generator", 
	description ="Fake DB Generator", 
	long_description = long_description, 
	long_description_content_type ="text/markdown", 
	license = "MIT", 
	packages = find_packages(), 
	entry_points = { 
		"console_scripts": [ 
			"fdg = fdg.runner:main"
		] 
	}, 
	classifiers = [
		"Programming Language :: Python :: 3", 
		"License :: OSI Approved :: MIT License", 
		"Operating System :: OS Independent", 
	], 
	data_files = data_files,
	include_package_data = True,
	keywords ="faker dummy db database generate generator dps", 
	install_requires = requirements, 
	zip_safe = False
) 
