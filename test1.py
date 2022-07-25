# import sys
# print(sys.version)

bitarray = 1<<10

#bitarray |=  1<<2
print(bin(bitarray))

x=bitarray & 1<<2
print(x>0)