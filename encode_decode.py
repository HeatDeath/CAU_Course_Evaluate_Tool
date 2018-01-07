from urllib import parse

def url_encode(string):
    return parse.quote(string.encode('gb2312'))

def url_decode(string):
    return parse.unquote(string)

aaa = url_encode('中文')
print(aaa)

print(url_decode(aaa))