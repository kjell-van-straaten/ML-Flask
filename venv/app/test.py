import hashlib
print('123'.encode('utf-8'))
print(str(int(hashlib.md5('123'.encode('utf-8')).hexdigest(), 16)))

