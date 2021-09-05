import json
import os
import dataset

rows = []

if os.path.isfile("bot.json"):
	cfg = json.load(open('bot.json'))
else:
	print("no importable config found")
	exit()

for server in cfg:
	if server not in ["config", "token", "owner"]:
		for conc in cfg[server]["ignore_list"]:
			message = conc[18:]
			channel = conc[:18]
			print("Found: Server: {} - Channel: {} - Message: {}".format(server, channel, message))
			rows.append(dict(server_id=server, channel_id=channel, message_id=message))

db = dataset.connect('sqlite:///settings.db')
db.begin()
try:
    db["starboardIgnore"].upsert_many(rows, ['message_id'])
    db.commit()
except:
    db.rollback()