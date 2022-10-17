# Partial date unk

Is an import (was not allowed to fork my own repo) from partial date. Goal is to make an extension with the option to enter unknown and now option for date

Create a date mapper class for a custom django date field (a custom django field is based on a python class)
This class maps a string input to a datetime instance. Following the partial-date repository we can use the seconds to store the specificity of the date.
The input string has the following format:

day	 		    1999-12-04	Y-M-D  
month		    1999-12			Y-M  
year 		    1999y				<integer>y  
decade		  200d				<integer>d 		1990-2000  
century 		20c					<integer>c		1900-2000  
millenium 	2m					<integer>m		1000-2000  

The datetime instance can easily be stored in a database

Inspired by:
https://pypi.org/project/django-partial-date/
