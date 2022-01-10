import logging
import time,sys
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
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
    
    # Incializacion de pines para sensores GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(24, GPIO.OUT)
    GPIO.setup(26, GPIO.IN)
    GPIO.setup(5, GPIO.IN)
    
    
    # Grove - Ultrasonic Ranger connected to port D16
    ultrasonic_sensor = GroveUltrasonicRanger(16)
    # Grove - RFID Sensor connected to serial
    reader = SimpleMFRC522()
    # Grove - Light Sensor connected to port A0
    light_sensor = GroveLightSensor(0)
    # Grove - Temperature&Humidity Sensor connected to port D22
    dht_sensor = DHT('11', 22)
    
    # Metodo que comprueba que la temperatura sea la correcta, en caso contrario se llamara a increaseTemp()
    def tempHum():
        humi, temp = dht_sensor.read()
        
        if(temp < 24):
            increaseTemp()
        else:
            print("Temperatura correcta")
        time.sleep(1)
    
    # En caso de no ser la temperatura correcta, el buzzer emitira 2 pitidos
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
    
    # Metodo que se encarga de comprobar que el nivel de luz sea el adecuado, en caso contrario se llamara a increaseLight() o decreaseLight() segun sea necesario
    def LightState():
        light_state = light_sensor.light
        print('light value {}'.format(light_state))
        if(light_state < 300):
            increaseLight()
        elif(light_state > 700):
            decreaseLight() 
        else:
            print("Luz adecuada")
        time.sleep(1)
            
    # En caso de tener un nivel de iluminación bajo el buzzer emitira un pitido
    def increaseLight():
        try:
            GPIO.output(24, True)
            time.sleep(0.5)
            GPIO.output(24, False)
            print('Subiendo luz')
        except KeyboardInterrupt:
                    GPIO.cleanup()
                    
    # En caso de tener un nivel de iluminación demasiado alto el buzzer emitira un pitido
    def decreaseLight():
        try:
            GPIO.output(24, True)
            time.sleep(0.5)
            GPIO.output(24, False)
            print('Bajando luz')
        except KeyboardInterrupt:
                    GPIO.cleanup()

    # Metodo que se encarga de comprobar si ha de activarse el grifo o no, comprobando la distancia, a su vez calcula el tiempo que el grifo esta encendido
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
        
    # Metodo que calcula el consumo de agua una vez el grifo ha sido apagado despues de uso
    def calcularAgua(tiempoDeUso):
        litros = tiempoDeUso * 0.2
        aguaData = [litros, tiempoDeUso]
        return aguaData
    
    # Metodo para poder cambiar el color de la LCD Backlight
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
    
    # Metodo que nos notifica que la ùerta ha sido abierta
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
        
    # Metodo que lee el sensor RFID para comprobar si ha de abrirse la puerta del Laboratorio o no
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
    # Metodo para grabar nombre en la tarjeta    
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
    
    # Metodo que comprueba si a de encenderse el secador o no y calcula el tiemo que ha estado encendido
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
                seguir = False
                return calcularElectricidad(tiempoDeUso)
            
    # Metodo que calcula el consumo electrico del secador en funcion del tiempo de uso del mismo
    def calcularElectricidad(tiempoDeUso):
        watios = tiempoDeUso * 0.11
        secadorData = [watios, tiempoDeUso]
        return secadorData
           
    # Metodo que detecta presencia y en caso de haberla comprueba el nivel de la luz 
    def pirSens():
        pir_sensor = GPIO.input(5)
        try:
        # Sense motion, usually human, within the target range
            if (pir_sensor == 1):
                LightState()
                return "Movimiento"
            else:
                return "-"
 
        # if your hold time is less than this, you might not see as many detections
 
        except KeyboardInterrupt:
            GPIO.cleanup()

            
    
    # Connecting to ThingsBoard
    client = TBDeviceMqttClient(thingsboard_server, access_token)
    #client.set_server_side_rpc_request_handler(on_server_side_rpc_request)
    client.connect()

    # Metodo principal que se encarga de llamar al resto de metodos, para recoger los datos y enviarlos al ThingsBoard
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
                    aguaData = DistanceGrifo()
                    presencia = pirSens()
                    text2 = leerPuerta()
                    secadorData = getDistanceSecador()
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
                
                log.debug('litros: {}'.format(aguaData[0]))
                
                log.debug('watios: {}'.format(secadorData[0]))
                
                log.debug('segundos_de_agua: {}'.format(aguaData[1]))
                
                log.debug('segundos_de_secado: {}'.format(secadorData[1]))
                
                log.debug('presencia: {}'.format(presencia))
                
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
                             'litros': aguaData[0],
                             'watios': secadorData[0],
                             'segundos_de_agua': aguaData[1],
                             'segundos_de_secado': secadorData[1],
                             'presencia': presencia}
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
