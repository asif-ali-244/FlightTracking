from setuptools import setup, find_packages

setup(
	name='FlightTracker',
	version='0.1',
	author='Asif Ali',
	py_modules=['helper','flight_cli'],
	install_requires=['Click','Requests','prettytable',],
	entry_points='''
			[console_scripts]
			FlightTracker=flight_cli:cli

	''',
	include_package_data=True,
	package_data={'':['*.json']},
	)