import dataset

db = dataset.connect('sqlite:///settings.db')

def save(name, value):
    if db.find_one(name=name) is None:
        db.insert(dict(name=name, value=value))
    else:
        db.update(dict(name=name, value=value) ['name'])

def ret(sheet, name):
    return db[sheet].find_one(name=name)["value"]
