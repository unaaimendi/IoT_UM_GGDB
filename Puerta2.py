import RPi.GPIO as GPIO

# Connect the Grove PIR Motion Sensor to digital port D8
# SIG,NC,VCC,GND
pir_sensor = 5
 
#GrovePi.pinMode(pir_sensor,"INPUT")

GPIO.setmode(GPIO.BCM)
GPIO.setup(pir_sensor, GPIO.IN)
sensor = GPIO.input(pir_sensor)

while True:
    try:
        # Sense motion, usually human, within the target range
        if (sensor == 1):
            print ("Motion Detected")
        else:
            print ("-")
 
        # if your hold time is less than this, you might not see as many detections
 
    except KeyboardInterrupt:
        GPIO.cleanup()

