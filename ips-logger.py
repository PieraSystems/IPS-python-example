import serial
import serial.tools.list_ports
import os
import time, sched
from datetime import datetime

# Set delay between averages, in seconds
duration = 5

try:
    os.mkdir("logs")
except (FileExistsError):
    pass

s = sched.scheduler(time.time, time.sleep)

pc_buffers = [] 
min_averages = []
serial_con = []
log_names = []
valid_keys = ["PC0.1", "PC0.3", "PC0.5", "PC1.0", "PC2.5", "PC5.0", "PC10", "PM0.1", "PM0.3", "PM0.5", "PM1.0", "PM2.5", "PM5.0", "PM10"]

def print_serial(sc):
    for index, ser in enumerate(serial_con):
        ser_bytes = ser.readline()
        ser.flushOutput()
        decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
        # Uncomment to show all output
        # print(decoded_bytes)
        serial_values = decoded_bytes.split(',')
        parsed_values = {}
        for index2, value in enumerate(serial_values):
            if value in valid_keys:
                # print(serial_values[index2 + 1])
                parsed_values[value] = serial_values[index2 + 1]
        if len(parsed_values) >= 3:
            pc_buffers[index].append(parsed_values)
        if ips_devices[index][0] == 'C' and len(parsed_values) >= 3:
            # Get device names (assumes default output)
            if serial_values[len(serial_values)-2][0] == 'I':
                ips_devices[index] = serial_values[len(serial_values)-2]
            else:
                ips_devices[index] = serial_values[len(serial_values)-1]
        
    s.enter(1, 2, print_serial, (sc,))

def minute_average(sc):
    print(str(duration) + " second averages: ")
    for index, ser in enumerate(serial_con):
        reading_count = len(pc_buffers[index])
        pc01sum = 0
        pc03sum = 0
        pc05sum = 0
        pc10sum = 0
        pc25sum = 0
        pc50sum = 0
        pc100sum = 0
        pm01sum = 0
        pm03sum = 0
        pm05sum = 0
        pm10sum = 0
        pm25sum = 0
        pm50sum = 0
        pm100sum = 0
        for reading in pc_buffers[index]:
            pc01sum += int(reading.get("PC0.1", 0))
            pc03sum += int(reading.get("PC0.3", 0))
            pc05sum += int(reading.get("PC0.5", 0))
            pc10sum += int(reading.get("PC1.0", 0))
            pc25sum += int(reading.get("PC2.5", 0))
            pc50sum += int(reading.get("PC5.0", 0))
            pc100sum += int(reading.get("PC10", 0))
            pm01sum += float(reading.get("PM0.1", 0))
            pm03sum += float(reading.get("PM0.3", 0))
            pm05sum += float(reading.get("PM0.5", 0))
            pm10sum += float(reading.get("PM1.0", 0))
            pm25sum += float(reading.get("PM2.5", 0))
            pm50sum += float(reading.get("PM5.0", 0))
            pm100sum += float(reading.get("PM10", 0))
        min_averages[index].append({
            "PC0.1": round(pc01sum/reading_count), 
            "PC0.3": round(pc03sum/reading_count),
            "PC0.5": round(pc05sum/reading_count),
            "PC1.0": round(pc10sum/reading_count),
            "PC2.5": round(pc25sum/reading_count),
            "PC5.0": round(pc50sum/reading_count),
            "PC10": round(pc100sum/reading_count),
            "PM0.1": pm01sum/reading_count, 
            "PM0.3": pm03sum/reading_count,
            "PM0.5": pm05sum/reading_count,
            "PM1.0": pm10sum/reading_count,
            "PM2.5": pm25sum/reading_count,
            "PM5.0": pm50sum/reading_count,
            "PM10": pm100sum/reading_count,
            })
        pc_buffers[index].clear()
        print("{} - PC0.1: {} PC0.3: {} PC0.5: {} PC1.0: {} PC2.5: {} PC5.0: {} PC10: {}".format(ips_devices[index], min_averages[index][len(min_averages[index])-1]["PC0.1"], min_averages[index][len(min_averages[index])-1]["PC0.3"], min_averages[index][len(min_averages[index])-1]["PC0.5"], min_averages[index][len(min_averages[index])-1]["PC1.0"], min_averages[index][len(min_averages[index])-1]["PC2.5"], min_averages[index][len(min_averages[index])-1]["PC5.0"], min_averages[index][len(min_averages[index])-1]["PC10"]))
        print("{} - PM0.1: {:.3f} PM0.3: {:.3f} PM0.5: {:.3f} PM1.0: {:.3f} PM2.5: {:.3f} PM5.0: {:.3f} PM10: {:.3f}".format(ips_devices[index], min_averages[index][len(min_averages[index])-1]["PM0.1"], min_averages[index][len(min_averages[index])-1]["PM0.3"], min_averages[index][len(min_averages[index])-1]["PM0.5"], min_averages[index][len(min_averages[index])-1]["PM1.0"], min_averages[index][len(min_averages[index])-1]["PM2.5"], min_averages[index][len(min_averages[index])-1]["PM5.0"], min_averages[index][len(min_averages[index])-1]["PM10"]))
        f = open("logs/" + log_names[index], "a")
        f.write("{},{},{},{},{},{},{},".format(min_averages[index][len(min_averages[index])-1]["PC0.1"], min_averages[index][len(min_averages[index])-1]["PC0.3"], min_averages[index][len(min_averages[index])-1]["PC0.5"], min_averages[index][len(min_averages[index])-1]["PC1.0"], min_averages[index][len(min_averages[index])-1]["PC2.5"], min_averages[index][len(min_averages[index])-1]["PC5.0"], min_averages[index][len(min_averages[index])-1]["PC10"]))
        f.write("{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},".format(min_averages[index][len(min_averages[index])-1]["PM0.1"], min_averages[index][len(min_averages[index])-1]["PM0.3"], min_averages[index][len(min_averages[index])-1]["PM0.5"], min_averages[index][len(min_averages[index])-1]["PM1.0"], min_averages[index][len(min_averages[index])-1]["PM2.5"], min_averages[index][len(min_averages[index])-1]["PM5.0"], min_averages[index][len(min_averages[index])-1]["PM10"]))
        f.write("{}\n".format(ips_devices[index]))
        f.close()
    s.enter(duration, 1, minute_average, (sc,))

print("IPS Testing Tool v0.3")
print(" Exit - Ctrl-C")
print("")
time.sleep(0.2)
print("Detected devices:")
ports = serial.tools.list_ports.comports()
ips_devices = []

for index, port in enumerate(ports, start=1):
    vid = int(0 if port.pid is None else port.vid)
    print("{}: {} [{}] - {}".format(index, hex(vid), port.serial_number, port.description))
    if vid == 0x10c4:
        ips_devices.append(str(port.name))

print("")
print("{} devices found with product ID 0x10c4.".format(len(ips_devices)))
print("")
if len(ips_devices) < 1:
    print("No devices found")
    quit()
input('Press Enter to begin (Ctrl-C to exit) ')
print("")
print("Warming up devices...")

now = datetime.now()
time_now = now.strftime("%m%d%y-%H%M%S")

for device in ips_devices:
    # print(device)
    serial_con.append(serial.Serial(device, 115200))
    pc_buffers.append([])
    min_averages.append([])
    log_name = time_now + "-" + device + ".csv"
    log_names.append(log_name)
    f = open("logs/" + log_name, "a")
    f.write("pc01,pc03,pc05,pc10,pc25,pc50,pc100,pm01,pm03,pm05,pm10,pm25,pm50,pm100,serial\n")
    f.close()
    
# Sending UART command examples
# ser.write('$Won=200\r\n'.encode())
# ser.write('$Winterval=1\r\n'.encode())
# ser.write('$Wpmd=0\r\n'.encode())
# ser.write('$Wunit=1\r\n'.encode())

time.sleep(5)
for index, ser in enumerate(serial_con):
    ser.flushOutput()
time.sleep(1)
print("Calculating " + str(duration) + " second averages...")


s.enter(duration, 1, minute_average, (s,))
s.enter(1, 2, print_serial, (s,))
s.run()