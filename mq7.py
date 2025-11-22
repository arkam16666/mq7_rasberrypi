import csv
import os
import time
import board
import digitalio
import adafruit_dht
from datetime import datetime, timedelta

mq7_pin = board.D17 
dhtDevice = adafruit_dht.DHT22(board.D4)

mq7 = digitalio.DigitalInOut(mq7_pin)
mq7.direction = digitalio.Direction.INPUT

print("MQ-7 Gas Sensor Test (Digital Mode)")
print("Waiting for sensor to warm up...")
time.sleep(2) 
print("Ready!")

csv_file_path = "data.csv"
if not os.path.exists(csv_file_path):
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["temp_c", "humidity", "gas_detected", "timestamp"])

while True:
    temp_c = None
    humidity = None
    now = (datetime.now() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")

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

    if not mq7.value: 
        print("Gas/CO Detected!")
    else:
        print("Normal")
        pass

    gas_detected = not mq7.value 
    
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([temp_c, humidity, gas_detected, now])
        
    time.sleep(60)
