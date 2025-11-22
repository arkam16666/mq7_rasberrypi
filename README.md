# Raspberry Pi Environmental & Gas Monitoring System

A Python-based IoT project that monitors environmental conditions (temperature and humidity) and carbon monoxide/gas levels using DHT22 and MQ-7 sensors connected to a Raspberry Pi.

## 📋 Overview

This system continuously monitors:
- **Temperature** (°C) via DHT22 sensor
- **Humidity** (%) via DHT22 sensor  
- **Gas/CO Detection** via MQ-7 sensor (digital mode)

All readings are logged to a CSV file with timestamps, creating a historical record of environmental conditions.

## 🔧 Hardware Requirements

- **Raspberry Pi** (any model with GPIO pins)
- **DHT22 Temperature & Humidity Sensor**
- **MQ-7 Carbon Monoxide Gas Sensor**
- Jumper wires
- Breadboard (optional)

## 🔌 Wiring Connections

### DHT22 Sensor
- **VCC** → 3.3V or 5V on Raspberry Pi
- **DATA** → GPIO 4 (Pin 7)
- **GND** → Ground

### MQ-7 Gas Sensor
- **VCC** → 5V on Raspberry Pi
- **DOUT** → GPIO 17 (Pin 11) - Digital output mode
- **GND** → Ground

## 📦 Software Dependencies

Install the required Python libraries:

```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade

# Install pip if not already installed
sudo apt-get install python3-pip

# Install required libraries
pip3 install adafruit-circuitpython-dht
sudo apt-get install libgpiod2

# For DHT sensors, you may also need
sudo pip3 install --upgrade adafruit-blinka
```

## 🚀 Installation

1. Clone or download this repository to your Raspberry Pi:
```bash
cd /home/arka/mq7_rasberrypi
```

2. Ensure all dependencies are installed (see above)

3. Connect the sensors according to the wiring diagram

## ▶️ Usage

Run the monitoring script:

```bash
python3 mq7.py
```

The program will:
1. Initialize both sensors
2. Wait 2 seconds for the MQ-7 sensor to warm up
3. Display "Ready!" when initialization is complete
4. Begin continuous monitoring with readings every 60 seconds

### Sample Output

```
MQ-7 Gas Sensor Test (Digital Mode)
Waiting for sensor to warm up...
Ready!
[2025-11-22 17:23:00] Temp: 28.5°C  Humidity: 65.3%
Normal
[2025-11-22 17:24:00] Temp: 28.6°C  Humidity: 65.1%
Gas/CO Detected!
```

## 📊 Data Logging

All sensor readings are automatically saved to `data.csv` with the following columns:

| Column | Description |
|--------|-------------|
| `temp_c` | Temperature in Celsius |
| `humidity` | Relative humidity percentage |
| `gas_detected` | Boolean (True if gas/CO detected, False if normal) |
| `timestamp` | Date and time of reading (GMT+7 timezone) |

### CSV Example

```csv
temp_c,humidity,gas_detected,timestamp
28.5,65.3,False,2025-11-22 17:23:00
28.6,65.1,True,2025-11-22 17:24:00
28.4,65.5,False,2025-11-22 17:25:00
```

## 💻 Code Structure

### Initialization
- Configures MQ-7 sensor on GPIO 17 (digital input)
- Configures DHT22 sensor on GPIO 4
- Creates CSV file with headers if it doesn't exist

### Main Loop
1. **Read DHT22 Sensor**: Attempts to read temperature and humidity
2. **Error Handling**: Retries on sensor read failures
3. **Read MQ-7 Sensor**: Checks digital output (LOW = gas detected, HIGH = normal)
4. **Log Data**: Appends all readings to CSV file
5. **Wait**: 60-second delay before next reading

### Timezone Configuration
The code adjusts timestamps by +7 hours to match Thailand timezone (GMT+7):
```python
now = (datetime.now() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
```

## ⚠️ Important Notes

- **MQ-7 Warm-up**: The MQ-7 sensor requires warm-up time (minimum 2 seconds in code, but 24-48 hours recommended for accurate readings)
- **Digital Mode**: This implementation uses the MQ-7 in digital mode (threshold-based detection). For more precise CO level measurements, use analog mode with an ADC
- **Sensor Accuracy**: DHT22 sensors can occasionally fail to read; the code handles this gracefully with retries
- **Power Requirements**: Ensure your Raspberry Pi power supply can handle both sensors

## 🛠️ Troubleshooting

### DHT22 Sensor Read Failures
- Check wiring connections
- Ensure 10K pull-up resistor between DATA and VCC (often built into modules)
- Add delays between readings (current: 60 seconds, which is adequate)

### MQ-7 Not Detecting Gas
- Allow proper warm-up time (24-48 hours for first use)
- Check wiring to GPIO 17
- Verify sensor module has power LED lit
- Adjust sensitivity potentiometer on MQ-7 module if available

### Permission Errors
Run the script with sudo if you encounter GPIO permission errors:
```bash
sudo python3 mq7.py
```

## 🔄 Running on Startup (Optional)

To run the script automatically on boot:

1. Create a systemd service:
```bash
sudo nano /etc/systemd/system/mq7-monitor.service
```

2. Add the following content:
```ini
[Unit]
Description=MQ7 Environmental Monitoring
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/arka/mq7_rasberrypi/mq7.py
WorkingDirectory=/home/arka/mq7_rasberrypi
StandardOutput=inherit
StandardError=inherit
Restart=always
User=arka

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl enable mq7-monitor.service
sudo systemctl start mq7-monitor.service
```

## 📈 Future Enhancements

- Add analog reading support for precise CO concentration (ppm)
- Implement data visualization dashboard
- Set up alerts for high temperature/humidity or gas detection
- Upload data to cloud services (ThingSpeak, Google Sheets, etc.)
- Add more sensors (air quality, pressure, etc.)

## 📝 License

This project is open source and available for educational and personal use.

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

---

**Author**: IoT Environmental Monitoring Project  
**Last Updated**: November 2025
