# sun_moon.py MicroPython Port of lunarmath.c
# Calculate sun and moon rise and set times for any date and location

# Licensing and copyright: see README.md

# Source "Astronomy on the Personal Computer" by Montenbruck and Pfleger
# ISBN 978-3-540-67221-0

# Port from C++ to MicroPython performed by Peter Hinch 2023.
# Withcontributions from Raul Kompaß and Marcus Mendenhall: see
# https://github.com/orgs/micropython/discussions/13075
# Raul Kompaß perfomed major simplification of the maths for deriving rise and
# set_times with improvements in precision with 32-bit floats.

# Moon phase now in separate module

import time
from math import sin, cos, sqrt, fabs, atan, radians, floor, pi

LAT = 53.29756504536339  # Local defaults
LONG = -2.102811634540558

# MicroPython wanton epochs:
# time.gmtime(0)[0] = 1970 or 2000 depending on platform.
# On CPython:
# (date(2000, 1, 1) - date(1970, 1, 1)).days * 24*60*60 = 946684800
# (date(2000, 1, 1) - date(1970, 1, 1)).days = 10957

# Return time now in days relative to platform epoch.
# System time is set to local time, and MP has no concept of this. Hence
# time.time() returns secs since epoch 00:00:00 local time. If lto is local time
# offset to UTC, provided -12 < lto < 12, the effect of rounding ensures the
# right number of days for platform epoch at UTC.
def now_days() -> int:
    secs_per_day = 86400  # 24 * 3600
    t = RiSet.mtime()  # Machine time as int. Can be overridden for test.
    t -= t % secs_per_day  # Previous Midnight
    return round(t / secs_per_day)  # Days since datum


def quad(ym, yz, yp):
    # See Astronomy on the PC P48-49, plus contribution from Marcus Mendenhall
    # finds the parabola throuh the three points (-1,ym), (0,yz), (1, yp)
    # and returns the values of x where the parabola crosses zero
    # (roots of the quadratic)
    # and the number of roots (0, 1 or 2) within the interval [-1, 1]
    nz = 0
    a = 0.5 * (ym + yp) - yz
    b = 0.5 * (yp - ym)
    c = yz
    xe = -b / (2 * a)
    ye = (a * xe + b) * xe + c
    dis = b * b - 4.0 * a * c  # discriminant of y=a*x^2 +bx +c
    if dis > 0:  # parabola has roots
        if b < 0:
            z2 = (-b + sqrt(dis)) / (2 * a)  # z2 is larger root in magnitude
        else:
            z2 = (-b - sqrt(dis)) / (2 * a)
        z1 = (c / a) / z2  # z1 is always closer to zero
        if fabs(z1) <= 1.0:
            nz += 1
        if fabs(z2) <= 1.0:
            nz += 1
        if z1 < -1.0:
            z1 = z2
        return nz, z1, z2, ye
    return 0, 0, 0, 0  # No roots


# **** GET MODIFIED JULIAN DATE FOR DAY RELATIVE TO TODAY ****

# Returns modified julian day number defined as mjd = jd - 2400000.5
# Deals only in integer MJD's: the JD of just after midnight will always end in 0.5
# hence the MJD of an integer day number will always be an integer

# Re platform comparisons get_mjd returns the same value regardless of
# the platform's epoch: integer days since 00:00 UTC on 17 November 1858.
def get_mjd(ndays: int = 0) -> int:
    secs_per_day = 86400  # 24 * 3600
    days_from_epoch = now_days() + ndays  # Days since platform epoch
    mjepoch = 40587  # Modified Julian date of C epoch (1 Jan 70)
    if time.gmtime(0)[0] == 2000:
        mjepoch += 10957
    return mjepoch + days_from_epoch  # Convert days from 1 Jan 70 to MJD


def frac(x):
    return x % 1


# Convert rise or set time to int. These can be None (no event).
def to_int(x):
    return None if x is None else round(x)


def minisun(t):
    # Output sin(dec), cos(dec), ra
    # returns the ra and dec of the Sun
    # in decimal hours, degs referred to the equinox of date and using
    # obliquity of the ecliptic at J2000.0 (small error for +- 100 yrs)
    # takes t centuries since J2000.0. Claimed good to 1 arcmin
    coseps = 0.9174805004
    sineps = 0.397780757938

    m = 2 * pi * frac(0.993133 + 99.997361 * t)
    dl = 6893.0 * sin(m) + 72.0 * sin(2 * m)
    l = 2 * pi * frac(0.7859453 + m / (2 * pi) + (6191.2 * t + dl) / 1296000)
    sl = sin(l)
    x = cos(l)
    y = coseps * sl
    z = sineps * sl
    # rho = sqrt(1 - z * z)
    # dec = (360.0 / 2 * pi) * atan(z / rho)
    # ra = ((48.0 / (2 * pi)) * atan(y / (x + rho))) % 24
    return x, y, z


def minimoon(t):
    # takes t and returns the geocentric ra and dec
    # claimed good to 5' (angle) in ra and 1' in dec
    # tallies with another approximate method and with ICE for a couple of dates
    arc = 206264.8062
    coseps = 0.9174805004
    sineps = 0.397780757938

    l0 = frac(0.606433 + 1336.855225 * t)  # mean longitude of moon
    l = 2 * pi * frac(0.374897 + 1325.552410 * t)  # mean anomaly of Moon
    ls = 2 * pi * frac(0.993133 + 99.997361 * t)  # mean anomaly of Sun
    d = 2 * pi * frac(0.827361 + 1236.853086 * t)  # difference in longitude of moon and sun
    f = 2 * pi * frac(0.259086 + 1342.227825 * t)  # mean argument of latitude

    # corrections to mean longitude in arcsec
    dl = 22640 * sin(l)
    dl += -4586 * sin(l - 2 * d)
    dl += +2370 * sin(2 * d)
    dl += +769 * sin(2 * l)
    dl += -668 * sin(ls)
    dl += -412 * sin(2 * f)
    dl += -212 * sin(2 * l - 2 * d)
    dl += -206 * sin(l + ls - 2 * d)
    dl += +192 * sin(l + 2 * d)
    dl += -165 * sin(ls - 2 * d)
    dl += -125 * sin(d)
    dl += -110 * sin(l + ls)
    dl += +148 * sin(l - ls)
    dl += -55 * sin(2 * f - 2 * d)

    # simplified form of the latitude terms
    s = f + (dl + 412 * sin(2 * f) + 541 * sin(ls)) / arc
    h = f - 2 * d
    n = -526 * sin(h)
    n += +44 * sin(l + h)
    n += -31 * sin(-l + h)
    n += -23 * sin(ls + h)
    n += +11 * sin(-ls + h)
    n += -25 * sin(-2 * l + f)
    n += +21 * sin(-l + f)

    # ecliptic long and lat of Moon in rads
    l_moon = 2 * pi * frac(l0 + dl / 1296000)
    b_moon = (18520.0 * sin(s) + n) / arc

    # equatorial coord conversion - note fixed obliquity
    cb = cos(b_moon)
    x = cb * cos(l_moon)
    v = cb * sin(l_moon)
    w = sin(b_moon)
    y = coseps * v - sineps * w
    z = sineps * v + coseps * w
    # rho = sqrt(1.0 - z * z)
    # dec = (360.0 / 2 * pi) * atan(z / rho)
    # ra = ((48.0 / (2 * pi)) * atan(y / (x + rho))) % 24
    return x, y, z


class RiSet:
    verbose = True
    # Riset.mtime() returns machine time as an int. The class variable tim is for
    # test purposes only and allows the hardware clock to be overridden
    tim = None

    @classmethod
    def mtime(cls):
        return round(time.time()) if cls.tim is None else cls.tim

    @classmethod
    def set_time(cls, t):  # Given time from Unix epoch set time
        if time.gmtime(0)[0] == 2000:  # Machine epoch
            t -= 10957 * 86400
        cls.tim = t

    def __init__(self, lat=LAT, long=LONG, lto=0, tl=None, dst=lambda x: x):  # Local defaults
        self.sglat = sin(radians(lat))
        self.cglat = cos(radians(lat))
        self.long = long
        self.check_lto(lto)  # -15 < lto < 15
        self.lto = round(lto * 3600)  # Localtime offset in secs
        self.tlight = sin(radians(tl)) if tl is not None else tl
        self.dst = dst
        self.mjd = None  # Current integer MJD
        # Times in integer secs from midnight on current day (in machine time adjusted for DST)
        # [sunrise, sunset, moonrise, moonset, cvend, cvstart]
        self._times = [None] * 6
        self.set_day()  # Initialise to today's date
        if RiSet.verbose:
            t = time.localtime()
            print(f"Machine time: {t[2]:02}/{t[1]:02}/{t[0]:4} {t[3]:02}:{t[4]:02}:{t[5]:02}")
            RiSet.verbose = False

    # ***** API start *****
    # Examine Julian dates either side of current one to cope with localtime.
    # 707μs on RP2040 at standard clock and with local time == UTC
    def set_day(self, day: int = 0):
        mjd = get_mjd(day)
        if self.mjd is None or self.mjd != mjd:
            spd = 86400  # Secs per day
            # ._t0 is time of midnight (local time) in secs since MicroPython epoch
            # time.time() assumes MicroPython clock is set to geographic local time
            self._t0 = ((self.mtime() + day * spd) // spd) * spd
            self.update(mjd)  # Recalculate rise and set times
        return self  # Allow r.set_day().sunrise()

    # variants: 0 secs since 00:00:00 localtime. 1 secs since MicroPython epoch
    # (relies on system being set to localtime). 2 human-readable text.
    def sunrise(self, variant: int = 0):
        return self._format(self._times[0], variant)

    def sunset(self, variant: int = 0):
        return self._format(self._times[1], variant)

    def moonrise(self, variant: int = 0):
        return self._format(self._times[2], variant)

    def moonset(self, variant: int = 0):
        return self._format(self._times[3], variant)

    def tstart(self, variant: int = 0):
        return self._format(self._times[4], variant)

    def tend(self, variant: int = 0):
        return self._format(self._times[5], variant)

    def set_lto(self, t):  # Update the offset from UTC
        self.check_lto(t)  # No need to recalc beause date is unchanged
        self.lto = round(t * 3600)  # Localtime offset in secs

    def has_risen(self, sun: bool):
        return self.has_x(True, sun)

    def has_set(self, sun: bool):
        return self.has_x(False, sun)

    # Return current state of sun or moon. The moon has a special case where it
    # rises and sets in a 24 hour period. If its state is queried after both these
    # events or before either has occurred, the current state depends on the order
    # in which they occurred (the sun always sets afer it rises).
    # The case is (.has_risen(False) and .has_set(False)) and if it occurs then
    # .moonrise() and .moonset() must return valid times (not None).
    def is_up(self, sun: bool):
        hr = self.has_risen(sun)
        hs = self.has_set(sun)
        rt = self.sunrise() if sun else self.moonrise()
        st = self.sunset() if sun else self.moonset()
        if rt is None and st is None:  # No event in 24hr period.
            return self.above_horizon(sun)
        # Handle special case: moon has already risen and set or moon has neither
        # risen nor set, yet there is a rise and set event in the day
        if not (hr ^ hs):
            if not ((rt is None) or (st is None)):
                return rt > st
        if not (hr or hs):  # No event has yet occurred
            return rt is None

        return hr and not hs  # Default case: up if it's risen but not set

    # ***** API end *****

    # Generic has_risen/has_set function
    def has_x(self, risen: bool, sun: bool):
        if risen:
            st = self.sunrise(1) if sun else self.moonrise(1)  # DST- adjusted machine time
        else:
            st = self.sunset(1) if sun else self.moonset(1)
        if st is not None:
            return st < self.dst(self.mtime())  # Machine time
        return False

    def above_horizon(self, sun: bool):
        now = self.mtime() + self.lto  # UTC
        tutc = (now % 86400) / 3600  # Time as UTC hour of day (float)
        return self.sin_alt(tutc, sun) > 0  # Object is above horizon

    # Re-calculate rise and set times
    def update(self, mjd):
        for x in range(len(self._times)):
            self._times[x] = None  # Assume failure
        days = (1, 2) if self.lto < 0 else (1,) if self.lto == 0 else (0, 1)
        tr = None  # Assume no twilight calculations
        ts = None
        for day in days:
            self.mjd = mjd + day - 1
            sr, ss = self.rise_set(True, False)  # Sun
            # Twilight: only calculate if required
            if self.tlight is not None:
                tr, ts = self.rise_set(True, True)
            mr, ms = self.rise_set(False, False)  # Moon
            # Adjust for local time and DST. Store in ._times if value is in
            # 24-hour local time window
            self.adjust((sr, ss, mr, ms, tr, ts), day)
        self.mjd = mjd

    def adjust(self, times, day):
        for idx, n in enumerate(times):
            if n is not None:
                n += self.lto + (day - 1) * 86400
                n = self.dst(n)  # Adjust for DST on day of n
                h = n // 3600
                if 0 <= h < 24:
                    self._times[idx] = n

    def _format(self, n, variant):
        if (n is not None) and (variant & 4):  # Machine clock set to UTC
            variant &= 0x03
            n = self.dst(n + self._t0) - self._t0
        if variant == 0:  # Default: secs since Midnight (local time)
            return n
        elif variant == 1:  # Secs since epoch of MicroPython platform
            return None if n is None else n + self._t0
        # variant == 2
        if n is None:
            return "--:--:--"
        else:
            hr, tmp = divmod(n, 3600)
            mi, sec = divmod(tmp, 60)
            return f"{hr:02d}:{mi:02d}:{sec:02d}"

    def check_lto(self, t):
        if not -15 < t < 15:
            raise ValueError("Invalid local time offset.")

    # See https://github.com/orgs/micropython/discussions/13075
    def lstt(self, t, h):
        # Takes the mjd and the longitude (west negative) and then returns
        # the local sidereal time in degrees. Im using Meeus formula 11.4
        # instead of messing about with UTo and so on
        # modified to use the pre-computed 't' value from sin_alt
        d = t * 36525
        df = frac(0.5 + h / 24)
        c1 = 360
        c2 = 0.98564736629
        dsum = c1 * df + c2 * d  # dsum is still ~ 9000 on average, losing precision
        lst = 280.46061837 + dsum + t * t * (0.000387933 - t / 38710000)
        return lst

    def sin_alt(self, hour, sun):
        # Returns the sine of the altitude of the object (moon or sun)
        # at an hour relative to the current date (mjd)
        func = minisun if sun else minimoon
        mjd = (self.mjd - 51544.5) + hour / 24.0
        # mjd = self.mjd + hour / 24.0
        t = mjd / 36525.0
        x, y, z = func(t)
        tl = self.lstt(t, hour) + self.long  # Local mean sidereal time adjusted for logitude
        return self.sglat * z + self.cglat * (x * cos(radians(tl)) + y * sin(radians(tl)))

    # Calculate rise and set times of sun or moon for the current MJD. Times are
    # relative to that 24 hour period.
    def rise_set(self, sun, tl):
        t_rise = None  # Rise and set times in secs from midnight
        t_set = None
        if tl:
            sinho = -self.tlight
        else:
            sinho = sin(radians(-0.833)) if sun else sin(radians(8 / 60))
        # moonrise taken as centre of moon at +8 arcmin
        # sunset upper limb simple refraction
        # The loop finds the sin(alt) for sets of three consecutive
        # hours, and then tests for a single zero crossing in the interval
        # or for two zero crossings in an interval for for a grazing event
        yp = self.sin_alt(0, sun) - sinho
        for hour in range(1, 24, 2):
            ym = yp
            yz = self.sin_alt(hour, sun) - sinho
            yp = self.sin_alt(hour + 1, sun) - sinho
            nz, z1, z2, ye = quad(ym, yz, yp)  # Find horizon crossings
            if nz == 1:  # One crossing found
                if ym < 0.0:
                    t_rise = 3600 * (hour + z1)
                else:
                    t_set = 3600 * (hour + z1)
            # case where two events are found in this interval
            # (rare but whole reason we are not using simple iteration)
            elif nz == 2:
                if ye < 0.0:
                    t_rise = 3600 * (hour + z2)
                    t_set = 3600 * (hour + z1)
                else:
                    t_rise = 3600 * (hour + z1)
                    t_set = 3600 * (hour + z2)

            if t_rise is not None and t_set is not None:
                break  # All done
        return to_int(t_rise), to_int(t_set)  # Convert to int preserving None values
