from datetime import datetime
import json
from PIL import Image, ImageDraw, ImageFont
from adafruit_epd.epd import Adafruit_EPD
import socket

tiny_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10
)

small_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16
)
medium_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
large_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
)
icon_font = ImageFont.truetype("/usr/share/fonts/truetype/meteocons/meteocons.ttf", 48)


# Map the OpenWeatherMap icon code to the appropriate font character
# See http://www.alessioatzeni.com/meteocons/ for icons
ICON_MAP = {
    "01d": "B",
    "01n": "C",
    "02d": "H",
    "02n": "I",
    "03d": "N",
    "03n": "N",
    "04d": "Y",
    "04n": "Y",
    "09d": "Q",
    "09n": "Q",
    "10d": "R",
    "10n": "R",
    "11d": "Z",
    "11n": "Z",
    "13d": "W",
    "13n": "W",
    "50d": "J",
    "50n": "K",
}

# RGB Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Weather_Graphics:
    def __init__(self, display, *, am_pm=True, celsius=True):
        self.am_pm = am_pm
        self.celsius = celsius

        self.tiny_font = tiny_font
        self.small_font = small_font
        self.medium_font = medium_font
        self.large_font = large_font

        self.display = display

        self._weather_icon = None
        self._city_name = None
        self._main_text = None
        self._temperature = None
        self._description = None
        self._time_text = None
        self._inside_temperature = None
        self._inside_humidity = None
        self._inside_pressure = None

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
             s.connect(("8.8.8.8", 80))
             self.ipaddr = s.getsockname()[0]

    def display_weather(self, weather, sensor):
        weather = json.loads(weather.decode("utf-8"))

        # set the icon/background
        self._weather_icon = ICON_MAP[weather["weather"][0]["icon"]]

        city_name = weather["name"] + ", " + weather["sys"]["country"]
        print(city_name)
        self._city_name = city_name

        main = weather["weather"][0]["main"]
        print(main)
        self._main_text = main

        temperature = weather["main"]["temp"] - 273.15  # its...in kelvin
        print(temperature)
        if self.celsius:
            self._temperature = "%d °C" % temperature
            self._inside_temperature = "%d °C" % sensor.temperature
        else:
            self._temperature = "%d °F" % ((temperature * 9 / 5) + 32)
            self._inside_temperature = "%d °C" % ((sensor.temperature * 9/5)+32)

        self._inside_humidity = "%d %%" % sensor.humidity
        self._inside_pressure = "%d hPa" % sensor.pressure
        description = weather["weather"][0]["description"]
        description = description[0].upper() + description[1:]
        print(description)
        print(self._inside_temperature, self._inside_pressure, self._inside_humidity)
        self._description = description
        # "thunderstorm with heavy drizzle"

        self.update_time()

    def update_time(self):
        now = datetime.now()
        self._time_text = now.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
        self.update_display()


    def clear_display(self):
        self.display.fill(Adafruit_EPD.WHITE)
        image = Image.new("RGB", (self.display.width, self.display.height), color=WHITE)
        draw = ImageDraw.Draw(image)
        self.display.image(image)
        self.display.display()

    def update_display(self):
        self.display.fill(Adafruit_EPD.WHITE)
        image = Image.new("RGB", (self.display.width, self.display.height), color=WHITE)
        draw = ImageDraw.Draw(image)

        # Draw the Icon
        (font_width, font_height) = icon_font.getsize(self._weather_icon)
        draw.text(
            (
                self.display.width // 2 - font_width // 2,
                self.display.height // 2 - font_height // 2 - 10,
            ),
            self._weather_icon,
            font=icon_font,
            fill=BLACK,
        )

	# Draw ip address
        (font_width, _) = tiny_font.getsize(self.ipaddr) 
        draw.text(
             (self.display.width-font_width,0), self.ipaddr, font=self.tiny_font, fill=BLACK,
        )

	# Draw the city
        draw.text(
            (3, 0), self._city_name, font=self.medium_font, fill=BLACK,
        )

        # Draw the time
        (font_width, font_height) = medium_font.getsize(self._time_text)
        draw.text(
            (3, font_height * 2 - 5),
            self._time_text,
            font=self.medium_font,
            fill=BLACK,
        )

        # Draw the main text
        (font_width, font_height) = large_font.getsize(self._main_text)
        draw.text(
            (3, self.display.height - font_height * 2),
            self._main_text,
            font=self.large_font,
            fill=BLACK,
        )

        # Draw the description
        (font_width, font_height) = small_font.getsize(self._description)
        draw.text(
            (3, self.display.height - font_height - 5),
            "BOOGERS",
            #self._description,
            font=self.small_font,
            fill=BLACK,
        )

        # Draw the temperature
        (font_width, font_height) = large_font.getsize(self._temperature)
        draw.text(
            (
                self.display.width - font_width - 5,
                self.display.height - font_height * 2 -10,
            ),
            self._temperature,
            font=self.large_font,
            fill=BLACK,
        )

        #Draw the internal values
        inside_text = f"inside: {self._inside_temperature}   {self._inside_humidity}"
        (font_width, font_height) = large_font.getsize(inside_text)
        draw.text(
            (0, self.display.height-font_height),
            inside_text,
            font=self.small_font,
            fill=BLACK,
        )

        self.display.image(image)
        self.display.display()
