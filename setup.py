import setuptools

setuptools.setup(
	name='partial-date',
	version = '0.1',
	author = 'Martijn Bentum, Mojtaba Kandroodi',
	author_email = 'm.bentum@let.ru.nl',
	description = 'a custom django model field to represent dates with varying specificity',
	long_description = '',
	long_description_content_type = 'text/markdown',
	url = 'https://github.com/martijnbentum/partial_date',
	packages = setuptools.find_packages(),
	classifiers = ['Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License'],
	python_requires = '>=3.5')
	
