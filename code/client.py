from machine import reset_cause,DEEPSLEEP,RTC,deepsleep,reset,I2C,Pin
from   time import sleep,time
import network
import sys
from   BME280_1 import BME280
import batterie
from   send_thingspeak2 import send
from   wdt import mywdt
from reset import Reset

''' led ports'''
blaueLed= Pin(2, Pin.OUT, value=1 )
roteled = Pin(14, Pin.OUT, value=1 ) #aus


''' deepsleep
    vorgabe in minuten , minuten=0 bedeutet aus
    deepsleep reset erfolgt ueber verbindung gpio16 mit res
    loetbruecke SJ3 'deep sleep' '''
class Schlafen:
    def __init__(self,*, minuten=0):
        self._en=0
        self.rtc = RTC()
        self.zeit(minuten)      
        self.rtc.irq(trigger=self.rtc.ALARM0, wake=DEEPSLEEP)
    def zeit(self,minuten=10.0):
        self._minuten=minuten
        if minuten > 0:
            self._en=True
        else:
            self._en=False
        ms= int(self._minuten*60*1000)
        self.rtc.alarm(self.rtc.ALARM0, ms )
    def jetzt(self):
        if self._en:           
            print( f"{self._minuten} Minuten schlafen...")
            wdt.stop()
            deepsleep()
            sleep(1) ##???
        else:
            print( 'deepsleep nicht freigegeben')
            wdt.stop()
            sys.exit()

''' BME280 sensor ueber i2c bus ansteuern
    da nur ein teilnehmer am i2c bus haengt, kann als adresse automatisch die erste und einzige
    beim scannnen gefundene adresse genommen werden
    - die Module haben evtll verschiedene adressen 0x77 ode 0x76 '''
bme=None
def start_bme():
    global bme
    try:
        # i2c sensor bme-280
        i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
        i2c_adr= i2c.scan()[0]
        print(f'BME adr: {hex(i2c_adr)}')
        bme = BME280(address=i2c_adr, i2c=i2c) 
        sleep(2)
    except Exception as e:
        y='?'
        if e.args[0]==19:
            y='Kein solches Geraet'
        raise Exception('BME, i2c :', y)

''' 4 messwerte '''
def messwerte():
    #messwerte lesen
    t = bme.temperature
    h = bme.humidity
    d = bme.pressure
    v = batterie.volt()
    return t,h,d,v

''' led kurz ( 0.1 sec) auf blitzen lassen '''
def blink(led= blaueLed):  
    sleep(.07)
    led.value(0)
    sleep(.02)
    led.value(1)

''' deepsleep starten mit ausgabe einer fehlermeldung
    watchdog vorher ausschalten '''
def schlaf_nach_fehler(e='alles ok'):
    print ('*** Fehler:',e)
    wdt.stop()
    for i in range (3):
        blink(roteled) 
    schlaf.jetzt() 

''' #################### hier start ################################### '''
print('...client')
''' falls lokal von der shell  gestartet wird, bleibt deepsleep aus '''
if __name__ == '__main__':
    schlaf= Schlafen(minuten=0)
else:
    schlaf= Schlafen(minuten=60)

''' reset meldung lesen und watchdog starten '''
reset=Reset()
wdt= mywdt()
wdt.start()
if reset.typ== "watchdog":   # kommt dann, wenn Batterie im tiefschlaf abgeklemmt wird
    schlaf.zeit(0.1)         # nur kurz
    schlaf_nach_fehler('watchdog')
try:
    '''BME280 sensor ueber i2c bus ansteuern'''
    start_bme()
except Exception as e:
    schlaf_nach_fehler(e)

'''10sec pause , um kb interrupt zu ermoeglichen'''
for i in range(10): 
    blink()

'''WLAN starten, falls noch nicht verbunden
   esp8266 merkt sich die einstellungen'''
WiFi_SSID, WiFi_PW= "dk2jk","dk2jk X1"

''' acces point deactivieren'''
ap = network.WLAN(network.AP_IF)
ap.active(False)

try:               
    sta = network.WLAN(network.STA_IF)
    if sta.active() and sta.isconnected():   # schon verbunden ?
        print ( f'verbunden mit "{sta.ifconfig()[0] }"')
    else:
        # neu verbinden
        try:
            sta.active(True)
            sta.connect(WiFi_SSID, WiFi_PW)
        except Exception as e:
            schlaf_nach_fehler(e) # verbindung hat nicht geklappt
            
        timeout=9
        wdt.feed() # ab jetzt 10 sec zeit bevor watchdog kommt
        count=0
        while not sta.isconnected (): # im abstand von 1 sec versuchen
            sleep(1)
            count=count+1
            print('{}'.format(count),end=' ') # ...
            if  count >= timeout:
                schlaf_nach_fehler('WLAN timeout!')
                break
    try:
        ''' messwerte senden !'''
        t,h,d,v=messwerte()
        #v=reset.message
        send(t,h,d,v)
    except:
        schlaf_nach_fehler('send()')
    finally:
        schlaf.jetzt()
    ''' #################### hier ende  ################################### '''
        
except KeyboardInterrupt:
    print( "kb interrupt erlaubt, stop hier")
except Exception as e:
    schlaf_nach_fehler(e) 
    #ende
