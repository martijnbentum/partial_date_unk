import datetime

'''
-goal: a custom Django field that accepts input with different levels of date specificity, ranging from a specific day to a millennium
creating a custom field keeps data entry and database structure simple compared to using multiple fields

-Solution
Create a date mapper class (a custom django field is based on a python class)
This class maps a string input to a datetime instance. Following the partial-date repository we can use the seconds to store the specificity of the date.
'''

format_help = '''
The input string has the following format:

day	 		1999-12-04			Y-M-D
month		1999-12				Y-M
year 		1999y				<integer>y
decade		200d				<integer>d 		1990-2000
century 	20c					<integer>c		1900-2000
millenium 	2m					<integer>m		1000-2000
'''

class Partial_date:
	def __init__(self,s = None, t = None):
		self.s = s
		self.format_help = format_help
		self.format_error = ValueError('input string does not conform to format ' + str(self.s) + '\n' + self.format_help)
		self.type_dict = {'y':'year','d':'decade','c':'century','m':'millenium','ym':'year_month','ymd':'year_month_day'}
		self.type2number_dict = {'year':0,'decade':1,'century':2,'millenium':3,'year_month':4,'year_month_day':5}
		self.number2type_dict = reverse_dict(self.type2number_dict)
		self.type2multiplier = {'decade':10,'century':100,'millenium':1000}
		if s == None and t == None: raise ValueError('please provide string or datetime object')
		if s:
			self.determine_type()
			self._set_datetime()
		else: self.set_datetime_form_database(t)

	def __str__(self):
		return self.s + ' ' + self.type

	def __repr__(self):
		return str(self.start_dt) + ' ' + str(self.end_dt)

	def determine_type(self):
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
		if self.type in 'decade,century,millenium'.split(','):
			self.end_year = self.number * self.type2multiplier[self.type]
			self.year = self.end_year - self.type2multiplier[self.type]
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
		self.dt = dt
		self.start_dt = self.dt
		self._datetime2str()
		self._set_datetime()


	def _datetime2str(self):
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
		if self.type in 'decade,century,millenium'.split(','):
			print(make_count_string(self.number),self.type)
			return make_count_string(self.number) + ' ' + self.type
		if self.type == 'year': s='%Y'
		if self.type == 'year_month': s='%Y-%m'
		if self.type == 'year_month_day': s='%Y-%m-%d'
		return self.dt.strftime(s)

	@property
	def name(self):
		return self.pretty_string()

		

	
def make_count_string(n):
	if n == 0 or int(str(n)[-1]) > 3: return str(n)+'th'
	if str(n)[-1] == '1': return str(n)+'st'
	if str(n)[-1] == '2': return str(n)+'nd'
	if str(n)[-1] == '3': return str(n)+'rd'
	raise ValueError('could not parse',n)
		
			

			
	
		
		
	
	
			
def reverse_dict(d):
	return {v:k for k, v in d.items()}
				
