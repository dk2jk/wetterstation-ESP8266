#delay.py

from time import sleep_ms

def Delay():
        start_main= False
        try:
            for i in range (30,-1,-1):
                sleep_ms(100)
                print(i,end=' ')
            start_main= True
        except KeyboardInterrupt:
            print('\nYou have pressed ctrl-c button.')
        return start_main

if __name__ == '__main__':
    start_flag= Delay()
    if start_flag:
        print ( 'weiter')
    else:
        print('stop')
