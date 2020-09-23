def save(sheet, **kwargs):
    print(kwargs)
    #print(kwargs[1])
    print(kwargs["name"])

save(1212, name="cock", type="nerd", bruh="yes")

def save2(sheet, *args):
    print(args)
    print(args[1])
    print(args[2])
    return

save2(1212, "cock", "nerd", "yes")

eval(save())