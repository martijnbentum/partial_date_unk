import datetime
from django.db import models

'''
-goal: a custom Django field that accepts input with different levels of date specificity, ranging from a specific day to a millennium
creating a custom field keeps data entry and database structure simple compared to using multiple fields

-Solution
Create a date mapper class (a custom django field is based on a python class)
This class maps a string input to a datetime instance. Following the partial-date repository we can use the seconds to store the specificity of the date.
'''

format_help = '''
The input string has the following format:
			(format)
day         1999-12-04    Y-M-D
month       1999-12       Y-M
year        1999y         <integer>y
decade      200d          <integer>d     1990-2000
century     20c           <integer>c     1900-2000
millenium   2m            <integer>m     1000-2000

For december fourth 1999 you type: 1999-12-04
'''

class PartialDate:
	'''A class to map between a string and datetime object for a custom django field that can store partial dates.'''
	def __init__(self,s = None, t = None):
		'''Object that map between string and datetime object.
		s 		specially formated string (see format_help) that specifies a date
		t 		datetime object with precission stored in the microseconds
		'''
		
		self.s = s
		self.format_help = format_help
		self.format_error = ValueError('input string does not conform to format ' 
			+ str(self.s) + '\n' + self.format_help)
		self.type_dict = {'y':'year','d':'decade','c':'century','m':'millenium',
			'ym':'year_month','ymd':'year_month_day'}
		self.type2number_dict = {'year':0,'decade':1,'century':2,'millenium':3,
			'year_month':4,'year_month_day':5}
		self.number2type_dict = reverse_dict(self.type2number_dict)
		self.type2multiplier = {'decade':10,'century':100,'millenium':1000}
		if s == None and t == None: raise ValueError('please provide string or datetime object')
		if s:
			self.determine_type()
			self._set_datetime()
		else: self.set_datetime_form_database(t)

	def __str__(self):
		return self.pretty_string()

	def __repr__(self):
		return str(self.start_dt) + ' ' + str(self.end_dt)

	def __lt__(self,other):
		if type(other) == float: return self.dt < datetime.datetime.fromtimestamp(other)
		elif type(other) == datetime.datetime: return self.dt < other
		elif not type(self) == type(other):
			raise ValueError('cannot compare with ' + str(type(other)) + ' ' + other)
		return self.dt < other.dt

	def __contains__(self,other):
		'''checks whether the other time is within the self time.'''
		if type(other) == float: 
			start_dt = datetime.datetime.fromtimestamp(other)
			end_dt = start_dt
		elif type(self) == type(other): start_dt, end_dt = other.start_dt,other.end_dt
		elif type(other) == datetime.datetime: start_dt, end_dt = dt, dt
		else: raise ValueError('cannot compare with ' + str(type(other)) + ' ' + other)
		return self.start_dt <= start_dt and self.end_dt >= end_dt
		

	def determine_type(self):
		'''based on the string format the level of date specificity is determined.'''
		self.year, self.month, self.day = 1,1,1
		if self.s == '': raise self.format_error
		if self.s[-1] in self.type_dict.keys():
			try: setattr(self,self.type_dict[self.s[-1]],int(self.s[:-1]))
			except: raise self.format_error
			else: 
				self.type = self.type_dict[self.s[-1]]
				self.number = int(self.s[:-1])
		elif self.s.count('-') == 1:
			try: self.year, self.month = reduce(int,self.s.split('-'))
			except: raise self.format_error
			else:self.type = 'year_month'
		elif self.s.count('-') == 2:
			try: self.year, self.month,self.day = reduce(int,self.s.split('-'))
			except: raise self.format_error
			else:self.type = 'year_month_day'
		else: raise self.format_error


	def _set_datetime(self):
		'''create the datetime object. dt, start_dt end_dt (dt == start_dt)
		start / end dt refer to the start /end point of a date, 
		for example 2nd century (2c) start_date = 100-01-01, end_date = 0199-12-31
		the start date is stored in the database
		'''
		if self.type in 'decade,century,millenium'.split(','):
			self.end_year = self.number * self.type2multiplier[self.type] - 1
			self.year = self.end_year + 1 - self.type2multiplier[self.type]
			if self.year == 0: self.year =1
			self.dt = datetime.datetime(year=self.year,month=1,day=1,microsecond = self.type2number_dict[self.type])
			self.start_dt = self.dt
			self.end_dt = datetime.datetime(year=self.end_year,month=12,day=31,microsecond = self.type2number_dict[self.type])
		else:
			self.dt = datetime.datetime(year=self.year,month=self.month,day=self.day,microsecond = self.type2number_dict[self.type])
			self.start_dt = self.dt
			if self.type == 'year': self.month, self.day =12,31
			if self.type == 'year_month': self.day = 31
			self.end_dt = datetime.datetime(year=self.year,month=self.month,day=self.day,
				microsecond=self.type2number_dict[self.type])

	def set_datetime_form_database(self, dt):
		'''Create a partial date object from a datetime object (microseconds indicate the precission).'''
		self.dt = dt
		self.start_dt = self.dt
		self._datetime2str()
		self._set_datetime()


	def _datetime2str(self):
		'''Create the string representation based on datetime object.'''
		self.type = self.number2type_dict[self.dt.microsecond]
		self.year = self.dt.year
		self.month = self.dt.month
		self.day = self.dt.day
		if self.type in 'decade,century,millenium'.split(','):
			n = self.type2multiplier[self.type]
			self.number = int((self.year+n)/n)
			self.s = str(self.number) + reverse_dict(self.type_dict)[self.type]
		elif self.type == 'year_month': self.s = self.dt.strftime('%Y-%m') 
		elif self.type == 'year_month_day': self.s = self.dt.strftime('%Y-%m-%d') 
		else: raise ValueError('do not recognize type:',self.type)

	def pretty_string(self):
		'''Create nice format for the date (e.g. 2nd century).'''
		if self.type in 'decade,century,millenium'.split(','):
			return make_count_string(self.number) + ' ' + self.type
		if self.type == 'year': s='%Y'
		if self.type == 'year_month': s='%Y-%m'
		if self.type == 'year_month_day': s='%Y-%m-%d'
		return self.dt.strftime(s)

	@property
	def name(self):
		return self.s 

	@property
	def help(self):
		print(self.format_help)


class PartialDateField(models.Field):
	'''Custom django field to store date information with different levels of specificity.'''
	def get_internal_type(self):
		return "DateTimeField"

	def from_db_value(self, value, expression, connection, context = None):
		if value is None: return value
		if isinstance(value, PartialDate): return value
		return PartialDate(t = value)

	def to_python(self, value):
		if value is None: return value
		if isinstance(value, PartialDate): return value
		if isinstance(value, str): return PartialDate(value)
		raise expressions.ValidationError('could not parse: '+value)

	def get_prep_value(self,value):
		if value is None or value == '': return None
		partial_date = self.to_python(value)
		return partial_date.dt

	
def make_count_string(n):
	'''Create the correct abbreviation for a date (2nd or 4th) for 2nd or 4th century).'''
	if n == 0 or int(str(n)[-1]) > 3: return str(n)+'th'
	if str(n)[-1] == '1': return str(n)+'st'
	if str(n)[-1] == '2': return str(n)+'nd'
	if str(n)[-1] == '3': return str(n)+'rd'
	raise ValueError('could not parse',n)
		
	
			
def reverse_dict(d):
	'''Swap keys and values does not check whether original values are unique.'''
	return {v:k for k, v in d.items()}
				
