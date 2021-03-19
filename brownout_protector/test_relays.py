from gpiozero import LED,  Button
from time import sleep
import datetime as dt

relay = LED(16)
reader = Button(14)
relay.on()
sleep(1)
relay.off()
sleep(1)
relay.on()
sleep(5)
start = dt.datetime.now()
relay.off()
while not reader.is_active:
    print('still dead')
end = dt.datetime.now()
print(end-start)

