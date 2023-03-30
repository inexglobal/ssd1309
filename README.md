# ssd1309
OLED 128*64
```c/c++
from machine import Pin,SoftI2C
from ssd1309 import SSD1309_I2C
import time
i2cbus = SoftI2C(scl=Pin(7),sda=Pin(6),freq=100_000)
oled =SSD1309_I2C(128,64,i2cbus)
c=35.678
h=56.789
oled.fill(0)
oled.text(' Pi Pico',0,0*10)
oled.text('MicroPython',0,1*10)
oled.text('Temp : {0:.2f}'.format(c),0,2*10)
oled.text('Humid : %.2f' %h,0,3*10)
oled.show()
time.sleep(2)
oled.invert(1)
time.sleep(2)
oled.invert(0)
```
