from machine import Pin, I2C
import ssd1306, time
# כפתור
button = Pin(27, Pin.IN, Pin.PULL_UP)

# תצוגת OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.text("press for PCR", 0, 0)
oled.show()
time.sleep(2)

if button.value() == 0:  # לחיצה התחילה 
    import main_pcr
else:
    import manoa_encoder
