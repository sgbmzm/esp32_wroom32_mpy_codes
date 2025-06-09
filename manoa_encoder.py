
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


