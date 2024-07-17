import random

a = ""
b = 0
c = []
d = []

def Ordering():
    global a, b, c, d
    a = input("好きな文字列を並び替えて出力:")
    d = list(a)

    while len(d) > 0:
        b = random.randint(0, len(d) - 1)
        c.append(d[b])
        del d[b] 

    print("並べ替え後の文字列:" + ''.join(c))#配列cないの要素をつなげている。

Ordering()
