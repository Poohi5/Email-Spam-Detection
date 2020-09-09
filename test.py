from emailclass import Email

e1 = Email("vignesh","0")
e2 = Email("click","1")
e3 = Email("vignesh","0")
e4 = Email("0","vignesh")

print(hash(e1))
print(hash(e2))
print(hash(e3))
print(hash(e4))

if (e1 == e3):
    print("true")
