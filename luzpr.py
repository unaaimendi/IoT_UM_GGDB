import time
 
from grove.grove_light_sensor_v1_2 import GroveLightSensor
 
def subir_luz():
    print('Subir luz')

def main():
    # Grove - Light Sensor connected to port A0
    sensor = GroveLightSensor(0)
 
    while True:
        light = sensor.light
        print('light value {}'.format(light))
        if(light < 500):
            subir_luz()

        time.sleep(1)
 
if __name__ == '__main__':
    main()

