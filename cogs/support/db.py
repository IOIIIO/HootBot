import dataset
import ast

db = dataset.connect('sqlite:///settingstest.db')

def save(sheet, name, value):
	if type(value) == list:
		value = str(value)
	if db[sheet].find_one(name=name) is None:
		db[sheet].insert(dict(name=name, value=value))
	else:
		db[sheet].update(dict(name=name, value=value), ['name'])

#def savem(sheet, **kwargs):
#	with list(kwargs.keys())[0] as key:
#		if db[sheet].find_one(**{key: kwargs[key]}):
#			db[sheet].insert(kwargs)
#		else:
#			db[sheet].update(kwargs, next(iter(kwargs)))

def ret(sheet, name):
	if db[sheet].find_one(name=name) != None:
		return db[sheet].find_one(name=name)["value"]
	else:
		return None

#def retm(sheet, column, name):
#	if db[sheet].find_one(**{column: name}) != None:
#		return db[sheet].find_one(**{column: name})
#	else:
#		return None

def retar(sheet, name):
	if ret(sheet, name) != None:
		c = ast.literal_eval(ret(sheet, name))
		return(c)
	else:
		return None

def append(sheet, name, value):
	if retar(sheet, name) != None:
		b = retar(sheet, name)
		try:
			b.append(value)
		except:
			return None
		save(sheet, name, b)
	else:
		save(sheet, name, value)

def remove(sheet, name, value):
	if retar(sheet, name) != None:
		b = retar(sheet, name)
		try:
			b.remove(value)
		except:
			return None
		save(sheet, name, b)
	else:
		save(sheet, name, value)