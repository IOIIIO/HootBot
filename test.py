import dataset
db = dataset.connect('sqlite:///settings.db')
bruh = db["farts"]

print(d := bruh.find_one(name="token"))
print(type(d))
if None == d:
    print("Value = None")