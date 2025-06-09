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


