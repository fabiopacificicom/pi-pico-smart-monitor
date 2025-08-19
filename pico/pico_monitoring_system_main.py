from machine import I2C, Pin, PWM
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

# --- RGB LED setup (assume common cathode, pins 16/17/18) ---
led_r = PWM(Pin(16))
led_g = PWM(Pin(17))
led_b = PWM(Pin(18))
for led in (led_r, led_g, led_b):
	led.freq(1000)

def set_led(r, g, b):
	# PWM duty: 0=off, 65535=full
	led_r.duty_u16(65535 - int(r * 65535 / 255))
	led_g.duty_u16(65535 - int(g * 65535 / 255))
	led_b.duty_u16(65535 - int(b * 65535 / 255))

# --- Show welcome message ---
lcd_clear()
lcd_move_to(0, 0)
for c in "Welcome":
	lcd_write_char(c)
time.sleep(2)

# --- Main loop ---
while True:
	temp, humi = read_dht11(1)
	# LED logic
	if temp is not None:
		if 20 <= temp <= 30:
			set_led(0, 255, 0)  # Green
		elif temp > 30:
			set_led(255, 0, 0)  # Red
		else:
			set_led(0, 0, 255)  # Blue
	else:
		set_led(0, 0, 0)
	# LCD display
	lcd_clear()
	lcd_move_to(0, 0)
	if temp is not None and humi is not None:
		for c in "T:{}C H:{}%".format(temp, humi):
			lcd_write_char(c)
	else:
		for c in "Sensor Error":
			lcd_write_char(c)
	time.sleep(2)