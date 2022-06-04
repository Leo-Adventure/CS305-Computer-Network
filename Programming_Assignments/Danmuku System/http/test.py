import re

price = '25.34-34.55'

test = re.compile(r'[1-9]\d*\.\d*|0\.\d*[1-9]|[1-9]\d*').findall(price)[0]
test2 = re.compile(r'-[1-9]\d*\.\d*|-0\.\d*[1-9]|-[1-9]\d*').findall(price)[0]

i = float(test)
x = -float(test2)
print(i)
print(x)