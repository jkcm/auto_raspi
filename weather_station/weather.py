"""
This example queries the Open Weather Maps site API to find out the current
weather for your location... and display it on a eInk Bonnet!
"""

import time
import urllib.request
import urllib.parse
import digitalio
import busio
import board
from adafruit_bme280 import Adafruit_BME280_I2C
from adafruit_epd.ssd1675 import Adafruit_SSD1675
from weather_graphics import Weather_Graphics
import signal
from threading import Event 
import sys

exit = Event()

def quit(signum, _):
    print(f'received kill signal {signum}, exiting')
    exit.set()

def main():
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    i2c = busio.I2C(board.SCL, board.SDA)
    ecs = digitalio.DigitalInOut(board.CE0)
    dc = digitalio.DigitalInOut(board.D22)
    rst = digitalio.DigitalInOut(board.D27)
    busy = digitalio.DigitalInOut(board.D17)

    # You'll need to get a token from openweathermap.org, looks like:
    # 'b6907d289e10d714a6e88b30761fae22'
    OPEN_WEATHER_TOKEN = 'f1525c6af313ad137fea6d36606822c9'

    # Use cityname, country code where countrycode is ISO3166 format.
    # E.g. "New York, US" or "London, GB"
    LOCATION = "Wenatchee, US"
    DATA_SOURCE_URL = "http://api.openweathermap.org/data/2.5/weather"

    if len(OPEN_WEATHER_TOKEN) == 0:
        raise RuntimeError(
            "You need to set your token first. If you don't already have one, you can register for a free account at https://home.openweathermap.org/users/sign_up"
        )

    # Set up where we'll be fetching data from
    params = {"q": LOCATION, "appid": OPEN_WEATHER_TOKEN}
    data_source = DATA_SOURCE_URL + "?" + urllib.parse.urlencode(params)

    # Initialize the Display
    display = Adafruit_SSD1675(
        122, 250, spi, cs_pin=ecs, dc_pin=dc, sramcs_pin=None, rst_pin=rst, busy_pin=busy,
    )

    display.rotation = 1

    gfx = Weather_Graphics(display, am_pm=True, celsius=False)
    weather_refresh = None

    # Try to read from the weather device
    try:
        bme280 = Adafruit_BME280_I2C(i2c)
    except InputError as e: #TODO actually catch the proper exception and handle it
        pass


    while not exit.is_set():
        try:
            # only query the weather every 10 minutes (and on first run)
            if (not weather_refresh) or (time.monotonic() - weather_refresh) > 300:
                response = urllib.request.urlopen(data_source)
                if response.getcode() == 200:
                    value = response.read()
                    print("Response is", value)
                    gfx.display_weather(value, bme280)
                    weather_refresh = time.monotonic()
                else:
                    print("Unable to retrieve data at {}".format(url))
            gfx.update_time()
            print('gonna wait for 3 mins')
            exit.wait(180)  # wait 5 minutes before updating anything again
            print('done waiting for 3 mins')
        except subprocess.CalledProcessError as e:
            print('caught error in subprocess')
            print(e)
            
    else:
        print('exiting')
        gfx.clear_display()
        time.sleep(1)
        sys.exit(0)

if __name__ =='__main__':
    for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(getattr(signal, 'SIG'+sig), quit);

    main()
