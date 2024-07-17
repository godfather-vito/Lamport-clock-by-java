class calc:
    def __init__(self):
        self.unk = 1

    def __iter__(self):
        return self
    
    def __next__(self):
        value = self.unk
        self.unk += 1
        return value

renshu = calc()
j = 0
for i in renshu:
    j += 1
    if j > 100:
        break
    else:
        print(i)

