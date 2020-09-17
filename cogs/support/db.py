import dataset
import ast

db = dataset.connect('sqlite:///settings.db')

def save(sheet, name, value):
	if type(value) == list:
		value = str(value)
	if db[sheet].find_one(name=name) is None:
		db[sheet].insert(dict(name=name, value=value))
	else:
		db[sheet].update(dict(name=name, value=value), ['name'])

def savem(sheet, **kwargs):
	if db[sheet].find_one(next(iter(kwargs.values()))) is None:
		db[sheet].insert(kwargs)
	else:
		db[sheet].update(kwargs, next(iter(kwargs)))

def ret(sheet, name):
	if db[sheet].find_one(name=name) != None:
		return db[sheet].find_one(name=name)["value"]
	else:
		return None

def retm(sheet, **kwargs):
	if db[sheet].find_one(next(iter(kwargs))=next(iter(kwargs.values()))) != None:
		return db[sheet].find_one(next(iter(kwargs))=next(iter(kwargs.values())))
	else:
		return None

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