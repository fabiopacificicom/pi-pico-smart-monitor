from machine import I2C, Pin
import time

# --- Minimal DHT11 read (blocking, bit-bang) ---
def read_dht11(pin):
	d = Pin(pin, Pin.OUT, value=1)
	time.sleep_ms(20)
	d.value(0)
	time.sleep_ms(20)
	d.value(1)
	d.init(Pin.IN)
	while d.value() == 1:
		pass
	while d.value() == 0:
		pass
	while d.value() == 1:
		pass
	data = []
	for i in range(40):
		while d.value() == 0:
			pass
		t = time.ticks_us()
		while d.value() == 1:
			pass
		if time.ticks_diff(time.ticks_us(), t) > 40:
			data.append(1)
		else:
			data.append(0)
	bits = data
	bytes_ = []
	for i in range(0, 40, 8):
		byte = 0
		for j in range(8):
			byte = (byte << 1) | bits[i + j]
		bytes_.append(byte)
	if len(bytes_) == 5 and ((sum(bytes_[:4]) & 0xFF) == bytes_[4]):
		return bytes_[2], bytes_[0]  # temp, humi
	else:
		return None, None

# --- Minimal LCD1602 I2C driver ---
I2C_ADDR = 0x27
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)

def lcd_strobe(data):
	i2c.writeto(I2C_ADDR, bytes([data | 0x04]))
	time.sleep_us(1)
	i2c.writeto(I2C_ADDR, bytes([data & ~0x04]))
	time.sleep_us(50)

def lcd_write4bits(data):
	i2c.writeto(I2C_ADDR, bytes([data]))
	lcd_strobe(data)

def lcd_write_cmd(cmd):
	lcd_write4bits((cmd & 0xF0) | 0x08)
	lcd_write4bits(((cmd << 4) & 0xF0) | 0x08)

def lcd_write_char(char):
	val = ord(char)
	lcd_write4bits((val & 0xF0) | 0x09)
	lcd_write4bits(((val << 4) & 0xF0) | 0x09)

def lcd_clear():
	lcd_write_cmd(0x01)
	time.sleep_ms(2)

def lcd_move_to(col, row):
	addr = 0x80 + (0x40 * row) + col
	lcd_write_cmd(addr)

# LCD init
time.sleep_ms(50)
lcd_write4bits(0x30 | 0x08)
time.sleep_ms(5)
lcd_write4bits(0x30 | 0x08)
time.sleep_us(150)
lcd_write4bits(0x30 | 0x08)
lcd_write4bits(0x20 | 0x08)
lcd_write_cmd(0x28)
lcd_write_cmd(0x0C)
lcd_write_cmd(0x06)
lcd_clear()



# --- ws2812b RGB LED bar setup (using rdb.py logic, data on GPIO15) ---
import array
import rp2

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
	T1 = 2
	T2 = 5
	T3 = 3
	wrap_target()
	label("bitloop")
	out(x, 1)               .side(0)    [T3 - 1]
	jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
	jmp("bitloop")          .side(1)    [T2 - 1]
	label("do_zero")
	nop()                   .side(0)    [T2 - 1]
	wrap()

class ws2812b:
	def __init__(self, num_leds, state_machine, pin, delay=0.001):
		self.pixels = array.array("I", [0 for _ in range(num_leds)])
		self.sm = rp2.StateMachine(state_machine, ws2812, freq=8000000, sideset_base=Pin(pin))
		self.sm.active(1)
		self.num_leds = num_leds
		self.delay = delay
		self.brightnessvalue = 255
	def brightness(self, brightness = None):
		if brightness == None:
			return self.brightnessvalue
		else:
			if (brightness < 1):
				brightness = 1
		if (brightness > 255):
			brightness = 255
		self.brightnessvalue = brightness
	def set_pixel(self, pixel_num, red, green, blue):
		blue = round(blue * (self.brightness() / 255))
		red = round(red * (self.brightness() / 255))
		green = round(green * (self.brightness() / 255))
		self.pixels[pixel_num] = blue | red << 8 | green << 16
	def show(self):
		for i in range(self.num_leds):
			self.sm.put(self.pixels[i],8)
		time.sleep(self.delay)
	def fill(self, red, green, blue):
		for i in range(self.num_leds):
			self.set_pixel(i, red, green, blue)
		self.show()

# Initialize ws2812b bar (1 LED, state machine 0, data pin 15)
led_bar = ws2812b(1, 0, 15)

# --- Show welcome message ---
lcd_clear()
lcd_move_to(0, 0)
for c in "Welcome":
	lcd_write_char(c)
time.sleep(2)

# --- Moisture sensor setup (digital, e.g. GP14) ---
moisture_pin = Pin(14, Pin.IN, Pin.PULL_UP)
last_orange = 0

# --- Main loop ---
while True:
	temp, humi = read_dht11(1)
	moisture = moisture_pin.value()  # 1 = wet, 0 = dry
	now = time.ticks_ms()
	show_alert = False
	# Moisture check: flash orange and show alert only briefly
	if moisture == 0:
		if time.ticks_diff(now, last_orange) > 5000:
			led_bar.fill(255, 128, 0)  # Orange
			last_orange = now
			show_alert = True
		else:
			led_bar.fill(0, 0, 0)  # Off between flashes
	# LED bar color logic if not dry
	elif temp is not None:
		if 20 <= temp <= 30:
			led_bar.fill(0, 255, 0)  # Green
		elif temp > 30:
			led_bar.fill(255, 0, 0)  # Red
		else:
			led_bar.fill(0, 0, 255)  # Blue
	else:
		led_bar.fill(0, 0, 0)  # Off

	# LCD display
	lcd_clear()
	lcd_move_to(0, 0)
	if show_alert:
		for c in "Water the plants":
			lcd_write_char(c)
		lcd_move_to(0, 1)
		for c in "Moisture: Dry":
			lcd_write_char(c)
		time.sleep(2)
		continue
	if temp is not None and humi is not None:
		for c in "T:{}C H:{}%".format(temp, humi):
			lcd_write_char(c)
		lcd_move_to(0, 1)
		for c in ("Moisture: Dry" if moisture == 0 else "Moisture: Wet"):
			lcd_write_char(c)
	else:
		for c in "Sensor Error":
			lcd_write_char(c)
	time.sleep(2)
