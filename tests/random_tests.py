
def carre_yield():
    for i in range(1, 4):
        yield i**2


for val in carre_yield():
    print(val)