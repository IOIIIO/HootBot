def save(sheet, **kwargs):
    print(kwargs)
    #print(kwargs[1])
    print(kwargs["name"])
    print(next(iter(kwargs.list())))

save(1212, name="cock", type="nerd", bruh="yes")