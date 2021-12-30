import logging
import time,sys
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
from grove.grove_mini_pir_motion_sensor import GroveMiniPIRMotionSensor
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger
from Seeed_Python_DHT.seeed_dht import DHT
from grove.grove_moisture_sensor import GroveMoistureSensor
from grove.button import Button
from grove.grove_ryb_led_button import GroveLedButton
from grove.grove_light_sensor_v1_2 import GroveLightSensor
from grove.grove_servo import GroveServo
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

# Configuration of logger, in this case it will send messages to console
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

log = logging.getLogger(__name__)

thingsboard_server = 'thingsboard.cloud'
access_token = 'whjHqjtGmVYpjkXR1KfC'


if sys.platform == 'uwp':
    import winrt_smbus as smbus
    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)

# this device has two I2C addresses
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e

def main():
    
    # Grove - mini PIR motion pir_sensor connected to port D5
    pir_sensor = GroveMiniPIRMotionSensor(5)

    # Grove - Ultrasonic Ranger connected to port D16
    ultrasonic_sensor = GroveUltrasonicRanger(16)

    # Grove - RFID Sensor connected to serial
    reader = SimpleMFRC522()

    # Grove - Light Sensor connected to port A0
    light_sensor = GroveLightSensor(0)
    # Grove - Temperature&Humidity Sensor connected to port D22
    dht_sensor = DHT('11', 22)
    def tempHum():
        while True:
            humi, temp = dht_sensor.read()
            print('temperature {}C, humidity {}%'.format(temp, humi))
            time.sleep(1)
    
    def getLightState():
        while True:
            light_state = lightSensor.light
            print('light value {}'.format(light_state))
            if(light_state < 500):
                subir_luz()

            time.sleep(1)
            
    def subir_luz():
        print('Subir luz')
        
    def getDistanceGrifo():
        # Grove - Ultrasonic Ranger connected to port D16
        distance_init = ultrasonic_sensor.get_distance()
        while True:
            distanceGR = ultrasonic_sensor.get_distance()
            print('{} cm'.format(distanceGR))
            if distance_init > distanceGR + 1.5:
                print('Encendido AGUA')
            else:
                print('Apagado')
            time.sleep(1)
    

        '''
                    PUERTA
        '''

    # set backlight to (R,G,B) (values from 0..255 for each)
    def setRGB(r,g,b):
        bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
        bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
        bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
        bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
        bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
        bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)

    # send command to display (no need for external use)
    def textCommand(cmd):
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)

    # set display text \n for second line(or auto wrap)
    def setText(text):
        textCommand(0x01) # clear display
        time.sleep(.05)
        textCommand(0x08 | 0x04) # display on, no cursor
        textCommand(0x28) # 2 lines
        time.sleep(.05)
        count = 0
        row = 0
        for c in text:
            if c == '\n' or count == 16:
                count = 0
                row += 1
                if row == 2:
                    break
                textCommand(0xc0)
                if c == '\n':
                    continue
            count += 1
            bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

    #Update the display without erasing the display
    def setText_norefresh(text):
        textCommand(0x02) # return home
        time.sleep(.05)
        textCommand(0x08 | 0x04) # display on, no cursor
        textCommand(0x28) # 2 lines
        time.sleep(.05)
        count = 0
        row = 0
        while len(text) < 32: #clears the rest of the screen
            text += ' '
        for c in text:
            if c == '\n' or count == 16:
                count = 0
                row += 1
                if row == 2:
                    break
                textCommand(0xc0)
                if c == '\n':
                    continue
            count += 1
            bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))


    def abrirPuerta():
        print("Puerta abierta")
        
    # Create a custom character (from array of row patterns)
    def create_char(location, pattern):
        """
        Writes a bit pattern to LCD CGRAM

        Arguments:
        location -- integer, one of 8 slots (0-7)
        pattern -- byte array containing the bit pattern, like as found at
                   https://omerk.github.io/lcdchargen/
        """
        location &= 0x07 # Make sure location is 0-7
        textCommand(0x40 | (location << 3))
        bus.write_i2c_block_data(DISPLAY_TEXT_ADDR, 0x40, pattern)

    # example code
    def leerPuerta():
        try:
            while True:
                setText("Lab 3\nPase su tarjeta")
                setRGB(0,102,204)
            
                idPuerta, nombreTarjeta = reader.read()
                if (nombreTarjeta.replace(" ","") == "Jon"):
                    setText("Puerta abierta\nCierre al pasar")
                    setRGB(0,255,0)
                    abrirPuerta()
                    time.sleep(5)
                    
                else:
                    setText("\nPermiso denegado")
                    setRGB(255,0,0)
                    time.sleep(5)
                setText("Lab 3\nPase su tarjeta")
                setRGB(0,102,204)
           
        except KeyboardInterrupt:
            GPIO.cleanup()
            

            '''
                PUERTA FIN
            '''
            '''
                GRABAR PUERTA
            '''
                    
    def grabarNombre():
        try:
            nombreTarjeta = input('New data:')
            print("Now place your tag to write")
            reader.write(nombreTarjeta)
            print("Written")
        finally:
            GPIO.cleanup()
            
        
            '''
                GRABAR PUERTA FIN
            '''
                        
    def getDistanceSecador():
        estadoSEC = False;
        distance_init = ultrasonic_sensor.get_distance()
        while True:
            distanceSEC = ultrasonic_sensor.get_distance()
            print('{} cm'.format(distanceSEC))
            if distance_init > distanceSEC + 1.5:
                print('Encendido SECADOR')
                estadoSEC = True;
            else:
                print('Apagado')
                estadoSEC = False;
            time.sleep(1)
            
    '''   
    # Callback for server RPC requests (Used for control servo and led blink)
    def on_server_side_rpc_request(client, request_id, request_body):
        log.info('received rpc: {}, {}'.format(request_id, request_body))
        if request_body['method'] == 'getLightState':
            client.send_rpc_reply(request_id, light_state)
        elif request_body['method'] == 'getDistanceGrifo':
            client.send_rpc_reply(request_id, distanceGR)
        elif request_body['method'] == 'leerPuerta':
            client.send_rpc_reply(request_id, idPuerta, nombreTarjeta)
        elif request_body['method'] == 'grabarNombre':
            client.send_rpc_reply(request_id, nombreTarjeta)
        elif request_body['method'] == 'getDistanceSecador':
            client.send_rpc_reply(request_id, distanceSEC, estadoSEC)
        elif request_body['method'] == 'getDistanceSecador':
            client.send_rpc_reply(request_id, distanceSEC, estadoSEC)
        elif request_body['method'] == 'getDistanceSecador':
            client.send_rpc_reply(request_id, distanceSEC, estadoSEC)
        elif request_body['method'] == 'getDistanceSecador':
            client.send_rpc_reply(request_id, distanceSEC, estadoSEC)
        elif request_body['method'] == 'getDistanceSecador':
            client.send_rpc_reply(request_id, distanceSEC, estadoSEC)
        elif request_body['method'] == 'getDistanceSecador':
            client.send_rpc_reply(request_id, distanceSEC, estadoSEC)
        elif request_body['method'] == 'getDistanceSecador':
            client.send_rpc_reply(request_id, distanceSEC, estadoSEC)
        elif request_body['method'] == 'getDistanceSecador':
            client.send_rpc_reply(request_id, distanceSEC, estadoSEC)
    '''
    

    # Connecting to ThingsBoard
    client = TBDeviceMqttClient(thingsboard_server, access_token)
    #client.set_server_side_rpc_request_handler(on_server_side_rpc_request)
    client.connect()

    '''
    # Callback on detect the motion from motion sensor
    def on_detect():
        log.info('motion detected')
        telemetry = {"motion": True}
        client.send_telemetry(telemetry)
        time.sleep(5)
        # Deactivating the motion in Dashboard
        client.send_telemetry({"motion": False})
        log.info("Motion alert deactivated")

    '''
    
    # Callback from button if it was pressed or unpressed
    def on_event():

        # Adding the callback to the motion sensor
        #pir_sensor.on_detect = on_detect
        # Adding the callback to the button
        #button.on_event = on_event
        try:
            while True:
                distance = ultrasonic_sensor.get_distance()
                
                log.debug('distance: {} cm'.format(distance))
                
                
                humidity, temperature = dht_sensor.read()
                log.debug('temperature: {}C, humidity: {}%'.format(temperature, humidity))

                #moisture = moisture_sensor.moisture
                #log.debug('moisture: {}'.format(moisture))
                light_state = light_sensor.light
                log.debug('light: {}'.format(light_state))
                
                #text = reader.read()
                #log.debug('puerta: {}'.format(text))

                # Formatting the data for sending to ThingsBoard
                telemetry = {'distance': distance,
                             'temperature': temperature,
                             'humidity': humidity,
                             'light': light_state}
                             #'puerta': text}

                # Sending the data
                client.send_telemetry(telemetry).get()

                time.sleep(.1)
        except Exception as e:
            raise e
        finally:
            client.disconnect()

    on_event()
if __name__ == '__main__':
    main()
