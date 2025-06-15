
from machine import Pin, PWM, I2C
import ssd1306
import time
import onewire, ds18x20, math, machine

# אתחול חיישן DS18B20
ds_sensor = ds18x20.DS18X20(onewire.OneWire(machine.Pin(15)))

# פונקציה לחישוב ממוצע מתגלגל
def calculate_moving_average(values, new_value, max_size=3):
    values.append(new_value)
    if len(values) > max_size:
        values.pop(0)
    return sum(values) / len(values)

def read_temperature(temp_history):
    try:
        roms = ds_sensor.scan()
        if not roms:
            return None  # אין חיישן

        ds_sensor.convert_temp()
        time.sleep_ms(750)
        for rom in roms:
            temperature_c = ds_sensor.read_temp(rom)
            return calculate_moving_average(temp_history, temperature_c)
    except Exception as e:
        print("שגיאה בקריאת טמפרטורה:", e)
        return None

# משתנים גלובליים
direction, speed, temp = False, False, False

# הגדרת הפינים של רוטרי אנקודר
clk_pin = Pin(25, Pin.IN, Pin.PULL_UP)
dt_pin = Pin(26, Pin.IN, Pin.PULL_UP)

# הגדרת מנוע
R_EN = Pin(15, Pin.OUT)
R_PWM = PWM(Pin(18))
L_EN = Pin(23, Pin.OUT)
L_PWM = PWM(Pin(19))
R_PWM.freq(5000)
L_PWM.freq(5000)
R_EN.value(1)
L_EN.value(1)

# תצוגת OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# כפתור איפוס
reset_button = Pin(27, Pin.IN, Pin.PULL_UP)

# משתנים לאנקודר
counter = 0
last_clk_state = clk_pin.value()

# עדכון מהירות מנוע
def update_motor_speed(counter):
    speed = min(max(abs(counter), 0), 1023)
    if counter > 0:
        L_PWM.duty(speed)
        R_PWM.duty(0)
        direction = "Right"
    elif counter < 0:
        L_PWM.duty(0)
        R_PWM.duty(speed)
        direction = "Left"
    else:
        L_PWM.duty(0)
        R_PWM.duty(0)
        direction = "Stopped"
    return direction, speed

start_time = time.ticks_ms()  # זמן התחלת הריצה של הקוד

# עדכון מסך OLED
def update_oled_display():
    global direction, speed, temp
    oled.fill(0)
    oled.text("Motor Control", 0, 0)
    oled.text(f"TEMP: {temp:.2f}C" if temp is not None else "TEMP: --", 0, 18)
    oled.text(f"Direction: {direction}", 0, 35)
    oled.text(f"Speed: {speed}", 0, 45)
    # חישוב זמן שעבר
    elapsed_ms = time.ticks_diff(time.ticks_ms(), start_time)
    elapsed_seconds = elapsed_ms // 1000
    oled.text(f"Time: {elapsed_seconds}s", 0, 55)
    oled.show()

# Callback לאנקודר
def rotary_callback(pin):
    global counter, last_clk_state
    clk_state = clk_pin.value()
    dt_state = dt_pin.value()

    if clk_state != last_clk_state:
        if dt_state != clk_state:
            counter += 10
        else:
            counter -= 10
        global direction, speed
        direction, speed = update_motor_speed(counter)
        update_oled_display()

    last_clk_state = clk_state

# איפוס
def reset_system():
    global counter, direction, speed, temp
    counter = 0
    direction, speed, temp = False, False, False
    L_PWM.duty(0)
    R_PWM.duty(0)
    update_oled_display()

# מסך ראשוני
oled.fill(0)
oled.text("Motor Control", 0, 0)
oled.text("Rotate encoder", 0, 35)
oled.text("to control motor", 0, 50)
oled.show()

# הגדרת IRQ לאנקודר
clk_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=rotary_callback)

# אתחול היסטוריית טמפרטורה
temp_history = []
last_temp_check = time.ticks_ms()
TEMP_CHECK_INTERVAL = 10000  # 5 שניות

# לולאה ראשית
while True:
    now = time.ticks_ms()

    # קריאת טמפרטורה כל 5 שניות
    if time.ticks_diff(now, last_temp_check) > TEMP_CHECK_INTERVAL:
        last_temp_check = now
        roms = ds_sensor.scan()
        if roms:
            temp = read_temperature(temp_history)
        else:
            temp = False
        update_oled_display()

    if reset_button.value() == 0:
        reset_system()

    time.sleep(0.1)



'''
# קוד לנוע דו כיווני 12 וולט עם מסך ורוטרי אנקודר וכפתור הכל מושלם

from machine import Pin, PWM, I2C
import ssd1306
import time

# הגדרת הפינים של הרוטרי אנקודר
clk_pin = Pin(25, Pin.IN, Pin.PULL_UP)  # CLK
dt_pin = Pin(26, Pin.IN, Pin.PULL_UP)   # DT

# הגדרת הפינים של המנוע
R_EN = Pin(15, Pin.OUT)
R_PWM = PWM(Pin(18))
L_EN = Pin(23, Pin.OUT)
L_PWM = PWM(Pin(19))

# הגדרת תדר ה-PWM
R_PWM.freq(5000)  # תדר 5kHz אפשר גם 5000
L_PWM.freq(5000)  # תדר 5kHz אפשר גם 5000

# אתחול של הפינים
R_EN.value(1)
L_EN.value(1)

# הגדרת תצוגת ה-OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # הגדרת הפינים ל-SDA ו-SCL
oled_width = 128  # רוחב המסך
oled_height = 64  # גובה המסך
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# הגדרת כפתור האיפוס
reset_button = Pin(27, Pin.IN, Pin.PULL_UP)

# משתנים
counter = 0
last_clk_state = clk_pin.value()

# פונקציה לעדכון מהירות המנוע
def update_motor_speed(counter):
    # הגבלת ערכים של counter ל-0 עד 1023
    speed = min(max(abs(counter), 0), 1023)
   
    if counter > 0:  # סיבוב קדימה
        L_PWM.duty(speed)
        R_PWM.duty(0)
        direction = "Right"  # כיוון ימינה
    elif counter < 0:  # סיבוב אחורה
        L_PWM.duty(0)
        R_PWM.duty(speed)
        direction = "Left"  # כיוון שמאלה
    else:  # עצירה
        L_PWM.duty(0)
        R_PWM.duty(0)
        direction = "Stopped"  # עצירה
   
    return direction, speed

# פונקציה לעדכון תצוגת ה-OLED
def update_oled_display(direction, speed):
    oled.fill(0)  # ניקוי המסך
    oled.text("Motor Control", 0, 0)  # כותרת
    oled.text(f"Direction: {direction}", 0, 30)  # כיוון הסיבוב
    oled.text(f"Speed: {speed}", 0, 50)  # מהירות המנוע
    oled.show()  # הצגת התוכן

# פונקציית callback של הרוטרי אנקודר
def rotary_callback(pin):
    global counter, last_clk_state
    clk_state = clk_pin.value()
    dt_state = dt_pin.value()

    if clk_state != last_clk_state:
        if dt_state != clk_state:
            counter += 10  # הגדלה בכיוון חיובי
        else:
            counter -= 10  # הגדלה בכיוון שלילי
       
        direction, speed = update_motor_speed(counter)
        update_oled_display(direction, speed)

    last_clk_state = clk_state

# פונקציה לאיפוס על ידי הכפתור
def reset_system():
    global counter
    counter = 0
    L_PWM.duty(0)
    R_PWM.duty(0)
    update_oled_display("Stopped", 0)

# הצגת הודעה ראשונית על המסך
oled.fill(0)
oled.text("Motor Control", 0, 0)
oled.text("Rotate encoder", 0, 30)
oled.text("to control motor", 0, 50)
oled.show()

# הגדרת טריגר להפעלת פונקציית callback
clk_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=rotary_callback)

# לולאה ראשית
while True:
    if reset_button.value() == 0:  # כפתור לחוץ
        reset_system()
    time.sleep(0.1)  # זמן מנוחה כדי למנוע עומס על המעבד
'''

