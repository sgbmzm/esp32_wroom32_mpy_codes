#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# ספריות פייתון שהם דרייברים לרכיבים שונים

# https://github.com/rafaelaroca/max30100/blob/master/max30100.py
# https://github.com/adafruit/Adafruit_CircuitPython_DS3231/blob/main/adafruit_ds3231.py
# https://github.com/pangopi/micropython-DS3231-AT24C32/blob/main/ds3231.py
# https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py # הרשמי
# https://raw.githubusercontent.com/RuiSantosdotme/ESP-MicroPython/master/code/WiFi/HTTP_Client_IFTTT_BME280/BME280.py
# https://github.com/miketeachman/micropython-rotary/blob/master/rotary.py
# https://github.com/miketeachman/micropython-rotary/blob/master/rotary_irq_esp.py
#https://github.com/pangopi/micropython-DS3231-AT24C32/blob/main/ds3231.py
# https://github.com/peterhinch/micropython-samples/blob/d2929df1b4556e71fcfd7d83afd9cf3ffd98fdac/astronomy/sun_moon.py
# https://github.com/peterhinch/micropython-samples/blob/d2929df1b4556e71fcfd7d83afd9cf3ffd98fdac/astronomy/moonphase.py
# https://github.com/peterhinch/micropython-samples/issues/42
# https://github.com/peterhinch/micropython-samples/tree/d2929df1b4556e71fcfd7d83afd9cf3ffd98fdac/astronomy


# פין 12 לא יכול להיות מחובר ל I2C כי זה תוקע את המכשיר


# In[ ]:


# הדלקת לד כחול שעל גבי הבקר קוד הכי בסיסי ופשוט
import machine
led = machine.Pin(2, machine.Pin.OUT)
led.value(1)
# led.value(0)


# In[ ]:


#אפשר להשתמש בכפתור בוט ככפתור

from machine import Pin
import time

# הגדרת GPIO0 כקלט עם התנגדות פנימית כלפי מעלה
boot_button = Pin(0, Pin.IN, Pin.PULL_UP)

while True:
    if boot_button.value() == 0:  # בדיקת אם הכפתור נלחץ
        print("Boot button pressed!")
        # ניתן להוסיף כאן קוד לבצע פעולה
        time.sleep(0.5)  # מניעת קריאה מרובה בזמן הלחיצה


# In[13]:


def get_utc_offset(longitude):
    return abs(round(longitude/15))

longitude = 1000
get_utc_offset(longitude)


# In[25]:


abs(round(950/15)) % 24


# In[ ]:


# דוגמא לקוד בורסט רק קוד לדוגמא ולא להפעלה
import time
import machine

# הגדרות חומרה
heater_pin = machine.Pin(2, machine.Pin.OUT)  # פין הפעלת גוף החימום
target_temp = 95  # הטמפרטורה הרצויה
temp_tolerance = 0.5  # סטייה מותרת
heater_on_time = 500  # זמן הפעלה (במילישניות)
heater_off_time = 200  # זמן השהייה (במילישניות)

def get_temperature():
    # פונקציה לדוגמה, מחזירה טמפרטורה מהחיישן
    return read_sensor_temp()  # קריאה מחיישן DS18B20 לדוגמה

while True:
    current_temp = get_temperature()
    print(f"Current Temperature: {current_temp}°C")
    
    if current_temp < (target_temp - temp_tolerance):
        print("Turning heater ON")
        heater_pin.value(1)  # הפעלת גוף חימום
        time.sleep_ms(heater_on_time)  # זמן הפעלה
    else:
        print("Turning heater OFF")
        heater_pin.value(0)  # כיבוי גוף חימום
        time.sleep_ms(heater_off_time)  # זמן הפסקה


# In[ ]:


# ניסיון שני לקוד PCR
# עובד קצת יותר טוב ברעיון של להשתמש ב PID רק לצורך כוונון עדין כשמגיעים לאיזור טמפרטורת היעד
# בינתיים זה הקוד היציב שעובד


from machine import Pin, PWM, ADC, I2C
import onewire, ds18x20, time, math, machine
from ssd1306 import SSD1306_I2C

# ------------------------
# הגדרות בסיסיות
# ------------------------
PWM_MAX = 1023  # ערך מקסימלי של PWM אם רוצים כמו 5 וולט אז צריך 426

PWM_FREQ = 5000  # תדר ה-PWM

# ------------------------
# הגדרת פינים ל-BTS7960
# ------------------------
R_EN = Pin(15, Pin.OUT)  # אפשר קירור
R_PWM = PWM(Pin(18))
L_EN = Pin(23, Pin.OUT)  # אפשר חימום
L_PWM = PWM(Pin(19))

R_PWM.freq(PWM_FREQ)
L_PWM.freq(PWM_FREQ)

R_EN.value(1)  # אפשר קירור
L_EN.value(1)  # אפשר חימום


# ------------------------
# הגדרת הפינים של הרוטרי אנקודר
# ------------------------
clk_pin = Pin(25, Pin.IN, Pin.PULL_UP)  # CLK
dt_pin = Pin(26, Pin.IN, Pin.PULL_UP)   # DT
button_pin = Pin(27, Pin.IN, Pin.PULL_UP)  # כפתור על פין 27
 
# ------------------------
# הגדרת חיישן NTC
# ------------------------
adc_pin = 34
adc = ADC(Pin(adc_pin))
adc.width(ADC.WIDTH_10BIT)
adc.atten(ADC.ATTN_11DB)

#R_NOMINAL = 10000
#B_COEFFICIENT = 3950
R_NOMINAL = 7000 # זה מתאים לאמת לא יודע למה
B_COEFFICIENT = 3380 # זה מה שרשום
T_NOMINAL = 25
SERIES_RESISTOR = 10000

# ------------------------
# משתני PID
# ------------------------
Kp = 2.0  # מקדם פרופורציונלי
Ki = 0.1  # מקדם אינטגרלי
Kd = 1.0  # מקדם נגזר
last_error = 0
integral = 0

# --------------------
ds_sensor = ds18x20.DS18X20(onewire.OneWire(machine.Pin(15)))

# ------------------------
# תוכנית PCR
# ------------------------
PCR_STEPS = [
    {"name": "Denaturation", "temp": 95, "time": 15},  # שלב 1
    {"name": "Annealing", "temp": 60, "time": 60},  # שלב 2
    {"name": "Extension", "temp": 72, "time": 15},  # שלב 3
]

CYCLES = 35  # מספר מחזורים

TEMP_TOLERANCE = 0.5  # סבילות טמפרטורה (חצי מעלה)

# ------------------------
# הגדרת מסך OLED
# ------------------------
i2c = I2C(1, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128, 64, i2c)  # גודל מסך: 128x64 פיקסלים

# ------------------------
# פונקציות
# ------------------------

# פונקציה לחישוב ממוצע מתגלגל
def calculate_moving_average(values, new_value, max_size=3):
    values.append(new_value)
    if len(values) > max_size:
        values.pop(0)
    return sum(values) / len(values)

# קריאת טמפרטורה מחיישן NTC
def read_temperature(temp_history):
    
    roms = ds_sensor.scan()

    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        temperature_c = ds_sensor.read_temp(rom)
    return calculate_moving_average(temp_history, temperature_c)    
    '''
    adc_value = adc.read()
    resistance = SERIES_RESISTOR / ((1023 / adc_value) - 1)
    steinhart = resistance / R_NOMINAL
    steinhart = math.log(steinhart)
    steinhart /= B_COEFFICIENT
    steinhart += 1.0 / (T_NOMINAL + 273.15)
    steinhart = 1.0 / steinhart
    temperature_c = steinhart - 273.15
    return calculate_moving_average(temp_history, temperature_c)
    '''
# פונקציית PID לשליטה בפלטייר
def pid_control(setpoint, current_temp):
    global last_error, integral
    
    # חישוב השגיאה
    error = setpoint - current_temp
    integral += error
    derivative = error - last_error
    last_error = error
    
    # חישוב פלט ה-PID
    output = Kp * error + Ki * integral + Kd * derivative
    
    # הגבלת הפלט
    output = max(0, min(PWM_MAX, int(abs(output))))
    return output, error

# שליטה בפלטייר דרך BTS7960
def control_peltier(setpoint, current_temp):
    global last_error, integral
    
    # חישוב השגיאה
    error = setpoint - current_temp
    
    # אם הפער גדול מעשר מעלות הפלטייר יפעל במלוא העוצמה
    if abs(error) > 0.5:
        if error > 0:
            # חימום
            L_PWM.duty(PWM_MAX)
            R_PWM.duty(0)
        elif error < 0:
            # קירור
            L_PWM.duty(0)
            R_PWM.duty(PWM_MAX)
    else:
        # הפעלת PID לכיוונון עדין
        pwm_value, error = pid_control(setpoint, current_temp)
        if error > 0:
            # חימום
            L_PWM.duty(pwm_value)
            R_PWM.duty(0)
        elif error < 0:
            # קירור
            L_PWM.duty(0)
            R_PWM.duty(pwm_value)
        else:
            # טמפרטורה יציבה
            L_PWM.duty(0)
            R_PWM.duty(0)
            
            
# ------------------------
# משתנה לזמן התחלת התוכנית
# ------------------------
start_time_program = time.time()  # שמירת זמן התחלת התוכנית


# עדכון תצוגת המסך
def update_display(cycle, total_cycles, step, total_steps, target_temp, current_temp, step_time, step_name, elapsed_time):
    
    # חישוב הזמן הכולל שחלף
    total_elapsed_time = int(time.time() - start_time_program)
    hours = total_elapsed_time // 3600
    minutes = (total_elapsed_time % 3600) // 60
    seconds = total_elapsed_time % 60

    oled.fill(0)  # נקה מסך
    oled.text(f"Cycle: {cycle}/{total_cycles}", 0, 0)
    oled.text(f"Step: {step_name}", 0, 9)
    oled.text(f"Target: {target_temp}C", 0, 20)
    oled.text(f"Current: {current_temp:.2f}C", 0, 30)
    oled.text(f"Time: {elapsed_time}/{step_time}s", 0, 40)
    oled.text(f"Total: {hours:02}:{minutes:02}:{seconds:02}", 0, 49)  # הצגת זמן כולל
    oled.show()

# ------------------------
# לולאה ראשית
# ------------------------
for cycle in range(CYCLES):
    for step, params in enumerate(PCR_STEPS, start=1):
        target_temp = params["temp"]
        step_time = params["time"]
        step_name = params["name"]
        start_time = None  # זמן תחילת השלב
        last_display_update = 0  # זמן עדכון אחרון של המסך
        temp_history = []  # היסטוריית טמפרטורות לממוצע מתגלגל

        while start_time is None or (time.time() - start_time < step_time):
            current_temp = read_temperature(temp_history)
            control_peltier(target_temp, current_temp)

            # בדיקה אם הגענו לטמפרטורת היעד
            if start_time is None and abs(current_temp - target_temp) <= TEMP_TOLERANCE:
                start_time = time.time()  # התחל למדוד את זמן השלב

            # עדכון המסך פעם בשנייה בלבד
            elapsed_time = int(time.time() - start_time) if start_time else 0
            if time.time() - last_display_update >= 1:
                update_display(cycle + 1, CYCLES, step, len(PCR_STEPS), target_temp, current_temp, step_time, step_name, elapsed_time)
                last_display_update = time.time()

            time.sleep(0.1)  # המתנה קצרה לעדכון

# כיבוי BTS7960 בסיום
R_PWM.duty(0)
L_PWM.duty(0)
oled.fill(0)
oled.text("PCR Complete", 0, 20)
oled.show()
print("PCR Complete")




# In[ ]:


# ניסיון קוד חדש בלי PID אלא עם בקרה על זמן החימום והקירור עדיין בוסר
# חשוב לעשות אפשרות לבדוק האם הטמפרטורה עולה כעת או יורדת כי אם הטמפרטורה עולה אין טעם להפעיל את החימום וכן להיפך.

from machine import Pin, PWM, ADC, I2C
import onewire, ds18x20, time, math, machine
from ssd1306 import SSD1306_I2C




# הפונקציה לביצוע פעולה מסוימת למשך פרק זמן
def perform_action_for_duration(action, stop_action, duration_ms):
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
        action()  # ביצוע הפעולה
    stop_action()  # עצירת הפעולה

# ------------------------
# הגדרות בסיסיות
# ------------------------
PWM_MAX = 1023  # ערך מקסימלי של PWM אם רוצים כמו 5 וולט אז צריך 426

PWM_FREQ = 5000  # תדר ה-PWM



# ------------------------
# הגדרת פינים ל-BTS7960
# ------------------------
R_EN = Pin(15, Pin.OUT)  # אפשר קירור
R_PWM = PWM(Pin(18))
L_EN = Pin(23, Pin.OUT)  # אפשר חימום
L_PWM = PWM(Pin(19))

R_PWM.freq(PWM_FREQ)
L_PWM.freq(PWM_FREQ)

R_EN.value(1)  # אפשר קירור
L_EN.value(1)  # אפשר חימום


# ------------------------
# הגדרת הפינים של הרוטרי אנקודר
# ------------------------
clk_pin = Pin(25, Pin.IN, Pin.PULL_UP)  # CLK
dt_pin = Pin(26, Pin.IN, Pin.PULL_UP)   # DT
button_pin = Pin(27, Pin.IN, Pin.PULL_UP)  # כפתור על פין 27
 
# ------------------------
# הגדרת חיישן NTC
# ------------------------
adc_pin = 34
adc = ADC(Pin(adc_pin))
adc.width(ADC.WIDTH_10BIT)
adc.atten(ADC.ATTN_11DB)

#R_NOMINAL = 10000
#B_COEFFICIENT = 3950
R_NOMINAL = 7000 # זה מתאים לאמת לא יודע למה
B_COEFFICIENT = 3380 # זה מה שרשום
T_NOMINAL = 25
SERIES_RESISTOR = 10000

# ------------------------
# משתני PID
# ------------------------
Kp = 2.0  # מקדם פרופורציונלי
Ki = 0.1  # מקדם אינטגרלי
Kd = 1.0  # מקדם נגזר
last_error = 0
integral = 0

# --------------------
ds_sensor = ds18x20.DS18X20(onewire.OneWire(machine.Pin(15)))

# ------------------------
# תוכנית PCR
# ------------------------
PCR_STEPS = [
    {"name": "Denaturation", "temp": 95, "time": 20},  # שלב 1
    {"name": "Annealing", "temp": 60, "time": 60},  # שלב 2
    {"name": "Extension", "temp": 72, "time": 20},  # שלב 3
]

CYCLES = 35  # מספר מחזורים

TEMP_TOLERANCE = 0.5  # סבילות טמפרטורה (חצי מעלה)

# ------------------------
# הגדרת מסך OLED
# ------------------------
i2c = I2C(1, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128, 64, i2c)  # גודל מסך: 128x64 פיקסלים

# ------------------------
# פונקציות
# ------------------------

# פונקציה לחישוב ממוצע מתגלגל
def calculate_moving_average(values, new_value, max_size=3):
    values.append(new_value)
    if len(values) > max_size:
        values.pop(0)
    return sum(values) / len(values)

# קריאת טמפרטורה מחיישן NTC
def read_temperature(temp_history):
    
    roms = ds_sensor.scan()

    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        temperature_c = ds_sensor.read_temp(rom)
    return calculate_moving_average(temp_history, temperature_c)    
    '''
    adc_value = adc.read()
    resistance = SERIES_RESISTOR / ((1023 / adc_value) - 1)
    steinhart = resistance / R_NOMINAL
    steinhart = math.log(steinhart)
    steinhart /= B_COEFFICIENT
    steinhart += 1.0 / (T_NOMINAL + 273.15)
    steinhart = 1.0 / steinhart
    temperature_c = steinhart - 273.15
    return calculate_moving_average(temp_history, temperature_c)
'''



# פונקציית PID לשליטה בפלטייר
def pid_control(setpoint, current_temp):
    global last_error, integral
    
    # חישוב השגיאה
    error = setpoint - current_temp
    integral += error
    derivative = error - last_error
    last_error = error
    
    # חישוב פלט ה-PID
    output = Kp * error + Ki * integral + Kd * derivative
    
    # הגבלת הפלט
    output = max(0, min(PWM_MAX, int(abs(output))))
    return output, error



#-----------
target_temp = 95  # הטמפרטורה הרצויה
temp_tolerance = 0.5  # סטייה מותרת
heater_on_time = 500  # זמן הפעלה (במילישניות)
heater_off_time = 200  # זמן השהייה (במילישניות)
fan_on_time = 500  # זמן הפעלה (במילישניות)
fan_off_time = 200  # זמן השהייה (במילישניות)


# שליטה בפלטייר דרך BTS7960
def control_peltier(setpoint, current_temp):
    global last_error, integral
    
    # חישוב השגיאה
    error = setpoint - current_temp
    
    # אם הפער גדול מעשר מעלות הפלטייר יפעל במלוא העוצמה
    if abs(error) > 8:
        if error > 0:
            # חימום
            L_PWM.duty(PWM_MAX)
            R_PWM.duty(0)
            
        elif error < 0:
            # קירור
            L_PWM.duty(0)
            R_PWM.duty(PWM_MAX)
            
    elif abs(error) < 8 and abs(error) > 0.5:
        if error > 0:
            # חימום
            L_PWM.duty(0)
            R_PWM.duty(0)
            #L_EN.value(1)  # אפשר חימום
            #R_EN.value(0)  # ביטול קירור
            #time.sleep(0.5)  # המתנה קצרה לעדכון
            #L_PWM.duty(0)
            
        elif error < 0:
            # קירור
            L_PWM.duty(0)
            R_PWM.duty(int(PWM_MAX / 2))
            #L_EN.value(0)  # ביטול חימום
            #R_EN.value(1)  # אפשר קירור
            time.sleep(0.5)  # המתנה קצרה לעדכון
            R_PWM.duty(0)
    
    else:
        L_PWM.duty(0)
        R_PWM.duty(0)
    
    '''
    else:
        # הפעלת PID לכיוונון עדין
        pwm_value, error = pid_control(setpoint, current_temp)
        if error > 0:
            # חימום
            L_PWM.duty(pwm_value)
            R_PWM.duty(0)
        elif error < 0:
            # קירור
            L_PWM.duty(0)
            R_PWM.duty(pwm_value)
        else:
            # טמפרטורה יציבה
            L_PWM.duty(0)
            R_PWM.duty(0)
       '''     
            
# ------------------------
# משתנה לזמן התחלת התוכנית
# ------------------------
start_time_program = time.time()  # שמירת זמן התחלת התוכנית


# עדכון תצוגת המסך
def update_display(cycle, total_cycles, step, total_steps, target_temp, current_temp, step_time, step_name, elapsed_time):
    
    # חישוב הזמן הכולל שחלף
    total_elapsed_time = int(time.time() - start_time_program)
    hours = total_elapsed_time // 3600
    minutes = (total_elapsed_time % 3600) // 60
    seconds = total_elapsed_time % 60

    oled.fill(0)  # נקה מסך
    oled.text(f"Cycle: {cycle}/{total_cycles}", 0, 0)
    oled.text(f"Step: {step_name}", 0, 9)
    oled.text(f"Target: {target_temp}C", 0, 20)
    oled.text(f"Current: {current_temp:.2f}C", 0, 30)
    oled.text(f"Time: {elapsed_time}/{step_time}s", 0, 40)
    oled.text(f"Total: {hours:02}:{minutes:02}:{seconds:02}", 0, 49)  # הצגת זמן כולל
    oled.show()

# ------------------------
# לולאה ראשית
# ------------------------
for cycle in range(CYCLES):
    for step, params in enumerate(PCR_STEPS, start=1):
        target_temp = params["temp"]
        step_time = params["time"]
        step_name = params["name"]
        start_time = None  # זמן תחילת השלב
        last_display_update = 0  # זמן עדכון אחרון של המסך
        temp_history = []  # היסטוריית טמפרטורות לממוצע מתגלגל

        while start_time is None or (time.time() - start_time < step_time):
            current_temp = read_temperature(temp_history)
            control_peltier(target_temp, current_temp)

            # בדיקה אם הגענו לטמפרטורת היעד
            if start_time is None and abs(current_temp - target_temp) <= TEMP_TOLERANCE:
                start_time = time.time()  # התחל למדוד את זמן השלב

            # עדכון המסך פעם בשנייה בלבד
            elapsed_time = int(time.time() - start_time) if start_time else 0
            if time.time() - last_display_update >= 1:
                update_display(cycle + 1, CYCLES, step, len(PCR_STEPS), target_temp, current_temp, step_time, step_name, elapsed_time)
                last_display_update = time.time()

            time.sleep(0.1)  # המתנה קצרה לעדכון

# כיבוי BTS7960 בסיום
R_PWM.duty(0)
L_PWM.duty(0)
oled.fill(0)
oled.text("PCR Complete", 0, 20)
oled.show()
print("PCR Complete")




# In[ ]:





# In[ ]:


# קוד מקורי ממומר מפוקט פי-סי אר תוך התאמות קלות של הפינים וכדומה

from machine import Pin, ADC, PWM, I2C
from time import sleep, ticks_ms
import math
import ssd1306

# Constants
VERSION_STRING = "V1.02 2020"
NTC_B = 3435
NTC_TN = 298.15
NTC_RN = 10000
NTC_R0 = 4.7
TEMPERATURE_TOLERANCE = 0.5

PID_P = 0.5
PID_I = 0.0001
PID_D = 0.15

# Pins and peripherals
analog_in_pin = ADC(Pin(34))  # ADC for temperature sensor
fan_pin = Pin(2, Pin.OUT)     # Fan pin
heater_pin = Pin(3, Pin.OUT)  # Heater pin
button_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # Button pin

# PWM setup
heater_pwm = PWM(heater_pin)
fan_pwm = PWM(fan_pin)
heater_pwm.freq(1000)
fan_pwm.freq(1000)

# I2C for OLED
i2c = I2C(1, scl=Pin(22), sda=Pin(21))
oled_width, oled_height = 128, 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Global variables
temperature = 0.0
temperature_mean = 0.0
TEMP_set = 0.0
TEMP_control = 0.0
TEMP_i = 0.0
TEMP_d = 0.0
TEMP_dif = 0.0
TEMP_click = 0
TIME_click = 0
TIME_control = 0

heat_power = 0
fan_power = 0
menu_item = 0
PCR_cycle = 1
PID_integration = False
current_state = "Main"
PCR_state = "Set"

# EEPROM Simulation (replace with real implementation if needed)
eeprom_settings = {
    "init_temp": 94, 
    "denature_time": 60,
    "denature_temp": 94,
    "annealing_time": 120,
    "annealing_temp": 55,
    "extension_time": 80,
    "extension_temp": 72,
    "final_time": 40,
    "final_temp": 25,
    "cycles": 20
}

# Functions
def calculate_temperature(sensor_value):
    """Calculate temperature from sensor ADC value."""
    sensor_voltage = 3.3 * sensor_value / 65535  # Assuming 16-bit ADC
    sensor_resistance = (sensor_voltage * NTC_R0) / (3.3 - sensor_voltage)
    temperature = 1 / (math.log(sensor_resistance * 1000 / NTC_RN) / NTC_B + 1 / NTC_TN) - 273.15
    return temperature

def run_pid():
    """Run PID control algorithm."""
    global TEMP_control, TEMP_i, TEMP_d, TEMP_dif
    TEMP_dif = TEMP_set - temperature_mean
    TEMP_i += TEMP_dif
    TEMP_d = TEMP_dif
    TEMP_control = PID_P * TEMP_dif + PID_D * TEMP_d + (int(PID_integration) * PID_I * TEMP_i)
    set_heater(temperature_mean, TEMP_control)

def set_heater(temperature, power):
    """Control heater and fan power."""
    global heat_power, fan_power
    if power > 0:
        heat_power = min(max(int(power), 0), 255)
        heater_pwm.duty_u16(int(heat_power * 65535 / 255))
        fan_pwm.duty_u16(0)
    elif power < 0:
        fan_power = min(max(int(-power), 0), 255)
        fan_pwm.duty_u16(int(fan_power * 65535 / 255))
        heater_pwm.duty_u16(0)
    else:
        heater_pwm.duty_u16(0)
        fan_pwm.duty_u16(0)

def draw_main_menu():
    """Draw the main menu on OLED."""
    oled.fill(0)
    oled.text("PocketPCR", 0, 0)
    if menu_item == 0:
        oled.fill_rect(0, 20, 128, 20, 1)
        oled.text("Run PCR", 10, 25, 0)
        oled.text("Setup", 10, 45, 1)
    else:
        oled.text("Run PCR", 10, 25, 1)
        oled.fill_rect(0, 40, 128, 20, 1)
        oled.text("Setup", 10, 45, 0)
    oled.show()

def draw_run_display():
    """Draw the PCR running screen."""
    oled.fill(0)
    oled.text("PCR Running", 0, 0)
    oled.text(f"Temp: {temperature_mean:.1f}C", 0, 20)
    oled.text(f"Set: {TEMP_set}C", 0, 30)
    oled.text(f"Cycle: {PCR_cycle}/{eeprom_settings['cycles']}", 0, 40)
    oled.text(f"Time: {TIME_control}s", 0, 50)
    oled.show()

def main_loop():
    global current_state, PCR_state, menu_item, PCR_cycle, TEMP_set, PID_integration, TEMP_click, TIME_click, TIME_control
    global temperature, temperature_mean
    
    while True:
        # Read sensor value and calculate temperature
        sensor_value = analog_in_pin.read_u16()
        temperature = calculate_temperature(sensor_value)
        temperature_mean = (temperature_mean * 3 + temperature) / 4

        # Handle state
        if current_state == "Main":
            draw_main_menu()
            if not button_pin.value():
                sleep(0.2)  # Debounce
                if menu_item == 0:
                    current_state = "Run"
                    PCR_state = "Set"
                    PCR_cycle = 1
                else:
                    current_state = "Setup"
            if menu_item == 0:
                menu_item = 1
            else:
                menu_item = 0

        elif current_state == "Run":
            if PCR_state == "Set":
                TEMP_set = eeprom_settings["denature_temp"]
                TIME_control = eeprom_settings["denature_time"]
                PID_integration = False
                PCR_state = "Transition"

            elif PCR_state == "Transition":
                run_pid()
                draw_run_display()
                if abs(TEMP_set - temperature_mean) < TEMPERATURE_TOLERANCE:
                    PID_integration = True
                    TEMP_click = ticks_ms()
                    PCR_state = "Time"

            elif PCR_state == "Time":
                run_pid()
                TIME_control = eeprom_settings["denature_time"] - (ticks_ms() - TEMP_click) / 1000
                draw_run_display()
                if TIME_control <= 0:
                    PCR_cycle += 1
                    if PCR_cycle > eeprom_settings["cycles"]:
                        current_state = "Done"
                    else:
                        PCR_state = "Set"

        elif current_state == "Done":
            set_heater(temperature_mean, 0)
            oled.fill(0)
            oled.text("PCR Done", 30, 30)
            oled.show()
            if not button_pin.value():
                sleep(0.2)  # Debounce
                current_state = "Main"

        sleep(0.1)

# Run the main loop
main_loop()


# In[ ]:


# קוד נסיוני לפיסיאר שלי לפי פוקט פיסיאר

from machine import Pin, PWM, I2C
from time import sleep, ticks_ms
import math, machine, onewire, ds18x20, time
from ssd1306 import SSD1306_I2C



# הגדרת הפינים של הרוטרי אנקודר
clk_pin = Pin(25, Pin.IN, Pin.PULL_UP)  # CLK
dt_pin = Pin(26, Pin.IN, Pin.PULL_UP)   # DT
button_pin = Pin(27, Pin.IN, Pin.PULL_UP)  # Button pin

last_clk_state = clk_pin.value()  # מצב התחלתי של CLK
selected_option = 0  # אופציה שנבחרה בתפריט

def update_selection(options):
    global selected_option, last_clk_state
    clk_state = clk_pin.value()
    dt_state = dt_pin.value()

    # אם מצב ה-CLK השתנה
    if clk_state != last_clk_state:
        if dt_state != clk_state:
            selected_option = (selected_option + 1) % len(options)  # סיבוב קדימה
        else:
            selected_option = (selected_option - 1) % len(options)  # סיבוב אחורה

    last_clk_state = clk_state
    
def display_options(options, title=""):
    """Display options on OLED with optional title."""
    oled.fill(0)
    if title:
        oled.text(title, 0, 0)  # מציג כותרת אם קיימת
    for i, option in enumerate(options):
        prefix = ">" if i == selected_option else " "  # סימון הבחירה הנוכחית
        oled.text(f"{prefix} {option}", 0, 20 + i * 10)
    oled.show()

menu_options = ["Run PCR", "Setup"]  # רשימת אפשרויות התפריט





# Constants
VERSION_STRING = "V1.02 2020"

ds_sensor = ds18x20.DS18X20(onewire.OneWire(machine.Pin(15)))

TEMPERATURE_TOLERANCE = 0.5

PID_P = 0.5
PID_I = 0.0001
PID_D = 0.15

# ------------------------
# הגדרת פינים ל-BTS7960
# ------------------------
R_EN = Pin(15, Pin.OUT)  # אפשר קירור
R_PWM = PWM(Pin(18))
L_EN = Pin(23, Pin.OUT)  # אפשר חימום
L_PWM = PWM(Pin(19))

R_EN.value(1)  # אפשר קירור
L_EN.value(1)  # אפשר חימום


# Pins and peripherals
fan_pin = R_EN     # Fan pin
heater_pin = L_EN  # Heater pin



# PWM setup
heater_pwm = R_PWM
fan_pwm = L_PWM
heater_pwm.freq(1000)
fan_pwm.freq(1000)



# I2C for OLED
i2c = I2C(1, scl=Pin(22), sda=Pin(21))
oled_width, oled_height = 128, 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Global variables
temperature = 0.0
temperature_mean = 0.0
TEMP_set = 0.0
TEMP_control = 0.0
TEMP_i = 0.0
TEMP_d = 0.0
TEMP_dif = 0.0
TEMP_click = 0
TIME_click = 0
TIME_control = 0

heat_power = 0
fan_power = 0
menu_item = 0
PCR_cycle = 1
PID_integration = False
current_state = "Run" #"Main" צריך להיות מיין כדי להתחיל בחירה במסך
PCR_state = "Set"

# EEPROM Simulation (replace with real implementation if needed)
eeprom_settings = {
    "init_temp": 95, 
    "denature_time": 20,
    "denature_temp": 95,
    "annealing_time": 20,
    "annealing_temp": 60,
    "extension_time": 60,
    "extension_temp": 72,
    "final_time": 20,
    "final_temp": 30,
    "cycles": 35
}

# Functions
def calculate_temperature():
    """Calculate temperature from sensor."""
    roms = ds_sensor.scan()
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        temperature = ds_sensor.read_temp(rom)
    return temperature

def run_pid():
    """Run PID control algorithm."""
    global TEMP_control, TEMP_i, TEMP_d, TEMP_dif
    TEMP_dif = TEMP_set - temperature_mean
    TEMP_i += TEMP_dif
    TEMP_d = TEMP_dif
    TEMP_control = PID_P * TEMP_dif + PID_D * TEMP_d + (int(PID_integration) * PID_I * TEMP_i)
    set_heater(temperature_mean, TEMP_control)

def set_heater(temperature, power):
    """Control heater and fan power."""
    global heat_power, fan_power
    if power > 0:
        heat_power = min(max(int(power), 0), 255)
        heater_pwm.duty_u16(int(heat_power * 65535 / 255))
        fan_pwm.duty_u16(0)
    elif power < 0:
        fan_power = min(max(int(-power), 0), 255)
        fan_pwm.duty_u16(int(fan_power * 65535 / 255))
        heater_pwm.duty_u16(0)
    else:
        heater_pwm.duty_u16(0)
        fan_pwm.duty_u16(0)

def draw_main_menu():
    """Draw the main menu using display_options."""
    display_options(menu_options, title="PocketPCR")

def draw_run_display():
    """Draw the PCR running screen."""
    oled.fill(0)
    oled.text("PCR Running", 0, 0)
    oled.text(f"Temp: {temperature_mean:.1f}C", 0, 20)
    oled.text(f"Set: {TEMP_set}C", 0, 30)
    oled.text(f"Cycle: {PCR_cycle}/{eeprom_settings['cycles']}", 0, 40)
    oled.text(f"Time: {TIME_control}s", 0, 50)
    oled.show()

def main_loop():
    global current_state, PCR_state, menu_item, PCR_cycle, TEMP_set, PID_integration, TEMP_click, TIME_click, TIME_control
    global temperature, temperature_mean
    
    while True:
        # Read sensor value and calculate temperature
        temperature = calculate_temperature()
        temperature_mean = (temperature_mean * 3 + temperature) / 4

        # Handle state
        if current_state == "Main":
            draw_main_menu()
            if not button_pin.value():
                sleep(0.2)  # Debounce
                if menu_item == 0:
                    current_state = "Run"
                    PCR_state = "Set"
                    PCR_cycle = 1
                else:
                    current_state = "Setup"
            if menu_item == 0:
                menu_item = 1
            else:
                menu_item = 0

        elif current_state == "Run":
            if PCR_state == "Set":
                TEMP_set = eeprom_settings["denature_temp"]
                TIME_control = eeprom_settings["denature_time"]
                PID_integration = False
                PCR_state = "Transition"

            elif PCR_state == "Transition":
                run_pid()
                draw_run_display()
                if abs(TEMP_set - temperature_mean) < TEMPERATURE_TOLERANCE:
                    PID_integration = True
                    TEMP_click = ticks_ms()
                    PCR_state = "Time"

            elif PCR_state == "Time":
                run_pid()
                TIME_control = eeprom_settings["denature_time"] - (ticks_ms() - TEMP_click) / 1000
                draw_run_display()
                if TIME_control <= 0:
                    PCR_cycle += 1
                    if PCR_cycle > eeprom_settings["cycles"]:
                        current_state = "Done"
                    else:
                        PCR_state = "Set"

        elif current_state == "Done":
            set_heater(temperature_mean, 0)
            oled.fill(0)
            oled.text("PCR Done", 30, 30)
            oled.show()
            if not button_pin.value():
                sleep(0.2)  # Debounce
                current_state = "Main"

        sleep(0.1)

# Run the main loop
main_loop()



# In[ ]:


# קוד חשוב נורא
# הקוד שלי אבל הפיד של פוקט פיסי אר\


# ניסיון שני לקוד PCR
# עובד קצת יותר טוב ברעיון של להשתמש ב PID רק לצורך כוונון עדין כשמגיעים לאיזור טמפרטורת היעד
# בינתיים זה הקוד היציב שעובד


from machine import Pin, PWM, ADC, I2C
import onewire, ds18x20, time, math, machine
from ssd1306 import SSD1306_I2C

# ------------------------
# הגדרות בסיסיות
# ------------------------
PWM_MAX = 1023  # ערך מקסימלי של PWM אם רוצים כמו 5 וולט אז צריך 426

PWM_FREQ = 5000  # תדר ה-PWM



# ------------------------
# הגדרת פינים ל-BTS7960
# ------------------------
R_EN = Pin(15, Pin.OUT)  # אפשר קירור
R_PWM = PWM(Pin(18))
L_EN = Pin(23, Pin.OUT)  # אפשר חימום
L_PWM = PWM(Pin(19))

R_PWM.freq(PWM_FREQ)
L_PWM.freq(PWM_FREQ)

R_EN.value(1)  # אפשר קירור
L_EN.value(1)  # אפשר חימום


# ------------------------
# הגדרת הפינים של הרוטרי אנקודר
# ------------------------
clk_pin = Pin(25, Pin.IN, Pin.PULL_UP)  # CLK
dt_pin = Pin(26, Pin.IN, Pin.PULL_UP)   # DT
button_pin = Pin(27, Pin.IN, Pin.PULL_UP)  # כפתור על פין 27
 
# ------------------------
# הגדרת חיישן NTC
# ------------------------
adc_pin = 34
adc = ADC(Pin(adc_pin))
adc.width(ADC.WIDTH_10BIT)
adc.atten(ADC.ATTN_11DB)

#R_NOMINAL = 10000
#B_COEFFICIENT = 3950
R_NOMINAL = 7000 # זה מתאים לאמת לא יודע למה
B_COEFFICIENT = 3380 # זה מה שרשום
T_NOMINAL = 25
SERIES_RESISTOR = 10000

# ------------------------
# משתני PID
# ------------------------
Kp = 2.0  # מקדם פרופורציונלי
Ki = 0.1  # מקדם אינטגרלי
Kd = 1.0  # מקדם נגזר
last_error = 0
integral = 0

# --------------------
ds_sensor = ds18x20.DS18X20(onewire.OneWire(machine.Pin(15)))

# ------------------------
# תוכנית PCR
# ------------------------
PCR_STEPS = [
    {"name": "Denaturation", "temp": 38, "time": 20},  # שלב 1
    {"name": "Annealing", "temp": 30, "time": 20},  # שלב 2
    {"name": "Extension", "temp": 35, "time": 20},  # שלב 3
]

CYCLES = 35  # מספר מחזורים

TEMPERATURE_TOLERANCE = 0.5

PID_P = 0.5
PID_I = 0.0001
PID_D = 0.15

temperature = 0.0
temperature_mean = 0.0
TEMP_set = 0.0
TEMP_control = 0.0
TEMP_i = 0.0
TEMP_d = 0.0
TEMP_dif = 0.0
TEMP_click = 0
TIME_click = 0
TIME_control = 0

PID_integration = True

# ------------------------
# הגדרת מסך OLED
# ------------------------
i2c = I2C(1, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128, 64, i2c)  # גודל מסך: 128x64 פיקסלים

# ------------------------
# פונקציות
# ------------------------

# פונקציה לחישוב ממוצע מתגלגל
def calculate_moving_average(values, new_value, max_size=3):
    values.append(new_value)
    if len(values) > max_size:
        values.pop(0)
    return sum(values) / len(values)

# קריאת טמפרטורה מחיישן NTC
def read_temperature(temp_history):
    
    roms = ds_sensor.scan()

    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        temperature_c = ds_sensor.read_temp(rom)
    return calculate_moving_average(temp_history, temperature_c)    
    '''
    adc_value = adc.read()
    resistance = SERIES_RESISTOR / ((1023 / adc_value) - 1)
    steinhart = resistance / R_NOMINAL
    steinhart = math.log(steinhart)
    steinhart /= B_COEFFICIENT
    steinhart += 1.0 / (T_NOMINAL + 273.15)
    steinhart = 1.0 / steinhart
    temperature_c = steinhart - 273.15
    return calculate_moving_average(temp_history, temperature_c)
'''

def run_pid():
    """Run PID control algorithm."""
    global TEMP_control, TEMP_i, TEMP_d, TEMP_dif
    TEMP_dif = TEMP_set - temperature_mean
    TEMP_i += TEMP_dif
    TEMP_d = TEMP_dif
    TEMP_control = PID_P * TEMP_dif + PID_D * TEMP_d + (int(PID_integration) * PID_I * TEMP_i)
    control_peltier(temperature_mean, TEMP_control)


def control_peltier(temperature, power):
    """Control heater and fan power."""
    global heat_power, fan_power
    if power > 0:
        heat_power = min(max(int(power), 0), 255)
        L_PWM.duty_u16(int(heat_power * 65535 / 255))
        R_PWM.duty_u16(0)
        print(power)
        print(int(heat_power * 65535 / 255))
    elif power < 0:
        fan_power = min(max(int(-power), 0), 255)
        R_PWM.duty_u16(int(fan_power * 65535 / 255))
        L_PWM.duty_u16(0)
    else:
        R_PWM.duty_u16(0)
        L_PWM.duty_u16(0)
'''
def control_peltier(temperature, power):
    """Control heater and fan power."""
    global heat_power, fan_power
    if power > 0:
        # חימום
        heat_power = min(max(int(power), 0), 1023)  # PWM בין 0 ל-1023
        L_PWM.duty(heat_power)  # חיבור PWM לפין החימום
        R_PWM.duty(0)  # כיבוי קירור
        print(power)
        print(heat_power)
    elif power < 0:
        # קירור
        fan_power = min(max(int(-power), 0), 1023)  # PWM בין 0 ל-1023
        R_PWM.duty(fan_power)  # חיבור PWM לפין הקירור
        L_PWM.duty(0)  # כיבוי חימום
    else:
        # כיבוי
        R_PWM.duty(0)
        L_PWM.duty(0)
'''

    
# ------------------------
# משתנה לזמן התחלת התוכנית
# ------------------------
start_time_program = time.time()  # שמירת זמן התחלת התוכנית


# עדכון תצוגת המסך
def update_display(cycle, total_cycles, step, total_steps, target_temp, current_temp, step_time, step_name, elapsed_time):
    
    # חישוב הזמן הכולל שחלף
    total_elapsed_time = int(time.time() - start_time_program)
    hours = total_elapsed_time // 3600
    minutes = (total_elapsed_time % 3600) // 60
    seconds = total_elapsed_time % 60

    oled.fill(0)  # נקה מסך
    oled.text(f"Cycle: {cycle}/{total_cycles}", 0, 0)
    oled.text(f"Step: {step_name}", 0, 9)
    oled.text(f"Target: {target_temp}C", 0, 20)
    oled.text(f"Current: {current_temp:.2f}C", 0, 30)
    oled.text(f"Time: {elapsed_time}/{step_time}s", 0, 40)
    #oled.text(f"Total: {hours:02}:{minutes:02}:{seconds:02}", 0, 49)  # הצגת זמן כולל
    oled.text(f"power: {TEMP_control}", 0, 49)
    oled.show()

# ------------------------
# לולאה ראשית
# ------------------------
for cycle in range(CYCLES):
    for step, params in enumerate(PCR_STEPS, start=1):
        target_temp = params["temp"]
        step_time = params["time"]
        step_name = params["name"]
        start_time = None  # זמן תחילת השלב
        last_display_update = 0  # זמן עדכון אחרון של המסך
        temp_history = []  # היסטוריית טמפרטורות לממוצע מתגלגל
        
        TEMP_set = target_temp ######
        
        while start_time is None or (time.time() - start_time < step_time):
            current_temp = read_temperature(temp_history)
            temperature_mean = (temperature_mean * 3 + temperature) / 4
            run_pid()

            # בדיקה אם הגענו לטמפרטורת היעד
            if start_time is None and abs(current_temp - target_temp) <= TEMPERATURE_TOLERANCE:
                start_time = time.time()  # התחל למדוד את זמן השלב

            # עדכון המסך פעם בשנייה בלבד
            elapsed_time = int(time.time() - start_time) if start_time else 0
            if time.time() - last_display_update >= 1:
                update_display(cycle + 1, CYCLES, step, len(PCR_STEPS), target_temp, current_temp, step_time, step_name, elapsed_time)
                last_display_update = time.time()

            time.sleep(0.1)  # המתנה קצרה לעדכון

# כיבוי BTS7960 בסיום
R_PWM.duty(0)
L_PWM.duty(0)
oled.fill(0)
oled.text("PCR Complete", 0, 20)
oled.show()
print("PCR Complete")




# In[ ]:


# הצגת שלום עולם על מסך OLED
from machine import Pin, I2C
import ssd1306


# ESP32 Pin assignment 
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.text('Hello, Wokwi!', 10, 10)      
oled.show()


# In[23]:





# In[39]:





# In[ ]:





# In[ ]:





# In[18]:





# In[2]:





# In[1]:


# חשוב ביותר!!!! עדכון השעון של רכיב שעון נלווה. צריך לעשות רק בפעם הראשונה או אם יש קצר בשעון

#https://github.com/pangopi/micropython-DS3231-AT24C32/blob/main/ds3231.py

from machine import I2C, Pin
from ds3231 import DS3231  # הנח שהדרייבר שלך נמצא בשם ds3231.py
import machine

rtc = machine.RTC()

# יצירת אובייקט I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # ודא שאתה משתמש בפינים המתאימים

# יצירת אובייקט של DS3231
ds = DS3231(i2c)

# הגדרת הזמן החדש (שנה, חודש, יום, יום בשבוע, שעה, דקה, שניה)
# לדוגמה: 2024-11-16 14:30:00, יום חמישי (יום 5 בשבוע)
#new_time = (2024, 11, 16, 20, 40, 30, 6)

# קריאת זמן המערכת של הבקר שזה הזמן המדוייק של המחשב רק כאשר הבקר מחובר למחשב
year, month, day, week_day, hour, minute, second, micro_second = rtc.datetime()

# מוציא את מספר היום בשבוע הנורמלי לפי סדר מתוך שעון המכשיר שמוגדר RTC
def get_normal_weekday(rtc_weekday):
    weekday_dict = {6:1,0:2,1:3,2:4,3:5,4:6,5:7}
    return weekday_dict.get(rtc_weekday)

# חייבים למפות מחדש את סדר הנתונים וצורתם כי כל ספרייה משתמשת בסדר וצורה אחרים קצת
new_time = (year, month, day, hour, minute, second, get_normal_weekday(week_day))


# עדכון הזמן ב-RTC
ds.datetime(new_time)

print("הזמן עודכן בהצלחה!", ds.datetime())



# In[ ]:


# הכי טוב ועדכני לשעון
# https://github.com/pangopi/micropython-DS3231-AT24C32/blob/main/ds3231.py

import machine
import time
from ds3231 import DS3231

# יצירת אובייקט I2C (בהנחה שהשימוש בפינים 21 ו-22)
i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21))

# פונקציה לקרוא את הזמן מ-DS3231 ולעדכן את ה-machine.RTC()
def sync_rtc_with_ds3231():
    try:
        
        # יצירת אובייקט RTC במערכת (machine RTC)
        rtc_system = machine.RTC()
 
        # יצירת אובייקט DS3231
        rtc_ds3231 = DS3231(i2c)

        # קריאת הזמן מ-DS3231
        ds3231_time = rtc_ds3231.datetime()

        # עדכון ה-machine RTC עם הזמן שנקרא מ-DS3231
        rtc_system.datetime(ds3231_time)
        print("Time synced with DS3231: ", ds3231_time)

    except Exception as e:
        print("Error reading from DS3231: ", e)
        # במקרה של שגיאה, נגדיר זמן ידני ב-machine.RTC()
        manual_time = (2005, 12, 30, get_rtc_weekday(7), 22, 50, 30, 0)  # (שנה, חודש, יום, יום בשבוע, שעה, דקות, שניות, תת-שניות)
        rtc_system.datetime(manual_time)
        print("Time set manually in machine.RTC: ", manual_time)

# קריאה לפונקציה
sync_rtc_with_ds3231()

# הצגת הזמן ב-machine.RTC
print("Current time in machine.RTC: ", rtc_system.datetime())



# In[ ]:


# חיישן טמפרטורה לחות ולחץ שעובד בסיסי BME280
from machine import Pin, I2C
import ssd1306
import bme280 as BME280
from time import sleep

# Initialize I2C for both OLED and BME280
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=10000)

# Initialize OLED display
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Initialize BME280 sensor
bme = BME280.BME280(i2c=i2c)

while True:
    # Read BME280 sensor values
    temp = bme.temperature
    hum = bme.humidity
    pres = bme.pressure

    # Clear the OLED screen
    oled.fill(0)

    # Display the sensor readings on the OLED
    oled.text('Temp: {}'.format(temp), 0, 0)
    oled.text('Humidity: {}'.format(hum), 0, 20)
    oled.text('Pressure: {}'.format(pres), 0, 40)

    # Update the display
    oled.show()

    # Wait before updating again
    sleep(5)


# In[1]:





# In[ ]:





# In[3]:


### קוד לכפתור סיבובי שלא דורש ספריות אבל יש בו בעיה שהוא מחזיר שני ערכים בכל פעם
# ייתכן שהבעיה נגרמת בגלל בעייה ברוטרי אנקודר שלי או בגלל הדרך של הטיפול ב ESP32 
# בכל מקרה הבעייה נגרמת בגלל שפיזית כל חצי קליק נספר כקליק שלם ולכן קליק אחד הוא בעצם שני קליקים 

from machine import Pin
import time

# הגדרת הפינים של הרוטרי אנקודר
clk_pin = Pin(25, Pin.IN, Pin.PULL_UP)  # CLK
dt_pin = Pin(26, Pin.IN, Pin.PULL_UP)   # DT

# הגדרת משתנים
counter = 0
last_clk_state = clk_pin.value()

def rotary_callback(pin):
    global counter, last_clk_state
    clk_state = clk_pin.value()
    dt_state = dt_pin.value()

    # אם הקלאק השתנה אז בודקים את כיוון הסיבוב
    if clk_state != last_clk_state:
        if dt_state != clk_state:
            counter += 1  # סיבוב לפי כיוון אחד
        else:
            counter -= 1  # סיבוב לפי כיוון הפוך
        print(f"Value: {counter}")

    last_clk_state = clk_state

# הגדרת טריגר להפעלת פונקציית callback
clk_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=rotary_callback)


    
# הקוד הנל משופץ כך שיספור כל שני סיבובים כסיבוב אחד
# גם נוסף בו כפתור

from machine import Pin
import time

# הגדרת הפינים של הרוטרי אנקודר
clk_pin = Pin(25, Pin.IN, Pin.PULL_UP)  # CLK
dt_pin = Pin(26, Pin.IN, Pin.PULL_UP)   # DT
button_pin = Pin(27, Pin.IN, Pin.PULL_UP)  # כפתור על פין 27

# הגדרת משתנים
counter = 0
change_count = 0  # משתנה לספירת השינויים
last_clk_state = clk_pin.value()  # משתנה לדעת מה המצב ההתחלתי של clk

def rotary_callback(pin):
    global counter, last_clk_state, change_count
    clk_state = clk_pin.value()
    dt_state = dt_pin.value()

    # אם הקלאק השתנה
    if clk_state != last_clk_state:
        change_count += 1  # מעדכנים את ספירת השינויים

        # רק לאחר שני שינויים נבצע את הספירה
        if change_count == 2:
            if dt_state != clk_state:
                counter += 1  # סיבוב לפי כיוון אחד
            else:
                counter -= 1  # סיבוב לפי כיוון הפוך

            # אפס את ספירת השינויים אחרי כל שני שינויים
            change_count = 0
            print(f"Value: {counter}")

    last_clk_state = clk_state

def button_callback(pin):
    # מדפיס את הערך של counter כאשר הכפתור נלחץ
    if pin.value() == 0:  # אם הכפתור לחוץ (נמצאה ערך LOW)
        print(f"Button pressed! Current counter value: {counter}")
        time.sleep(0.2)  # השהייה קצרה כדי להימנע מכפילות בלחיצה על הכפתור

# הגדרת טריגר להפעלת פונקציית callback רק כאשר יש שינוי במצב הקלאק
clk_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=rotary_callback)

# הגדרת טריגר להפעלת פונקציית callback כאשר הכפתור נלחץ
button_pin.irq(trigger=Pin.IRQ_FALLING, handler=button_callback)




# הקוד הנ"ל עם הדפסות למסך במקום למסוף

from machine import Pin, I2C
import time
import ssd1306

# הגדרת ה־I2C עבור מסך OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # החלף את הפינים לפי הצורך
oled = ssd1306.SSD1306_I2C(128, 64, i2c)  # גודל המסך הוא 128x64 פיקסלים

# הגדרת הפינים של הרוטרי אנקודר
clk_pin = Pin(25, Pin.IN, Pin.PULL_UP)  # CLK
dt_pin = Pin(26, Pin.IN, Pin.PULL_UP)   # DT
button_pin = Pin(27, Pin.IN, Pin.PULL_UP)  # כפתור על פין 27

# הגדרת משתנים
counter = 0
change_count = 0  # משתנה לספירת השינויים
last_clk_state = clk_pin.value()  # משתנה לדעת מה המצב ההתחלתי של clk

def rotary_callback(pin):
    global counter, last_clk_state, change_count
    clk_state = clk_pin.value()
    dt_state = dt_pin.value()

    # אם הקלאק השתנה
    if clk_state != last_clk_state:
        change_count += 1  # מעדכנים את ספירת השינויים

        # רק לאחר שני שינויים נבצע את הספירה
        if change_count == 2:
            if dt_state != clk_state:
                counter += 1  # סיבוב לפי כיוון אחד
            else:
                counter -= 1  # סיבוב לפי כיוון הפוך

            # אפס את ספירת השינויים אחרי כל שני שינויים
            change_count = 0

            # הצגת הערך על המסך
            oled.fill(0)  # ניקוי המסך
            oled.text(f"Value: {counter}", 0, 0)  # הדפסה למיקום (0, 0)
            oled.show()  # הצגת התוכן על המסך

    last_clk_state = clk_state

def button_callback(pin):
    # מדפיס את הערך של counter כאשר הכפתור נלחץ
    if pin.value() == 0:  # אם הכפתור לחוץ (נמצאה ערך LOW)
        oled.fill(0)  # ניקוי המסך
        oled.text(f"Button pressed!", 0, 20)  # הדפסה למיקום (0, 0)
        oled.text(f"Counter: {counter}", 0, 30)  # הדפסה למיקום (0, 10)
        oled.show()  # הצגת התוכן על המסך
        time.sleep(0.2)  # השהייה קצרה כדי להימנע מכפילות בלחיצה על הכפתור

# הצגת הודעה לסובב את האנקודר
oled.fill(0)  # ניקוי המסך
oled.text("rotate encoder", 0, 0)
oled.show()

# הגדרת טריגר להפעלת פונקציית callback רק כאשר יש שינוי במצב הקלאק
clk_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=rotary_callback)

# הגדרת טריגר להפעלת פונקציית callback כאשר הכפתור נלחץ
button_pin.irq(trigger=Pin.IRQ_FALLING, handler=button_callback)



# In[ ]:


# קוד נורא חשוב לתפריט בחירה באמצעות אנקודר

from machine import Pin, I2C
import time
import ssd1306

# הגדרת ה־I2C עבור מסך OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # עדכן את הפינים לפי הצורך
oled = ssd1306.SSD1306_I2C(128, 64, i2c)  # גודל המסך הוא 128x64 פיקסלים

# הגדרת הפינים של הרוטרי אנקודר
clk_pin = Pin(25, Pin.IN, Pin.PULL_UP)  # CLK
dt_pin = Pin(26, Pin.IN, Pin.PULL_UP)   # DT
button_pin = Pin(27, Pin.IN, Pin.PULL_UP)  # כפתור

# משתנים לבחירה
main_options = ["Morning", "Evening"]  # אפשרויות הבחירה הראשיות
exit_options = ["No", "Yes"]  # אפשרויות היציאה
selected_option = 0  # האופציה המתחילה
last_clk_state = clk_pin.value()  # מצב אחרון של CLK

# עדכון הבחירה בהתבסס על מצב הרוטרי אנקודר

change_count = 0  # משתנה לספירת השינויים
last_clk_state = clk_pin.value()  # המצב ההתחלתי של CLK

def update_selection(options):
    global selected_option, change_count, last_clk_state
    clk_state = clk_pin.value()
    dt_state = dt_pin.value()

    # אם מצב ה-CLK השתנה
    if clk_state != last_clk_state:
        change_count += 1  # נחשב את השינויים

        # רק לאחר שני שינויים נבצע עדכון
        if change_count == 2:
            if dt_state != clk_state:
                selected_option = (selected_option + 1) % len(options)  # סיבוב קדימה
            else:
                selected_option = (selected_option - 1) % len(options)  # סיבוב אחורה

            change_count = 0  # אפס את ספירת השינויים

    last_clk_state = clk_state

# תצוגת ההודעה על המסך
def display_message(message):
    oled.fill(0)  # ניקוי המסך
    oled.text(message, 0, 20)
    oled.show()

# הצגת אפשרויות
def display_options(options, title=""):
    oled.fill(0)
    if title:
        oled.text(title, 0, 0)
    for i, option in enumerate(options):
        prefix = ">" if i == selected_option else " "  # סימון הבחירה הנוכחית
        oled.text(f"{prefix} {option}", 0, 20 + i * 10)
    oled.show()

# שאלה אם לצאת עם בחירה
def ask_exit():
    global selected_option
    selected_option = 0  # אתחול הבחירה
    
    while True:
        # עדכון המיקום בתפריט לפי ה-Rotary Encoder
        update_selection(exit_options)
        
        # הצגת הבחירה הנוכחית על המסך
        display_options(exit_options, "Exit? Confirm:")
        
        # בדיקה אם הכפתור שוחרר לחלוטין
        if button_pin.value() == 1:  # הכפתור משוחרר
            # המתנה ללחיצה חדשה
            while button_pin.value() == 1:  # המתנה שהכפתור יישאר משוחרר
                update_selection(exit_options)  # לאפשר שינוי בחירה בזמן ההמתנה
                display_options(exit_options, "Exit? Confirm:")
                time.sleep(0.1)
            
            # זיהוי לחיצה חדשה
            if button_pin.value() == 0:  # הכפתור נלחץ
                time.sleep(0.2)  # מניעת קריאה כפולה
                
                # פעולה לפי הבחירה הנוכחית
                if exit_options[selected_option] == "Yes":
                    return True  # יציאה לתפריט הראשי
                elif exit_options[selected_option] == "No":
                    return False  # חזרה למקום שבו היינו

# פונקציה לטיפול בלחיצות
def handle_button_press():
    start_time = time.ticks_ms()
    while button_pin.value() == 0:  # כל עוד הכפתור לחוץ
        if time.ticks_diff(time.ticks_ms(), start_time) > 3000:  # לחיצה ארוכה מעל 3 שניות
            return "long"
    if time.ticks_diff(time.ticks_ms(), start_time) < 1000:  # לחיצה קצרה מתחת לשנייה אחת
        return "short"
    return None  # במידה ולא זוהתה לחיצה

# לולאת הבחירה
def main_loop():
    global selected_option
    while True:
        update_selection(main_options)
        display_options(main_options, "Please select:")

        # בדיקת מצב לחיצה
        if button_pin.value() == 0:  # כפתור נלחץ
            press_type = handle_button_press()
            if press_type == "short":
                chosen_option = main_options[selected_option]
                display_message(f"You chose: {chosen_option}")
                time.sleep(2)  # הצגת הבחירה למשך 2 שניות
            elif press_type == "long":
                if ask_exit():  # אם המשתמש בחר לצאת
                    selected_option = 0  # חזרה לתפריט הראשי
                else:
                    display_message("Returning...")
                    time.sleep(2)  # חזרה למקום האחרון

# הפעלת הקוד
try:
    main_loop()
except KeyboardInterrupt:
    oled.fill(0)
    oled.show()



# In[ ]:


# ניסיון לעשות פונקצייה שלמה לשליטה באנקודר אבל זה לא הכי טוב ועדיין לא מושלם העיקר הרעיון

from machine import Pin
import time

def rotary_encoder(clk_pin, dt_pin, min_value=None, max_value=None, circular=True):
    """
    פונקציה לניהול אנקודר.
    """
    # משתנים פנימיים של הפונקציה
    counter = 0
    change_count = 0
    last_clk_state = clk_pin.value()
    last_reported_value = None

    def update():
        """
        מעדכנת את הערך של האנקודר על בסיס מצב הפינים.
        """
        nonlocal counter, change_count, last_clk_state
        clk_state = clk_pin.value()
        dt_state = dt_pin.value()

        if clk_state != last_clk_state:
            change_count += 1

            if change_count == 2:
                if dt_state != clk_state:
                    counter += 1
                else:
                    counter -= 1

                if min_value is not None and max_value is not None:
                    if circular:
                        if counter > max_value:
                            counter = min_value
                        elif counter < min_value:
                            counter = max_value
                    else:
                        if counter > max_value:
                            counter = max_value
                        elif counter < min_value:
                            counter = min_value

                change_count = 0

        last_clk_state = clk_state

    def get_value():
        """
        מחזירה את הערך הנוכחי של האנקודר.
        """
        return counter

    def has_changed():
        """
        בודקת אם הערך של האנקודר השתנה מאז הפעם האחרונה.
        """
        nonlocal last_reported_value
        current_value = get_value()
        if current_value != last_reported_value:
            last_reported_value = current_value
            return True
        return False

    return update, get_value, has_changed


# הגדרת הפינים
clk_pin = Pin(25, Pin.IN, Pin.PULL_UP)
dt_pin = Pin(26, Pin.IN, Pin.PULL_UP)

# יצירת פונקציות לעדכון וקבלת ערך
update, get_value, has_changed = rotary_encoder(clk_pin, dt_pin, min_value=-50, max_value=50, circular=True)

# לולאת עבודה
while True:
    update()  # עדכון הערך של האנקודר
    if has_changed():  # בדיקה אם הערך השתנה
        print(f"Encoder value: {get_value()}")
    time.sleep(0.01)  # השהייה קצרה




# In[ ]:


# קוד מדוייק לכפתור סיבובי שעובד נפלא אבל מצריך ספרייה ייעודית
#https://github.com/miketeachman/micropython-rotary
import time
from machine import Pin, I2C
import ssd1306
from rotary_irq_esp import RotaryIRQ

# הגדרת חיבור למסך OLED
i2c = I2C(1, scl=Pin(22), sda=Pin(21))  # חיבור I2C על פי החיבורים שלך
oled = ssd1306.SSD1306_I2C(128, 64, i2c)  # הגדרת מסך 128x64

# הגדרת Rotary Encoder
r = RotaryIRQ(pin_num_clk=25, 
              pin_num_dt=26, 
              min_val=-50,  # מינימום -50
              max_val=50,   # מקסימום 50
              reverse=False, 
              range_mode=RotaryIRQ.RANGE_WRAP)

val_old = r.value()

# הגדרת כפתור
button = Pin(27, Pin.IN, Pin.PULL_UP)  # כפתור על פין 27

# הצגת ברכה ראשונית על המסך
oled.fill(0)
oled.text("Rotary Encoder", 0, 0)
oled.text("Value:", 0, 20)
oled.show()

# משתנה לשמירת הערך של הסיבוב
val_new = val_old

# לולאת עבודה ראשית
while True:
    # קריאה לערך הנוכחי של ה-Rotary Encoder
    val_new = r.value()
    
    if val_old != val_new:
        val_old = val_new
        # הצגת הערך החדש על המסך
        oled.fill(0)  # ניקוי המסך
        oled.text("Rotary Encoder", 0, 0)
        oled.text("Value: {}".format(val_new), 0, 20)
        oled.show()
        
    # אם הכפתור נלחץ, הצג את הערך הנבחר
    if not button.value():  # כפתור נלחץ
        oled.fill(0)  # ניקוי המסך
        oled.text("Chosen Value:", 0, 0)
        oled.text("Value: {}".format(val_new), 0, 8)
        oled.show()
        time.sleep(1)  # השהייה קצרה כדי להימנע מכפילות בתצוגה

    time.sleep_ms(50)  # השהייה קצרה למנוע חישוב חזרות מיותרות



# In[ ]:





# In[ ]:


# קוד למנוע דו כיווני מאוד חשוב שעובד סוף סוף


from machine import Pin, PWM
import time

# הגדרת הפינים ב-ESP32
#R_IS = Pin(4, Pin.OUT)
R_EN = Pin(15, Pin.OUT)
R_PWM = PWM(Pin(18))
#L_IS = Pin(5, Pin.OUT)
L_EN = Pin(23, Pin.OUT)
L_PWM = PWM(Pin(19))

# הגדרת תדר ה-PWM
R_PWM.freq(5000)  # תדר 5kHz
L_PWM.freq(5000)  # תדר 5kHz

# אתחול של הפינים
#R_IS.value(0)
#L_IS.value(0)
R_EN.value(1)
L_EN.value(1)

while True:
    # סיבוב קדימה
    for i in range(0, 1024, 10):
        R_PWM.duty(i)  # שליחת PWM לערוץ R_PWM 
        #R_PWM.duty(1023)  # שליחת PWM מקסימלית לערוץ R_PWM אם רוצים מייד תאוצה מלאה
        L_PWM.duty(0)  # שליחת PWM לערוץ L_PWM
        time.sleep(0.5)
    
    time.sleep(0.5)
    
    # סיבוב אחורה
    for i in range(0, 1024, 10):
        R_PWM.duty(0)  # שליחת PWM לערוץ R_PWM
        #L_PWM.duty(1023)  # שליחת PWM מקסימלית לערוץ L_PWM אם רוצים מייד תאוצה מלאה
        L_PWM.duty(i)  # שליחת PWM לערוץ L_PWM
        time.sleep(0.5)
    
    time.sleep(0.5)
    

'''
# קוד עם תאוצה מיידית
from machine import Pin, PWM
import time

# הגדרת הפינים ב-ESP32
R_EN = Pin(15, Pin.OUT)  # אפשר כיוון קדימה
R_PWM = PWM(Pin(18))
L_EN = Pin(23, Pin.OUT)  # אפשר כיוון אחורה
L_PWM = PWM(Pin(19))

# הגדרת תדר ה-PWM
R_PWM.freq(5000)  # תדר 5kHz
L_PWM.freq(5000)  # תדר 5kHz

# אתחול של הפינים
R_EN.value(1)  # אפשר כיוון קדימה
L_EN.value(1)  # אפשר כיוון אחורה

while True:
    # סיבוב קדימה - PWM על 255 מיד
    R_PWM.duty(1023)  # שליחת PWM מקסימלית לערוץ R_PWM
    L_PWM.duty(0)    # שליחת PWM לערוץ L_PWM
    time.sleep(0.5)
    
    time.sleep(1)
    
    # סיבוב אחורה - PWM על 255 מיד
    R_PWM.duty(0)    # שליחת PWM לערוץ R_PWM
    L_PWM.duty(1023)  # שליחת PWM מקסימלית לערוץ L_PWM
    time.sleep(0.5)
    
    time.sleep(1)
    


# In[ ]:


# קוד למנוע משולב רוטרי אנקודר דו כיווני בלי מסך

from machine import Pin, PWM
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
R_PWM.freq(5000)  # תדר 5kHz
L_PWM.freq(5000)  # תדר 5kHz

# אתחול של הפינים
R_EN.value(1)
L_EN.value(1)

# משתנים
counter = 0
last_clk_state = clk_pin.value()

# פונקציה לעדכון מהירות המנוע
def update_motor_speed(counter):
    # הגבלת ערכים של counter ל-0 עד 1023
    speed = min(max(abs(counter), 0), 1023)
    
    if counter > 0:  # סיבוב קדימה
        R_PWM.duty(speed)
        L_PWM.duty(0)
    elif counter < 0:  # סיבוב אחורה
        R_PWM.duty(0)
        L_PWM.duty(speed)
    else:  # עצירה
        R_PWM.duty(0)
        L_PWM.duty(0)

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
        
        print(f"Counter: {counter}")
        update_motor_speed(counter)

    last_clk_state = clk_state

# הגדרת טריגר להפעלת פונקציית callback
clk_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=rotary_callback)

# לולאה ראשית
while True:
    time.sleep(0.1)  # זמן מנוחה כדי למנוע עומס על המעבד


# In[ ]:


# קוד למנוע דו כיווני 12 וולט עם מסך ורוטרי אנקודר וכפתור הכל מושלם

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
R_PWM.freq(15000)  # תדר 5kHz אפשר גם 5000
L_PWM.freq(15000)  # תדר 5kHz אפשר גם 5000

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



# In[ ]:


# הפעלת וכיבוי נורה באמצעות כפתור

# הפעלת וכיבוי נורת לד

from machine import Pin
import time

# הגדרת נורת ה-LED (במצב output)
led = Pin(23, Pin.OUT)

# הגדרת הכפתור (במצב input עם pull-up)
button = Pin(18, Pin.IN, Pin.PULL_UP)

# פונקציה לבדיקת לחיצה על הכפתור
def check_button():
    if button.value() == 0:  # 0 מציין שהכפתור לחוץ
        led.value(not led.value())  # הפוך את מצב ה-LED
        time.sleep(0.3)  # השהייה קטנה כדי למנוע לחיצות כפולות       
# לולאה ראשית
while True:
    check_button()  # בדוק את מצב הכפתור
'''



# In[ ]:


# כפתור בלי נורה
# הפעלת וכיבוי נורת לד

from machine import Pin
import time

# הגדרת נורת ה-LED (במצב output)
led = Pin(23, Pin.OUT)

# הגדרת הכפתור (במצב input עם pull-up)
button = Pin(18, Pin.IN, Pin.PULL_UP)

# פונקציה לבדיקת לחיצה על הכפתור
def check_button():
    if button.value() == 0:  # 0 מציין שהכפתור לחוץ
        led.value(not led.value())  # הפוך את מצב ה-LED
        time.sleep(0.3)  # השהייה קטנה כדי למנוע לחיצות כפולות       
# לולאה ראשית
while True:
    check_button()  # בדוק את מצב הכפתור
'''


# In[ ]:


# קוד לחיישן טמפרטורה בלבד ds18x20 והדפסה על המסך

 
import machine
import onewire
import ds18x20
import time
import ssd1306
from machine import Pin, I2C

# הגדרת חיישן DS18B20 על פין 22
ds_pin = machine.Pin(13)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

# סריקת חיישנים
roms = ds_sensor.scan()
#print('Found DS devices: ', roms)

# הגדרת OLED
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

while True:
    ds_sensor.convert_temp()  # התחלת המרת טמפרטורה
    time.sleep_ms(750)  # זמן המתנה להשלמת המדידה
    
    for rom in roms:
        temp_c = ds_sensor.read_temp(rom)  # קריאת הטמפרטורה במעלות צלזיוס
        print('Temperature: {}°C'.format(temp_c))
        
        # הצגת הטמפרטורה על המסך OLED
        oled.fill(0)  # ניקוי המסך
        oled.text('Temp: {:.5f} C'.format(temp_c), 0, 0)
        oled.show()  # עדכון המסך
        
    time.sleep(0)  # המתנה של 5 שניות לפני המדידה הבאה

    
'''
# זה בלי מסך אלא מדפיס למסוף ובכל מקרה בהכל לא צריך ספרייה ייעודית
# Complete project details at https://RandomNerdTutorials.com

import machine, onewire, ds18x20, time

ds_sensor = ds18x20.DS18X20(onewire.OneWire(machine.Pin(15)))

roms = ds_sensor.scan()
print('Found DS devices: ', roms)

while True:
  ds_sensor.convert_temp()
  time.sleep_ms(750)
  for rom in roms:
    print(rom)
    print(ds_sensor.read_temp(rom))
  time.sleep(1)
'''


# In[ ]:


# בחירת מספרים באמצעות פוטנציומטר
from machine import ADC, Pin, I2C
import ssd1306
import time

# הגדרות של הפינים
pot_pin = ADC(Pin(34))
button_pin = Pin(23, Pin.IN, Pin.PULL_UP)

# הגדרות של המסך OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

selected_number = 1

while True:
    # קריאת ערך מהפוטנציומטר
    pot_value = pot_pin.read()
    selected_number = int((pot_value / 4095) * 100) + 1  # בין 1 ל-100

    # עדכון המסך
    oled.fill(0)  # מנקה את המסך
    oled.text("Selected:", 0, 0)
    oled.text(str(selected_number), 0, 20)
    oled.show()

    # בדיקת מצב הכפתור
    if not button_pin.value():  # אם הכפתור נלחץ
        oled.fill(0)
        oled.text("Confirmed:", 0, 0)
        oled.text(str(selected_number), 0, 20)
        oled.show()
        time.sleep(1)  # המתנה לפני חזרה למצב הראשי


# In[ ]:


# קריאת טמפרטורה מחיישן NTC שדורש חיבור מקביל לנגד 10

# פונקצייה חשובה מאוד לקראת מכשיר PCR
from machine import Pin, ADC, I2C
import ssd1306  # ספריית מסך ה-OLED
import time
import math

# הגדרת ה-ADC לחיבור ה-NTC Thermistor
adc_pin = 34
adc = ADC(Pin(adc_pin))
adc.width(ADC.WIDTH_10BIT)  # רזולוציה של 10 ביט
adc.atten(ADC.ATTN_11DB)    # טווח הקריאה: 0-3.3V

# הגדרת מסך ה-OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# קבועים ל-NTC Thermistor
R_NOMINAL = 10000  # 10KΩ
B_COEFFICIENT = 3950
T_NOMINAL = 25  # טמפרטורה נומינלית (C°)
SERIES_RESISTOR = 10000  # נגד סדרה

def read_temperature():
    # קריאת ערך האנלוגי
    adc_value = adc.read()
    
    # חישוב התנגדות ה-NTC
    resistance = SERIES_RESISTOR / ((1023 / adc_value) - 1)
    
    # שימוש בנוסחת סטפאן-בולצמן לחישוב טמפרטורה
    steinhart = resistance / R_NOMINAL  # (R/Ro)
    steinhart = math.log(steinhart)  # ln(R/Ro)
    steinhart /= B_COEFFICIENT  # 1/B * ln(R/Ro)
    steinhart += 1.0 / (T_NOMINAL + 273.15)  # + (1/To)
    steinhart = 1.0 / steinhart  # Invert
    temperature_c = steinhart - 273.15  # ממעלות קלווין לצלזיו
    return temperature_c

def display_temperature(temp):
    oled.fill(0)  # נקה את המסך
    oled.text('Temp: {:.2f} C'.format(temp), 0, 0)
    oled.show()

# לולאה למדידת טמפרטורה והצגתה
while True:
    temperature = read_temperature()
    display_temperature(temperature)
    time.sleep(1)  # המתנה של 1 שניות בין המדידות


# In[ ]:


# הפעלת וכיבוי ממסר חשמל

from machine import Pin
import time

relay = Pin(5, Pin.OUT)

while True:
    relay.on()  # להפעיל את הממסר
    time.sleep(5)
    relay.off() # לכבות את הממסר
    time.sleep(5)


# In[ ]:


# שליטה לפי מדידדת טמפרטורה בגוף חימום וגוף קירור שמחוברים יחד לממסר כפול 

# הפעלת גוף חימום לפי הטמפרטורה חשוב מאוד

from machine import Pin, ADC, I2C
import ssd1306  # ספריית מסך ה-OLED
import time
import math

# הגדרת ה-ADC לחיבור ה-NTC Thermistor
adc_pin = 34
adc = ADC(Pin(adc_pin))
adc.width(ADC.WIDTH_10BIT)  # רזולוציה של 10 ביט
adc.atten(ADC.ATTN_11DB)    # טווח הקריאה: 0-3.3V

# הגדרת מסך ה-OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# קבועים ל-NTC Thermistor
R_NOMINAL = 10000  # 10KΩ
B_COEFFICIENT = 3950
T_NOMINAL = 25  # טמפרטורה נומינלית (C°)
SERIES_RESISTOR = 10000  # נגד סדרה

# הגדרת הממסר לגוף החימום
relay1 = Pin(5, Pin.OUT)  # חיבור הממסר או גוף החימום
relay2 = Pin(15, Pin.OUT)  # חיבור הממסר או גוף החימום

def read_temperature():
    # קריאת ערך האנלוגי
    adc_value = adc.read()
    
    # חישוב התנגדות ה-NTC
    resistance = SERIES_RESISTOR / ((1023 / adc_value) - 1)
    
    # שימוש בנוסחת סטפאן-בולצמן לחישוב טמפרטורה
    steinhart = resistance / R_NOMINAL  # (R/Ro)
    steinhart = math.log(steinhart)  # ln(R/Ro)
    steinhart /= B_COEFFICIENT  # 1/B * ln(R/Ro)
    steinhart += 1.0 / (T_NOMINAL + 273.15)  # + (1/To)
    steinhart = 1.0 / steinhart  # Invert
    temperature_c = steinhart - 273.15  # ממעלות קלווין לצלזיו
    return temperature_c

def display_temperature(temp):
    oled.fill(0)  # נקה את המסך
    oled.text('Temp: {:.2f} C'.format(temp), 0, 0)
    oled.show()

# לולאה למדידת טמפרטורה והצגתה
while True:
    temperature = read_temperature()
    display_temperature(temperature)

    # שליטה בגוף החימום
    if temperature < 25:
        relay1.on()  # הדלק את גוף החימום
        relay2.on()
    else:
        relay1.off()
        relay2.off()  # כבה את גוף החימום

    time.sleep(2)  # המתנה של 2 שניות בין המדידות
'''


# In[ ]:





# In[ ]:


# למד סטורציה ודופק

from machine import Pin, SoftI2C
import max30100
import ssd1306
import time

# הגדרת החיבור של I2C לחיישן ולמסך
sda = Pin(4)
scl = Pin(5)
i2c = SoftI2C(scl=scl, sda=sda)

# בדיקת חיבורי I2C
print('Scanning I2C devices...')
devices = i2c.scan()
print("I2C devices found:", devices)

if 87 not in devices:  # כתובת MAX30100 בעשרוני
    print("MAX30100 not found!")
else:
    print("MAX30100 found!")

# הגדרת החיישן
sensor = max30100.MAX30100(i2c=i2c)
sensor.enable_spo2()

# הגדרת המסך OLED
oled_width = 128
oled_height = 64
i2c_oled = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c_oled)

# פונקציה לקריאת הנתונים והצגתם
def read_and_display():
    while True:
        # קריאה מהחיישן
        sensor.read_sensor()
        ir_value = sensor.ir
        red_value = sensor.red

        # הצגת הנתונים על המסך
        oled.fill(0)  # ניקוי המסך
        oled.text("Heart Rate Monitor", 0, 0)
        oled.text("IR: {}".format(ir_value), 0, 20)
        oled.text("RED: {}".format(red_value), 0, 40)
        oled.show()

        # השהיה בין קריאות
        time.sleep(0.5)

# קריאה והצגה של הנתונים על המסך
read_and_display()



# In[ ]:


# קוד נורא חשוב לחישובי שמש וירח במיקרופייתון

# https://github.com/peterhinch/micropython-samples/issues/42
# https://github.com/peterhinch/micropython-samples/tree/d2929df1b4556e71fcfd7d83afd9cf3ffd98fdac/astronomy
# https://github.com/peterhinch/micropython-samples/blob/d2929df1b4556e71fcfd7d83afd9cf3ffd98fdac/astronomy/sun_moon.py
# https://github.com/peterhinch/micropython-samples/blob/d2929df1b4556e71fcfd7d83afd9cf3ffd98fdac/astronomy/moonphase.py



# למה בניו יורק יש בעיה עם שעה זמנית מגן אברהם???????????????????????????
# צריך לחשוב איך לגרום שהשעון יהיה מוגדר אוטומטית לשעון קיץ בתאריכים המתאימים.


import time, math, machine, utime
#import datetime as dt
from sun_moon import RiSet  # יבוא הספרייה
from machine import I2C, Pin
from ssd1306 import SSD1306_I2C  # ספריית OLED
from ds3231 import DS3231

from writer import Writer
import myfont  # Font to use



#########################################

# פונקצייה להפיכת טקסט כדי שעברית תהיה משמאל לימין
def reverse(string):
    return "".join(reversed(string))

# מקבל מספר יום בשבוע לפי הנורמלי ומחזיר את מספר היום בשבוע לפי ההגדרות ב RTC
def get_rtc_weekday(weekday):
    rtc_weekday_dict = {1:6,2:0,3:1,4:2,5:3,6:4,7:5}
    return rtc_weekday_dict.get(weekday)

# מוציא את מספר היום בשבוע הנורמלי לפי סדר מתוך שעון המכשיר שמוגדר RTC
def get_normal_weekday(rtc_weekday):
    weekday_dict = {6:1,0:2,1:3,2:4,3:5,4:6,5:7}
    return weekday_dict.get(rtc_weekday)


# פונקצייה שמחזירה נכון או לא נכון האם כרגע נוהג שעון קיץ בישראל
# היא מתבססת על מה השעה והתאריך ברגע זה בשעון הפנימי של המיקרו בקר ולכן חייבים להגדיר אותו לפני שקוראים לפונקצייה זו
# שעון הקיץ מופעל בישראל בין יום שישי שלפני יום ראשון האחרון של חודש מרץ בשעה 02:00, לבין יום ראשון האחרון של חודש אוקטובר בשעה 02:00.
def is_now_israel_DST():
    # קבלת השנה הנוכחית
    current_year = utime.localtime()[0]
    
    # חישוב יום ראשון האחרון של מרץ
    march_last_sunday = utime.mktime((current_year, 3, 31, 2, 0, 0, 0, 0, 0))
    while utime.localtime(march_last_sunday)[6] != get_rtc_weekday(1):
        march_last_sunday -= 86400  # מורידים יום
    
    # חישוב יום שישי שלפני יום ראשון האחרון של מרץ
    # אם יום ראשון האחרון הוא ה-31, אז יום שישי לפניו יהיה ה-29.
    last_friday_march = march_last_sunday - 2 * 86400  # מורידים 2 ימים (שישי)

    # חישוב יום ראשון האחרון של אוקטובר
    october_last_sunday = utime.mktime((current_year, 10, 31, 2, 0, 0, 0, 0, 0))
    while utime.localtime(october_last_sunday)[6] != get_rtc_weekday(1): 
        october_last_sunday -= 86400  # מורידים יום
    
    # השוואה בין הזמן הנוכחי לתאריכים של שעון קיץ
    current_time = utime.mktime(utime.localtime())
    
    # שעון קיץ פעיל בין יום שישי שלפני יום ראשון האחרון של מרץ ועד יום ראשון האחרון של אוקטובר
    if last_friday_march <= current_time < october_last_sunday:
        return True  # שעון קיץ פעיל
    else:
        return False  # לא פעיל


# פונקצייה להמרת זמן מ-שניות ל- סטרינג שעות דקות ושניות, או רק ל- סטרינג דקות ושניות שבניתי בסיוע רובי הבוט
def convert_seconds(seconds, to_hours=False):        
    # חישוב מספר הדקות והשניות שיש בשעה אחת, והדפסתם בפורמט של דקות ושניות
    if to_hours:
        return f'{seconds // 3600 :02.0f}:{(seconds % 3600) // 60 :02.0f}:{seconds % 60 :02.0f}'
    else:
        return f'{seconds // 60 :02.0f}:{seconds % 60 :02.0f}'


# פונקציה לעדכון זמן ב-RiSet
def update_riset_time(riset):
    rtc_timestamp = utime.mktime(utime.localtime())
    riset.set_time(rtc_timestamp)
    
    
    
# פונקציה לקרוא את הזמן מ-DS3231 ולעדכן את ה-machine.RTC()
def sync_rtc_with_ds3231():
     
    
    try:
        
        # נתינת חשמל חיובי לפין המתאים של ds3231
        ds3231_plus = machine.Pin(27, machine.Pin.OUT)
        ds3231_plus.value(1)

        # יצירת אובייקט I2C (בהנחה שהשימוש בפינים 21 ו-22)
        # בפין 12 חובה להשתמש דווקא ב softI2C
        ds3231_i2c = machine.SoftI2C(scl=machine.Pin(12), sda=machine.Pin(14))
        
        # יצירת אובייקט RTC במערכת (machine RTC)
        rtc_system = machine.RTC()

        # יצירת אובייקט DS3231
        rtc_ds3231 = DS3231(ds3231_i2c)
        
        ################################################################################################
        # כל החלק הזה קשור לאופצייה של עדכון השעון הפנימי שבדרך כלל לא מתבצעת
        
        # ברירת המחדל היא לא לעדכן את השעון החיצוני
        # ואם הבקר לא מחובר למחשב אסור לעדכן את השעון החיצוני לפי השעון הפנימי
        # רק אם הבקר מחובר למחשב אפשר לעדכן את השעון החיצוני לפי שעון המחשב אם רוצים
        # גם זה לא מומלץ כי יתן שעון קיץ בקיץ וכדאי לשמור את השעון החיצוני על שעון חורף
        update_rtc_ds3231 = False # False or True  
        update_rtc_ds3231_from_computer = False # False or True  
        
        if update_rtc_ds3231:
            
            if update_rtc_ds3231_from_computer:
            
                # קריאת זמן המערכת של הבקר שזה הזמן המדוייק של המחשב רק כאשר הבקר מחובר למחשב
                year, month, day, week_day, hour, minute, second, micro_second = rtc.datetime()
                # חייבים למפות מחדש את סדר הנתונים וצורתם כי כל ספרייה משתמשת בסדר וצורה אחרים קצת
                new_time = (year, month, day, hour, minute, second, get_normal_weekday(week_day))
            
            else:
                
                # כאן אפשר לבחור לבד איזה נתונים לכוון לשעון החיצוני
                year, month, day, hour, minute, second, weekday = 1988, 2, 24, 18, 45, 56, 1 # 1 = sunday                
                new_time = (year, month, day, hour, minute, second, weekday)


            print("השעה בשעון החיצוני לפני העדכון", rtc_ds3231.datetime())
            
            # עדכון הזמן ב-RTC
            rtc_ds3231.datetime(new_time)

            print("הזמן בשעון החיצוני עודכן בהצלחה השעה לאחר העדכון היא", rtc_ds3231.datetime())

        ###################################################################################################################    
        
        # קריאת הזמן מ-DS3231
        ds3231_time = rtc_ds3231.datetime()

        # עדכון ה-machine RTC עם הזמן שנקרא מ-DS3231
        rtc_system.datetime(ds3231_time)
        print("Time synced with DS3231: ", ds3231_time)
        
        # כיבוי החשמל החיובי שהולך לשעון החיצוני כי כבר לא צריך אותו
        # זה לא חובה
        ds3231_plus.value(0)

    except Exception as e:
        print("Error reading from DS3231: ", e)
        #במקרה של שגיאה, נגדיר זמן ידני ב-machine.RTC()
        manual_time = (2005, 12, 30, get_rtc_weekday(7), 22, 50, 30, 0)  # (שנה, חודש, יום, יום בשבוע, שעה, דקות, שניות, תת-שניות)
        rtc_system.datetime(manual_time)
        print("Time set manually in machine.RTC: ", manual_time)
        
        
def calculate_temporal_time(rtc_timestamp, sunrise_timestamp, sunset_timestamp):
    
        # בדיקה האם זה יום לפי בדיקה האם הזמן הנוכחי גדול משעת הזריחה וקטן משעת השקיעה
        is_day = rtc_timestamp >= sunrise_timestamp and rtc_timestamp < sunset_timestamp
        
        # חישוב מספר השניות בין הזריחה לשקיעה
        day_length_seconds = sunset_timestamp - sunrise_timestamp
        # חישוב מספר השניות בין השקיעה לזריחה כלומר אורך הלילה בשיטה לא מדוייקת כי היא הולכת לפי היום הנוכחי
        night_length_seconds = 86400 - day_length_seconds # 86400 זה מספר השניות שיש ביממה שלמה
        
        # חישוב מספר השניות בשעה זמנית אחת של היום לפי חלוקת אורך היום או הלילה ל 12
        seconds_per_hour_in_day_or_night = (day_length_seconds if is_day else night_length_seconds) / 12
        
        # חישוב כמה שניות עברו מאז הזריחה או השקיעה עד הזמן הנוכחי 
        time_since_last_sunrise_or_sunset = rtc_timestamp - (sunrise_timestamp if is_day else sunset_timestamp)
        
        # אם מדובר אחרי 12 בלילה ולפני הזריחה
        if rtc_timestamp < sunrise_timestamp:
            # חישוב מתי הייתה השקיעה של אתמול זה לא מדוייק אבל מספיק בסדר בשביל שעה זמנית בלילה
            yesterday_sunset_timestamp = sunrise_timestamp - night_length_seconds
            time_since_last_sunrise_or_sunset = rtc_timestamp - yesterday_sunset_timestamp
        
        
        # המרת השניות לפורמט שעות, דקות ושניות
        A = (time_since_last_sunrise_or_sunset / seconds_per_hour_in_day_or_night) + 0.0000001
        zmanit_hour = int(A)
        B = ((A - zmanit_hour) * 60) + 0.0000001
        zmanit_minute = int(B)
        C = ((B - zmanit_minute) * 60) + 0.0000001
        zmanit_second = int(C)

        # הדפסת השעה הזמנית המתאימה בפורמט שעות:דקות:שניות
        temporal_time = f'{zmanit_hour:02.0f}:{zmanit_minute:02.0f}:{zmanit_second:02.0f}'
        
        return temporal_time
        


#######################################################################


# הגדרת מסך OLED
WIDTH = 128
HEIGHT = 64
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # שנה פינים בהתאם לחומרה שלך
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)


# Instantiate a writer for a specific font
wri = Writer(oled, myfont)


# הגדרת RTC השעון של המיקרו בקר
rtc = machine.RTC()

# את השורה הזו צריך להגדיר רק אם רוצים להגדיר ידנית את השעון הפנימי של הבקר וזה בדרך כלל לא יישומי כאן
#rtc.datetime((2025, 3, 26, get_rtc_weekday(4), 10, 59, 0, 0))  # (שנה, חודש, יום, יום בשבוע, שעה, דקות, שניות, תת-שניות)

# קריאה לפונקצייה שמעדכנת את שעון המכונה לפי שעון כרכיב נלווה ואם יש שגיאה או שהוא לא מחובר מעדכנת זמן אחר
# זה קורה רק פעם בהתחלה ולא כל שנייה מחדש
sync_rtc_with_ds3231()


modiin_illit = {"name": "modiin-illit", "heb_name": "מ. עילית", "lat": 31.940826, "long": 35.037057, "utc_offset": 3 if is_now_israel_DST() else 2}
jerusalem = {"name": "jerusalem", "heb_name": "ירושלים", "lat": 31.776812, "long": 35.235694, "utc_offset": 3 if is_now_israel_DST() else 2}
bnei_brak = {"name": "bnei_brak", "heb_name": "בני ברק", "lat": 32.083156, "long": 34.832722, "utc_offset": 3 if is_now_israel_DST() else 2}
new_york = {"name": "new_york", "heb_name": "ניו-יורק", "lat": 40.7143528, "long": -74.0059731, "utc_offset": 3 if is_now_israel_DST() else 2}


locations = [modiin_illit, jerusalem, bnei_brak, new_york]

location = locations[0]

#sunrise_timestamp = 0.0
#sunset_timestamp = 0.0

# תצוגה על מסך OLED
def display_oled():
    # יצירת אובייקט RiSet
    riset = RiSet(lat=location["lat"], long=location["long"], lto=location["utc_offset"], tl=16) # 16 זה המעלות במינוס לתחילת וסוף מגן אברהם
    #update_riset_time(riset) # לא צריך את זה כי ברירת מחדל שהחישוב הוא על הזמן הנוכחי

    # קבלת הזמן הנוכחי מהמכשיר
    year, month, day, rtc_week_day, hour, minute, second, micro_second = rtc.datetime()
    # חישוב מה השעה הנוכחית בשבר עשרות
    current_hour = (hour + (minute / 60) + (second / 3600)) - location["utc_offset"]
    
    # חישוב גובה השמש והירח ברגע זה כלומר שעה נוכחית בשבר עשרוני
    altitude = math.degrees(math.asin(riset.sin_alt(current_hour, sun=True)))
    m_altitude = math.degrees(math.asin(riset.sin_alt(current_hour, sun=False)))
    
    # קבלת זמני זריחה ושקיעה
    #sunrise = riset.sunrise(variant=2)  # פורמט זמן קריא
    #sunset = riset.sunset(variant=2)  # פורמט זמן קריא
    
    #sunrise_datetime = dt.datetime.fromtimestamp(riset.sunrise(1)) # נתמך רק בפייתון רגיל
    #print(sunrise_datetime)
    
    #sunrise_utime = utime.localtime(riset.sunrise(1))
    
    #print(sunrise_utime)
    #sunrise_datetime = dt.datetime(*sunrise_utime[:6])  # יצירת אובייקט datetime מתוך רשימת הערכים
    #sunset_utime = utime.localtime(riset.sunset(1))
    #sunset_datetime = dt.datetime(*sunset_utime[:6])  # יצירת אובייקט datetime מתוך רשימת הערכים
    
    # חותמת זמן של הרגע
    rtc_timestamp = utime.mktime(utime.localtime())
    
    #global sunrise_timestamp, sunset_timestamp
    #is_same_day = rtc_timestamp // 86400 == sunrise_timestamp // 86400
    #sunrise_timestamp = sunrise_timestamp if is_same_day else riset.sunrise(1)
    #sunset_timestamp = sunset_timestamp if is_same_day else riset.sunset(1)
    
    #  חותמת זמן של רגע הזריחה והשקיעה היום
    sunrise_timestamp = riset.sunrise(1)
    sunset_timestamp = riset.sunset(1)
    
    # חוממת זמן של תחילת וסוף הדמדומים של מגן אברהם כרגע מוגדר לעיל מינוס 16
    mga_start = riset.tstart(1) 
    mga_end = riset.tend(1)
    
    # חישוב שעה זמנית לפי הגרא מזריחה לשקיעה באמצעות פונקצייה שהוגדרה למעלה
    temporal_time = calculate_temporal_time(rtc_timestamp, sunrise_timestamp, sunset_timestamp)
    # חישוב שעה זמנית לפי מגן אברהם משמש בגובה מינוס 16 בבוקר לשמש בגובה מינוס 16 בערב
    temporal_time_mga = calculate_temporal_time(rtc_timestamp, mga_start, mga_end)
    
    
    # הצגת נתונים על מסך OLED
    oled.fill(0)
    date_string = "{:02d}/{:02d}/{:04d} ({})".format(day, month, year, get_normal_weekday(rtc_week_day))
    time_string = "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
    
    oled.text(f' {date_string}', 0, 0)
    oled.text(f'  {time_string} {"DST" if is_now_israel_DST() else "WT"}', 0, 9)
    #oled.text(f'  {location["name"]}', 0, 20)
    oled.text(f"{" " if altitude > 0 else ""}{round(altitude,3):.3f}", 0, 30)
    #oled.text(f"S_rise: {sunrise}", 0, 40)
    oled.text(f"{temporal_time}", 0, 42)
    #oled.text(f"  {" " if m_altitude > 0 else ""}{m_altitude:.2f}", 0, 54)
    oled.text(f"{temporal_time_mga}", 0, 54)
    
    
    Writer.set_textpos(oled, 16, 13)  # שורה שלישית בגובה 20
    wri.printstring(f'{reverse(location["heb_name"])} - {reverse("ח חודש")}')

    Writer.set_textpos(oled, 27, 58)  # שורה רביעית בגובה 30
    wri.printstring(f'°  :{reverse("שמש-גובה")}')
    
    Writer.set_textpos(oled, 39, 66)  # שורה רביעית בגובה 30
    wri.printstring(f' :{reverse("שעה זמנית")}')
    
    #Writer.set_textpos(oled, 51, 67)  # שורה רביעית בגובה 30
    #wri.printstring(f'° :{reverse("ירח")}')
    
    Writer.set_textpos(oled, 51, 67)  # שורה רביעית בגובה 30
    wri.printstring(f' :{reverse("זמנית-מגא")}')
       
    oled.show()



# הגדרת GPIO0 כקלט עם התנגדות פנימית כלפי מעלה
boot_button = Pin(0, Pin.IN, Pin.PULL_UP)

# אינדקס המיקום הנוכחי
location_index = 0

# משתנה לזמן הקריאה האחרונה
last_read_time = time.time()


    
# לולאת רענון
while True:
    
    # כל שעה צריך לקרוא מחדש את השעה כי השעון הפנימי של הבקר עצמו לא מדוייק מספיק
    # בדיקה אם עברה שעה (3600 שניות)
    if time.time() - last_read_time >= 3600:
        sync_rtc_with_ds3231()
        # עדכון זמן הקריאה האחרונה
        last_read_time = time.time()
   
    # טיפול בשינויי מיקום גיאוגרפי בלחיצה על הכפתור
    if boot_button.value() == 0:  # בדיקת אם הכפתור נלחץ
            # עדכון אינדקס המיקום באופן מעגלי
            location_index = (location_index + 1) % len(locations)
            location = locations[location_index]  # שליפת המילון של המיקום הנוכחי
            # ניתן להוסיף כאן קוד לבצע פעולה
            display_oled()
            time.sleep(0.5)  # מניעת קריאה מרובה בזמן הלחיצה

    display_oled()
    time.sleep(0.75)  # רענון כל שנייה




# In[ ]:


# קוד סופי לחיישן טמפרטורה לחות ולחץ אוויר BME280

# קוד טוב יותר שעובד עם פונקציות נוספות ושמירת מינ-מקס

import math
import machine
from machine import Pin, I2C
import ssd1306
import BME280
from time import sleep, localtime
from ds3231 import DS3231


# Initialize I2C for both OLED and BME280
i2c_BME280 = I2C(0, scl=Pin(27), sda=Pin(26))
i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=10000)

# Initialize OLED display
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Initialize BME280 sensor
bme = BME280.BME280(i2c=i2c_BME280)


# מקבל מספר יום בשבוע לפי הנורמלי ומחזיר את מספר היום בשבוע לפי ההגדרות ב RTC
def get_rtc_weekday(weekday):
    rtc_weekday_dict = {1:6,2:0,3:1,4:2,5:3,6:4,7:5}
    return rtc_weekday_dict.get(weekday)



# פונקציה לקרוא את הזמן מ-DS3231 ולעדכן את ה-machine.RTC()
def sync_rtc_with_ds3231():
    try:
        # הגדרת ערוץ שונה לקלט של שעון חיצוני
        # לא חובה ואפשר להשתמש בערוץ הקלט הרגיל
        i2c_ds3231 = i2c_BME280
        
        # יצירת אובייקט RTC במערכת (machine RTC)
        rtc_system = machine.RTC()
 
        # יצירת אובייקט DS3231
        rtc_ds3231 = DS3231(i2c_ds3231)

        # קריאת הזמן מ-DS3231
        ds3231_time = rtc_ds3231.datetime()

        # עדכון ה-machine RTC עם הזמן שנקרא מ-DS3231
        rtc_system.datetime(ds3231_time)
        print("Time synced with DS3231: ", ds3231_time)

    except Exception as e:
        print("Error reading from DS3231: ", e)
        # במקרה של שגיאה, נגדיר זמן ידני ב-machine.RTC()
        manual_time = (2005, 12, 30, get_rtc_weekday(7), 19, 50, 30, 0)  # (שנה, חודש, יום, יום בשבוע, שעה, דקות, שניות, תת-שניות)
        rtc_system.datetime(manual_time)
        print("Time set manually in machine.RTC: ", manual_time)


# הגדרת הזמן
rtc = machine.RTC()
#rtc.datetime((2024, 12, 12, 3, 18, 5, 0, 0))  # (שנה, חודש, יום, יום בשבוע, שעה, דקות, שניות, תת-שניות)
sync_rtc_with_ds3231()


# Variables for minimum and maximum tracking
min_temp = float('inf')
max_temp = float('-inf')
min_humidity = float('inf')
max_humidity = float('-inf')
min_pressure = float('inf')
max_pressure = float('-inf')

min_time_temp = localtime()
max_time_temp = localtime()
min_time_humidity = localtime()
max_time_humidity = localtime()
min_time_pressure = localtime()
max_time_pressure = localtime()

# Variable for current day tracking
current_date = localtime()[0:3]

# State for display toggling
current_screen = 0  # 0: Temperature, 1: Humidity, 2: Pressure

def get_sea_level_pressure_hpa(P_hpa, T_celsius, h_meters, M=0.0289644, g=9.80665, R=8.3144598):
    """
    Computes the sea level atmospheric pressure given the pressure at a specific height.

    Parameters:
        P_hpa (float): Pressure at the given height (hPa).
        T_celsius (float): Temperature at the given height (°C).
        h_meters (float): Height above sea level (meters).
        M (float): Molar mass of Earth's air (kg/mol). Default is 0.0289644.
        g (float): Gravitational acceleration (m/s^2). Default is 9.80665.
        R (float): Universal gas constant (J/(mol·K)). Default is 8.3144598.

    Returns:
        float: Atmospheric pressure at sea level (hPa).
    """
    # Convert inputs
    P = P_hpa * 100  # Convert hPa to Pa
    T = T_celsius + 273.15  # Convert Celsius to Kelvin

    # Reverse barometric formula to calculate sea-level pressure
    P0 = P * math.exp(M * g * h_meters / (R * T))

    # Convert back to hPa
    return P0 / 100

def get_data():
    """Reads temperature, humidity, and pressure from BME280 sensor."""
    temp = float(bme.temperature[:-1])
    humidity = float(bme.humidity[:-1])
    pressure = float(bme.pressure[:-3])
    return temp, humidity, pressure

def update_min_max(temp, humidity, pressure):
    """Updates minimum and maximum values for temperature, humidity, and pressure."""
    global min_temp, max_temp, min_humidity, max_humidity, min_pressure, max_pressure
    global min_time_temp, max_time_temp, min_time_humidity, max_time_humidity, min_time_pressure, max_time_pressure

    if temp < min_temp:
        min_temp = temp
        min_time_temp = localtime()
    if temp > max_temp:
        max_temp = temp
        max_time_temp = localtime()

    if humidity < min_humidity:
        min_humidity = humidity
        min_time_humidity = localtime()
    if humidity > max_humidity:
        max_humidity = humidity
        max_time_humidity = localtime()

    if pressure < min_pressure:
        min_pressure = pressure
        min_time_pressure = localtime()
    if pressure > max_pressure:
        max_pressure = pressure
        max_time_pressure = localtime()

def reset_min_max_if_new_day():
    """Resets minimum and maximum values if the day changes."""
    global min_temp, max_temp, min_humidity, max_humidity, min_pressure, max_pressure
    global min_time_temp, max_time_temp, min_time_humidity, max_time_humidity, min_time_pressure, max_time_pressure
    global current_date

    today = localtime()[0:3]
    if today != current_date:
        current_date = today
        min_temp = float('inf')
        max_temp = float('-inf')
        min_humidity = float('inf')
        max_humidity = float('-inf')
        min_pressure = float('inf')
        max_pressure = float('-inf')
        min_time_temp = localtime()
        max_time_temp = localtime()
        min_time_humidity = localtime()
        max_time_humidity = localtime()
        min_time_pressure = localtime()
        max_time_pressure = localtime()

def format_time(time_tuple):
    """Formats time tuple to HH:MM."""
    return '{:02}:{:02}'.format(time_tuple[3], time_tuple[4])

def display_data():
    """Displays sensor readings and additional information on OLED."""
    global current_screen

    temp, humidity, pressure = get_data()
    altitude = 320
    #delta_p = 10 * (altitude/100) # כלל האצבע: לחץ האוויר יורד בכ-12 hPa לכל 100 מטרים בגובה
    #pressure_at_sea_level = pressure + delta_p
    pressure_at_sea_level = get_sea_level_pressure_hpa(pressure, temp, altitude)

    update_min_max(temp, humidity, pressure_at_sea_level)
    reset_min_max_if_new_day()
    
    # Calculate dew point
    dew_point = temp - ((100 - humidity) / 5)

    oled.fill(0)

    t = localtime()
    time_string = "{:02d}/{:02d}/{:04d} {:02d}:{:02d}:{:02d}".format(t[2], t[1], t[0], t[3], t[4], t[5])
    oled.text(f'{time_string}', 0, 0)
    oled.text(' {:.1f} C   {:.1f}%'.format(temp, humidity), 0, 20)
    oled.text('   tal: {:.1f} C'.format(dew_point), 0, 9)
    oled.text('{:.1f} hPa {:.1f}'.format(pressure_at_sea_level,pressure), 0, 30)  

    if current_screen == 0:  # Temperature
        oled.text('Min: {:.1f}C {}'.format(min_temp, format_time(min_time_temp)), 0, 40)
        oled.text('Max: {:.1f}C {}'.format(max_temp, format_time(max_time_temp)), 0, 50)

    elif current_screen == 1:  # Humidity
        oled.text('Min: {:.1f}% {}'.format(min_humidity, format_time(min_time_humidity)), 0, 40)
        oled.text('Max: {:.1f}% {}'.format(max_humidity, format_time(max_time_humidity)), 0, 50)

    elif current_screen == 2:  # Pressure
        oled.text('Min: {:.0f}P {}'.format(min_pressure, format_time(min_time_pressure)), 0, 40)
        oled.text('Max: {:.0f}p {}'.format(max_pressure, format_time(max_time_pressure)), 0, 50)

    oled.show()

# Main loop to continuously update data
while True:
    display_data()
    current_screen = (current_screen + 1) % 3  # Cycle through screens (0, 1, 2)
    sleep(10)




# In[ ]:


# https://github.com/peterhinch/micropython-font-to-py/blob/master/writer/WRITER.md
# חובה להשתמש בדרייבר הרשמי של המסך בקישור הבא
# https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py #רשמי

# דוגמא נורא חשובה שעובדת למסך

import machine
from machine import Pin, I2C
from ssd1306 import SSD1306_SPI, SSD1306_I2C
from writer import Writer

import arial10  # Font to use


# Initialize I2C for both OLED and BME280
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=10000)
WIDTH = const(128)
HEIGHT = const(64)
ssd = SSD1306_I2C(WIDTH, HEIGHT, i2c)

#use_spi=False  # Tested with a 128*64 I2C connected SSD1306 display
#ssd = setup(use_spi)  # Instantiate display: must inherit from framebuf
# Demo drawing geometric shapes
rhs = WIDTH -1
ssd.line(rhs - 20, 0, rhs, 20, 1)  # Demo underlying framebuf methods
square_side = 10
ssd.fill_rect(rhs - square_side, 0, square_side, square_side, 1)
# Instantiate a writer for a specific font
wri = Writer(ssd, arial10)  # verbose = False to suppress console output
Writer.set_textpos(ssd, 0, 0)  # In case a previous test has altered this
wri.printstring('Sunday\n12 Aug 2018\n10.30am')
ssd.show()





# ציור כוכב

import machine
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from writer import Writer
import arial10  # Font to use

# Initialize I2C for both OLED and BME280
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=10000)
WIDTH = const(128)
HEIGHT = const(64)
ssd = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Define function to draw a star
def draw_star(x, y, size):
    # Draw the 5 points of a star using lines
    ssd.line(x, y - size, x + size // 2, y + size // 2, 1)  # top to bottom-right
    ssd.line(x, y - size, x - size // 2, y + size // 2, 1)  # top to bottom-left
    ssd.line(x, y + size, x + size // 2, y - size // 2, 1)  # bottom to top-right
    ssd.line(x, y + size, x - size // 2, y - size // 2, 1)  # bottom to top-left
    ssd.line(x - size // 2, y, x + size // 2, y, 1)          # left to right

# Draw a star in the middle of the screen
draw_star(WIDTH // 2, HEIGHT // 2, 20)

# Instantiate a writer for a specific font
wri = Writer(ssd, arial10)  # verbose = False to suppress console output
Writer.set_textpos(ssd, 0, 0)  # In case a previous test has altered this
wri.printstring('Star!\nTest')

# Show the result on the display
ssd.show()



# ציור אות A


import machine
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

# Initialize I2C for the OLED display
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=10000)
WIDTH = const(128)
HEIGHT = const(64)
ssd = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Function to draw the letter 'A' with lines
def draw_A(x, y, size):
    # Draw the left leg of A
    ssd.line(x, y + size, x + size // 2, y, 1)  # From bottom-left to top-middle
    # Draw the right leg of A
    ssd.line(x + size, y + size, x + size // 2, y, 1)  # From bottom-right to top-middle
    # Draw the horizontal line of A
    ssd.line(x + size // 4, y + size // 2, x + 3 * size // 4, y + size // 2, 1)  # Middle horizontal line

# Draw the letter 'A' in the center of the screen
draw_A(WIDTH // 4, HEIGHT // 4, 30)

# Show the result on the display
ssd.show()


# In[26]:


# הפיכת סטרינג במיקרופייתון 
my_string = "המהב"

def reversed_string(string):
    return "".join(reversed(string))

print(reversed_string(my_string))


# In[ ]:


# הדפסות משולבות בשתי שיטות

import machine
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from writer import Writer
import myfont  # Font to use

def reverse(string):
    return "".join(reversed(string))

# Initialize I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=10000)
ssd = SSD1306_I2C(128, 64, i2c) # אורך ורוחב המסך בפיקסלים

# Instantiate a writer for a specific font
wri = Writer(ssd, myfont)

# הדפסת טקסט בשורות עם מיקומים שונים
Writer.set_textpos(ssd, 0, 0)  # שורה ראשונה
wri.printstring(f':{reverse("שמש")}\n')

Writer.set_textpos(ssd, 9, 0)  # שורה שנייה בגובה 10
wri.printstring(f'{reverse("ירח")}\n')

Writer.set_textpos(ssd, 20, 0)  # שורה שלישית בגובה 20
wri.printstring(f'{reverse("כוכבים")}\n')

Writer.set_textpos(ssd, 30, 0)  # שורה רביעית בגובה 30
wri.printstring(f'{reverse("חלב")}\n')

Writer.set_textpos(ssd, 40, 0)  # שורה חמישית בגובה 40
wri.printstring(f'{reverse("תמרים")}')

Writer.set_textpos(ssd, 50, 0)  # שורה חמישית בגובה 40
wri.printstring(f'{reverse("לחם")}')


# הדפסה במספר שורות עם מרווח של 8 פיקסלים
ssd.text("line 1", 80, 0)   # y = 0
ssd.text("line 2", 80, 8)   # y = 8
ssd.text("line 3", 80, 16)  # y = 16
ssd.text("line 4", 80, 24)  # y = 24
ssd.text("line 5", 80, 32)  # y = 32
ssd.text("line 6", 80, 40)  # y = 40
ssd.text("line 7", 80, 48)  # y = 48
ssd.text("line 8", 80, 56)  # y = 56
ssd.text("line 9", 80, 64)  # y = 56


# הצגת הטקסט על המסך
ssd.show()


# In[ ]:





# In[ ]:




