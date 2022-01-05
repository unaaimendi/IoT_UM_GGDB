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
from grove.grove_mini_pir_motion_sensor import GroveMiniPIRMotionSensor
from datetime import datetime

# Configuration of logger, in this case it will send messages to console
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

log = logging.getLogger(__name__)

thingsboard_server = 'thingsboard.cloud'
access_token = 'SYCSlKb2Ku676Tt7OF6H'


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
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(24, GPIO.OUT)
    GPIO.setup(26, GPIO.IN)
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
        humi, temp = dht_sensor.read()
        #print('temperature {}C, humidity {}%'.format(temp, humi))
        if(temp < 24):
            increaseTemp()
        else:
            print("Temperatura correcta")
        time.sleep(1)
    
    def increaseTemp():
        try:
            GPIO.output(24, True)
            time.sleep(0.5)
            GPIO.output(24, False)
            time.sleep(0.2)
            GPIO.output(24, True)
            time.sleep(0.5)
            GPIO.output(24, False)
            print("Subiendo temperatura")
        except KeyboardInterrupt:
                    GPIO.cleanup()
        
    def LightState():
        light_state = light_sensor.light
        print('light value {}'.format(light_state))
        if(light_state < 300):
            increaseLight()
        else:
            print("Luz adecuada")
        time.sleep(1)
            
    def increaseLight():
        try:
            GPIO.output(24, True)
            time.sleep(0.5)
            GPIO.output(24, False)
            print('Subiendo luz')
        except KeyboardInterrupt:
                    GPIO.cleanup()
        
    def DistanceGrifo():
        tiempoDeUso = 0
        seguir = True
        instanteInicial = datetime.now()
        while seguir == True:
            estadoGRIF = False;
            distanceGRIF = ultrasonic_sensor.get_distance()
            print('{} cm'.format(distanceGRIF))
            if 15 > distanceGRIF + 1.5:
                print('Encendido GRIFO')
                estadoGRIF = True;
                if ((datetime.now() - instanteInicial).seconds > 20):
                    print("Apagando")

            else:
                print('Apagado')
                print(estadoGRIF)
                #if estadoGRIF: 
                #    estadoGRIF = False;
            
                instanteFinal = datetime.now()
                tiempo = instanteFinal - instanteInicial # Devuelve un objeto timedelta
                segundos = tiempo.seconds
                tiempoDeUso += segundos
                print("He llegado")
                seguir = False
                return calcularAgua(tiempoDeUso)
            
    

        '''
                    PUERTA
        '''

    def calcularAgua(tiempoDeUso):
        litros = tiempoDeUso * 0.2
        return litros

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
        
        print("Pase su tarjeta")
        setText("Lab 3\nPase su tarjeta")
        setRGB(0,102,204)
            
        idPuerta, nombreTarjeta = reader.read()
        if (nombreTarjeta.replace(" ","") == "Jon"):
            setText("Puerta abierta\nCierre al pasar")
            setRGB(0,255,0)
            print("Puerta abiera")
            time.sleep(5)
            setText("Lab 3\nPase su tarjeta")
            setRGB(0,102,204)
            return("Puerta abierta " + nombreTarjeta.replace(" ",""))
            
            
            
                    
        else:
            setText("\nPermiso denegado")
            print("Credenciales incorrectas")
            setRGB(255,0,0)
            time.sleep(5)
            setText("Lab 3\nPase su tarjeta")
            setRGB(0,102,204)
            return("Credenciales incorrectas " + nombreTarjeta.replace(" ",""))
            
        
        
            

        '''
            PUERTA FIN
        '''
        '''
            GRABAR PUERTA
        '''
                    
    def grabarNombre():
        input_state = GPIO.input(26)
        if input_state == True:
            nombreTarjeta = input('New data:')
            print("Now place your tag to write")
            reader.write(nombreTarjeta)
            print("Written")
        
            return(nombreTarjeta)
        else:
            return("")
        
        '''
            GRABAR PUERTA FIN
        '''
                        
    def getDistanceSecador():
        tiempoDeUso = 0
        seguir = True
        instanteInicial = datetime.now()
        while seguir == True:
            estadoSEC = False;
            distanceSEC = ultrasonic_sensor.get_distance()
            print('{} cm'.format(distanceSEC))
            if 15 > distanceSEC + 1.5:
                print('Encendido SECADOR')
                estadoSEC = True;
                if ((datetime.now() - instanteInicial).seconds > 20):
                    print("Apagando")

            else:
                print('Apagado')
                print(estadoSEC)
            
            
                instanteFinal = datetime.now()
                tiempo = instanteFinal - instanteInicial # Devuelve un objeto timedelta
                segundos = tiempo.seconds
                tiempoDeUso += segundos
                print("He llegado")
                seguir = False
                return calcularElectricidad(tiempoDeUso)
            
    def calcularElectricidad(tiempoDeUso):
        watios = tiempoDeUso * 0.11
        return watios
            
    def pirSens():
        # Sense motion, usually human, within the target range
        print(pir_sensor.on_detect)
        if (pir_sensor == 1):
            LightState()
            print ("Motion Detected")
        else:
            print ("-")
 
        # if your hold time is less than this, you might not see as many detections
        time.sleep(2)
            
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
                
                try:
                    text = grabarNombre()
                    tempHum()
                    litros = DistanceGrifo()
                    pirSens()
                    text2 = leerPuerta()
                    watios = getDistanceSecador()
                except KeyboardInterrupt:
                    GPIO.cleanup()
                
                distance = ultrasonic_sensor.get_distance()
                
                log.debug('distance: {} cm'.format(distance))
                
                
                humidity, temperature = dht_sensor.read()
                log.debug('temperature: {}C, humidity: {}%'.format(temperature, humidity))

                #moisture = moisture_sensor.moisture
                #log.debug('moisture: {}'.format(moisture))
                light_state = light_sensor.light
                log.debug('light: {}'.format(light_state))
                
                #text = reader.read()
                log.debug('grabada: {}'.format(text))
                
                log.debug('leida: {}'.format(text2))
                
                log.debug('litros: {}'.format(litros))
                
                log.debug('watios: {}'.format(watios))
                
                if distance < 15:
                    estado_grif = "Encendido"
                else:
                    estado_grif = "Apagado"
                
                log.debug('seca_grif: {}'.format(estado_grif))
            
                #presencia = pir_sensor.on_detect()
                #log.debug('presencia: {}'.format(presencia))
                # Formatting the data for sending to ThingsBoard
                telemetry = {'distance': distance,
                             'temperature': temperature,
                             'humidity': humidity,
                             'light': light_state,
                             #'presencia': presencia
                             'grabada': text,
                             'leida': text2,
                             'seca_grif': estado_grif,
                             'litros': litros,
                             'watios': watios}

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
