import dataset

db = dataset.connect('sqlite:///settings.db')

def save(sheet, name, value):
	if db[sheet].find_one(name=name) is None:
		db[sheet].insert(dict(name=name, value=value))
	else:
		db[sheet].update(dict(name=name, value=value), ['name'])

def ret(sheet, name):
	if db[sheet].find_one(name=name) != None:
		return db[sheet].find_one(name=name)["value"]
	else:
		return None

def append(sheet, name, value):
	if b := ret(sheet, name) != None:
		b.append(value)
		save(sheet, name, b)
	else:
		save(sheet, name, value)

def remove(sheet, name, value):
	if b := ret(sheet, name) != None:
		try:
			b.remove(value)
		except:
			return None
		save(sheet, name, b)
	else:
		save(sheet, name, value)