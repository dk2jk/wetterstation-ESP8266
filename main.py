#  main.py
from delay import Delay
print('main...')
start_flag= Delay()
if start_flag:
    print ( 'weiter')
    from readme import version
    print(version)
    import client
else:
    print('stop')

