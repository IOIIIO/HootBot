import os, sys, subprocess
import cogs.support.db as dbc

class Launch:
    def __init__(self):
        self.f = 1

    def main(self):
        failT = False
        failO = False
        self.resize(80,24)
        try:
            import dataset
        except:
            self.head("Failed to load required modules.")
            print("Do you wish to download them?")
            print("")
            x = input("y/n: ")
            if x == "y":
                self.req()
                print("Please launch the program again!")
                exit()
            else:
                print("Can't start without requirements.")
                exit()
            
        self.settings = dbc.db['bot']
        #print(self.settings.find_one(name="token"))
        #exit()
        print(testa := self.settings.find_one(name="token"))
        if testa is None:
            print(testa)
            failT = True
        print(testb := self.settings.find_one(name="owner_id"))
        if testb is None:
            print(testb)
            failO = True
        if failT or failO is not False:
            self.head("First boot or missing files!")
            print("")
            if failT == True:
                self.token()
            if failO == True:
                self.id()
        self.menu()
        
    def menu(self):
        self.head("Boot Menu")
        print("")
        print("1. Boot bot")
        print("2. Maintenance menu")
        print("")
        print("3. Exit")
        x = input("Type number: ")
        if x == "1":
            self.boot()
        elif x == "2":
            self.cls()
            self.maintenance()
        elif x == "3":
            exit()
        else:
            print("Invalid option!")
            self.menu()

    def maintenance(self):
        self.head("Maintenance Menu", False)
        print("")
        print("1. Update bot")
        print("2. Update requirements")
        print("3. Update all")
        print("4. Delete database")
        print("5. Factory reset")
        print("6. Change owner ID")
        print("7. Change bot token")
        print("")
        print("8. Go back")
        x = input("Type number: ")
        if x == "1":
            self.update()
            self.maintenance()
        elif x == "2":
            self.req()
            self.maintenance()
        elif x == "3":
            self.update()
            self.req(False)
            self.maintenance()
        elif x == "4":
            self.delete()
            self.maintenance()
        elif x == "5":
            self.factory()
            self.maintenance()
        elif x == "6":
            self.id()
            self.maintenance()
        elif x == "7":
            self.token()
            self.maintenance()
        elif x == "8":
            self.menu()
        else:
            print("Invalid option!")
            self.maintenance()

    def factory(self):
        print("Are you sure you want to do this?")
        print("All bot data will be wiped, and the latest reinstalled!")
        print("THIS ACTION IS IRREVERSABLE!")
        x = input("y/n: ")
        if x == "y":
            os.system("git fetch origin")
            os.system("git reset --hard origin/master")
            self.maintenance()
        elif x == "n":
            self.maintenance()
        else:
            self.factory()

    def delete(self):
        print("Are you sure you want to do this?")
        print("THIS ACTION IS IRREVERSABLE!")
        x = input("y/n: ")
        if x == "y":
            os.remove("settings.db")     
            print("Database deleted.")
            self.maintenance()
        elif x == "n":
            self.maintenance()
        else:
            self.delete()

    def req(self, wipe = True):
        if wipe == True:
            self.cls()
        subprocess.check_call([sys.executable, "-m", "pip", "install",  "-r", "requirements.txt"])

    def update(self):
        self.cls()
        try:
            code = subprocess.call(("git", "pull", "--ff-only"))
        except FileNotFoundError:
            print("\nError: Git not found. It's either not installed or not in PATH.")
            return
        if code == 0:
            print("\nUpdated successfully.")
        else:
            print("\nUpdate failed. Did you tinker around with the code?")
    
    def boot(self):
        self.cls()
        os.system('{} bot.py'.format(sys.executable))

    def id(self):
        self.cls()
        print("Enter the user ID of the bot owner.")
        id = input("")
        dbc.save("owned_id", id)

    def token(self):
        self.cls()
        print("Enter the bot token you got from the Discord developer site.")
        token = input("")
        if "." in token:
            dbc.save("token", token)
        else:
            print("That doesn't look like a valid token!")
            self.token()

    def head(self, text = None, clear = True, width = 55): # From CorpNewt's utils.py
        if clear == True:
            self.cls()
        print("  {}".format("#"*width))
        mid_len = int(round(width/2-len(text)/2)-2)
        middle = " #{}{}{}#".format(" "*mid_len, text, " "*((width - mid_len - len(text))-2))
        if len(middle) > width+1:
            # Get the difference
            di = len(middle) - width
            # Add the padding for the ...#
            di += 3
            # Trim the string
            middle = middle[:-di] + "...#"
        print(middle)
        print("#"*width)

    def resize(self, width, height): # From CorpNewt's utils.py
        print('\033[8;{};{}t'.format(height, width))

    def cls(self): # From CorpNewt's utils.py
    	os.system('cls' if os.name=='nt' else 'clear')

while True:
    Launch().main()
