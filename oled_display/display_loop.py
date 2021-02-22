# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

import time
import subprocess
import sys
from datetime import datetime

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import signal

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    print(f'received kill signal {signum}, exiting')
    self.kill_now = True


# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
disp.rotation=2
# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = 0
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
#font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/a_goblin_appears/aga.otf', 7)

draw.rectangle((0, 0, width, height), outline=0, fill=0)
disp.image(image)
disp.show()
draw.text((x, top + 8), "Hello, Hans", font=font, fill=255)
disp.image(image)
disp.show()
time.sleep(10)


killer = GracefulKiller()
i=0
imax=12
while not killer.kill_now:
    try:
	    # Draw a black filled box to clear the image.
	    draw.rectangle((0, 0, width, height), outline=0, fill=0)
	    # Shell scripts for system monitoring from here:
	    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
	    cmd = "hostname -I | cut -d' ' -f1"
	    IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
	    cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
	    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
	    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
	    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
	    cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
	    Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
	    cmd = '/usr/sbin/iwgetid -r'
	    Net = subprocess.check_output(cmd, shell=True).decode("utf-8")
	    time_str = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
	    cmd = 'uptime -p'
	    UpTime = subprocess.check_output(cmd, shell=True).decode("utf-8")

	    # Write four lines of text.
	    line1 = [time_str]
	    line2 = ["IP: " + IP, "SSID: " + Net]
	    line3 = [CPU, MemUsage, Disk]
	    line4 = [UpTime]

	    draw.text((x, top + 0), line1[0], font=font, fill=255)
	    draw.text((x, top + 8), line2[i//8], font=font, fill=255)
	    draw.text((x, top + 16), line3[i//4], font=font, fill=255)
	    draw.text((x, top + 25), line4[0], font=font, fill=255)

	    # Display 2image.
	    disp.image(image)
	    disp.show()
	    time.sleep(0.25)
	    i=(i+1)%imax
    except subprocess.CalledProcessError as e:
        print('caught error in subprocess')
        print(e)
        killer.kill_now=True
else:
	print('exiting')
	draw.rectangle((0, 0, width, height), outline=0, fill=0)
	disp.image(image)
	disp.show()
	time.sleep(0.25)
	draw.text((x, top + 8), "Goodbye, Hans", font=font, fill=255)
	disp.image(image)
	disp.show()
	time.sleep(2)
	draw.rectangle((0, 0, width, height), outline=0, fill=0)
	disp.image(image)
	disp.show()
	sys.exit(0)
