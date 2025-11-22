# MQ7 & DHT22 Sensor Monitoring

โปรแกรม Python สำหรับติดตามอุณหภูมิ ความชื้น และก๊าซคาร์บอนมอนอกไซด์ (CO) ด้วย Raspberry Pi

## ภาพรวม

ระบบนี้ทำงานตลอด 24 ชั่วโมงเพื่อ:
- วัด**อุณหภูมิ** (°C) จาก DHT22
- วัด**ความชื้น** (%) จาก DHT22
- ตรวจจับ**ก๊าซ/CO** จาก MQ-7 (แบบ digital)
- บันทึกข้อมูลทั้งหมดลงไฟล์ CSV พร้อม timestamp

## การเชื่อมต่อ Hardware

- **DHT22** → GPIO 4 (Pin 7)
- **MQ-7** → GPIO 17 (Pin 11)

## อธิบายโค้ด

### 1. Import Libraries
```python
import csv              # เขียนข้อมูลลง CSV
import os               # เช็คว่าไฟล์มีอยู่หรือไม่
import time             # หน่วงเวลา
import board            # GPIO pins
import digitalio        # อ่านค่า digital
import adafruit_dht     # ไลบรารี DHT22
from datetime import datetime, timedelta
```

### 2. ตั้งค่า Sensors
```python
mq7_pin = board.D17                          # MQ-7 ใช้ GPIO 17
dhtDevice = adafruit_dht.DHT22(board.D4)     # DHT22 ใช้ GPIO 4

mq7 = digitalio.DigitalInOut(mq7_pin)
mq7.direction = digitalio.Direction.INPUT    # ตั้งเป็น input
```

**อธิบาย:**
- `board.D17` และ `board.D4` คือ GPIO pins ที่เชื่อมต่อกับเซนเซอร์
- MQ-7 ตั้งเป็น INPUT เพื่ออ่านสัญญาณ digital (HIGH/LOW)

### 3. สร้างไฟล์ CSV
```python
csv_file_path = "data.csv"
if not os.path.exists(csv_file_path):
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["temp_c", "humidity", "gas_detected", "timestamp"])
```

**อธิบาย:**
- เช็คว่ามีไฟล์ `data.csv` อยู่แล้วหรือไม่
- ถ้าไม่มี → สร้างไฟล์ใหม่และเขียน header row

### 4. Main Loop - อ่านค่าทุก 60 วินาที

#### 4.1 เตรียมตัวแปร
```python
while True:
    temp_c = None
    humidity = None
    now = (datetime.now() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
```

**อธิบาย:**
- ตั้งค่าเริ่มต้นเป็น `None`
- `timedelta(hours=7)` ปรับเวลาเป็น GMT+7 (เวลาไทย)
- Format เป็น `"2025-11-22 17:23:00"`

#### 4.2 อ่านค่า DHT22 (Temperature & Humidity)
```python
try:
    temp_c = dhtDevice.temperature
    humidity = dhtDevice.humidity
    if temp_c is not None and humidity is not None:
        print(f"[{now}] Temp: {temp_c:.1f}°C  Humidity: {humidity:.1f}%")
    else:
        print("Sensor read failed, retrying...")
except RuntimeError as error:
    print(error.args[0])
    time.sleep(2.0)
    continue
except Exception as error:
    dhtDevice.exit()
    raise error
```

**อธิบาย:**
- `dhtDevice.temperature` อ่านอุณหภูมิ
- `dhtDevice.humidity` อ่านความชื้น
- **RuntimeError**: เกิดขึ้นบ่อยกับ DHT22 (เซนเซอร์ไม่พร้อม) → รอ 2 วินาทีแล้วลองใหม่
- **Exception อื่นๆ**: ปิดเซนเซอร์และ raise error

#### 4.3 อ่านค่า MQ-7 (Gas Detection)
```python
if not mq7.value: 
    print("Gas/CO Detected!")
else:
    print("Normal")

gas_detected = not mq7.value
```

**อธิบาย:**
- `mq7.value` คืนค่า `True` (HIGH) หรือ `False` (LOW)
- เซนเซอร์ MQ-7 output = **LOW (False)** เมื่อ**ตรวจจับก๊าซ**
- เซนเซอร์ MQ-7 output = **HIGH (True)** เมื่อ**ปกติ**
- `not mq7.value` เปลี่ยนเป็น `True` = ตรวจจับก๊าซ, `False` = ปกติ

#### 4.4 บันทึกข้อมูลลง CSV
```python
with open(csv_file_path, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([temp_c, humidity, gas_detected, now])
```

**อธิบาย:**
- `mode='a'` = append (เพิ่มข้อมูลต่อท้าย ไม่ลบข้อมูลเก่า)
- เขียน 4 columns: อุณหภูมิ, ความชื้น, ตรวจจับก๊าซ, เวลา

#### 4.5 หน่วงเวลา
```python
time.sleep(60)
```

**อธิบาย:**
- รอ 60 วินาที (1 นาที) ก่อนอ่านค่าใหม่

## ผลลัพธ์

### หน้าจอ Terminal
```
MQ-7 Gas Sensor Test (Digital Mode)
Waiting for sensor to warm up...
Ready!
[2025-11-22 17:23:00] Temp: 28.5°C  Humidity: 65.3%
Normal
[2025-11-22 17:24:00] Temp: 28.6°C  Humidity: 65.1%
Gas/CO Detected!
```

### ไฟล์ data.csv
```csv
temp_c,humidity,gas_detected,timestamp
28.5,65.3,False,2025-11-22 17:23:00
28.6,65.1,True,2025-11-22 17:24:00
28.4,65.5,False,2025-11-22 17:25:00
```

## จุดสำคัญ

⚠️ **MQ-7 Digital Mode**
- โค้ดนี้ใช้ MQ-7 แบบ **digital** (ตรวจจับ HIGH/LOW)
- ไม่สามารถวัดความเข้มข้นของก๊าซ (ppm) ได้
- ถ้าต้องการค่า ppm → ใช้ analog mode + ADC

⏰ **Timezone**
- เวลาปรับเป็น GMT+7 (เวลาไทย) ด้วย `timedelta(hours=7)`

🔄 **Error Handling**
- DHT22 อาจอ่านค่าไม่ได้บ้าง → โค้ดจะ retry อัตโนมัติ

## การรันโปรแกรม

```bash
python3 mq7.py
```

---

**Hardware:** Raspberry Pi + DHT22 + MQ-7  
**Language:** Python 3
