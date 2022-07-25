# batterie.py

import machine
from time import sleep

''' batteriespannung messen, loetbruecke 'MSG' muss geschlossen sein
    spannungsteiler 470k 100k an ADC0
    max spannung am adc 1 volt '''
def volt():
        y=5.0*machine.ADC(0).read() /944
        return round (y,2) # 2 stellen hinter'm komma reichen
    # bei 5V 944 gemessen ,empirisch

''' test '''
if __name__=='__main__':
    from time import sleep
    while True:
        print( f"Batteriespannung= {volt()} Volt" )
        sleep(1)