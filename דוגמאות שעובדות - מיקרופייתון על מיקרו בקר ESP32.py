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
