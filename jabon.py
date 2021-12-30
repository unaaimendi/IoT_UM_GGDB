import time
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger

def main():
	# Grove - Ultrasonic Ranger connected to port D16
	sensor = GroveUltrasonicRanger(16)
	distance_init = sensor.get_distance()
	while True:
		distance = sensor.get_distance()
		print('{} cm'.format(distance))
		if distance_init > distance + 1.5:
			print('Encendido JABON')
		else:
			print('Apagado')
		time.sleep(1)
if __name__ == '__main__':
	main()

