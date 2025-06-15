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



