import dataset

db = dataset.connect('sqlite:///settings.db')

def save(sheet, name, value):
    if db[sheet].find_one(name=name) is None:
        db[sheet].insert(dict(name=name, value=value))
    else:
        db[sheet].update(dict(name=name, value=value) ['name'])

def ret(sheet, name):
    if db[sheet].find_one(name=name) != None:
        return db[sheet].find_one(name=name)["value"]
    else:
        return None

print(db["bot"].find_one(name="token")["value"])
print(db["bot"].find_one(name="token"))
print(ret("bot", "owner_id"))