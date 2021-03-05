from gpiozero import LED
from time import sleep

#relay pin matching, from top to bottom
relay_order = [14, 15, 18, 17, 27, 22, 23, 24]


relays = {i: LED(j) for i,j in enumerate(relay_order)}


i=0
while(True):
	relays[i].toggle()
	sleep(0.1)
	i=(i+1)%len(relays)
