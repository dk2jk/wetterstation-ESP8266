## Simple software WDT implementation
import machine
from micropython import const,alloc_emergency_exception_buf
alloc_emergency_exception_buf(100)

'''
nachdem der watchdog mit ' wdt_start()' gestartet wurde, muss spaetestens nach 10 sekunden wieder 'wdt_feed()' aufgerufen werden.
falls ein programmteil sich aufhaengt oder mehr als 10 sekunden benoetigt, wird vom watchdog ein reset ausgeloest. der reset
erfolgt ueber 'machine.reset()' . Die CPU startet mit 'boot.py' neu mit der
meldung  'ets Jan  8 2013, rst cause:4, boot mode:(3,0) wdt reset '.
'''

wdt_timeout=const(10)
class mywdt:
    def __init__(self):
        self.wdt_timer = machine.Timer(-1)
        self.feed()

    ''' interrupt routine laeuft jede sekunde;
        wenn zaehler den grenzwert ueberschreitet,
        wird ein softreset ausgelöst , dann weiter bei 'boot.py' '''
    def _callback(self):
        self.wdt_counter += 1
        if (self.wdt_counter >= wdt_timeout):
            self.wdt_timer.deinit()
            machine.reset()  ## softreset =4

    ''' watchdog counter zuruecksetzen / restart '''
    def feed(self):
        self.wdt_counter = 0

    ''' hardware timer wird gestartet, watchdog ist jetzt scharf '''
    def start(self): 
        self.wdt_timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=lambda t:self._callback())

    ''' watchdog stoppen , nicht mehr scharf '''
    def stop(self):
        try:
            self.wdt_timer.deinit()
        except:
            pass
        self.wdt_counter = 0
        #machine.RTC().memory(b'wdt gestoppt')

## END Simple software WDT implementation
        
if __name__ == '__main__':
    import time
    w= mywdt()
    w.start()
    for i in range (13):   # bei 9 gehts noch;  bei 10 spricht er an
        time.sleep(1)
        print(i,end=' ')
        #w.feed()           # hiermit spricht er nicht mehr an
    w.stop()

