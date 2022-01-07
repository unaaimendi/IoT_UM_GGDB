# IoT_UM_GGDB
Trabajo final Desarrollo de aplicaciones para Internet de las Cosas

## Descripción 



Como ya explicamos en la presentación, nuestro proyecto consiste en la implementación de diversos sensores que eviten el contacto humano con cosas comunitarias como pueden ser puertas, grifos, secadores, luces… para de este modo intentar evitar contagios de COVID-19. Así mismo esta implementación también supondría un ahorro energético y de agua, prueba de ello, medimos la luz y el agua usada.

Para la implementación del mismo, hemos hecho uso de los siguientes sensores:

Mini Pir Motion Sensor
Temperature & Humidity Sensor
Buzzer
Light sensor
Ultrasonic Distance Sensor
Grove-LCD RGB Backlight
Touch Sensor
RFID Sensor


El código cuenta con un método main() que cuenta con 4 segmentos principales. 

- 1- Inicialización de los sensores

- 2- Métodos de control de sensores

- 3- Inicialización de la conexión con ThingsBoard

- 4- Método OnEvent

Este código ha utilizado de base un ejemplo de la documentación de ThingsBoard.

# 1- Inicialización de los sensores
En esta sección del código se inicializa cada sensor que se utilizará posteriormente para la recogida de datos y la implementación de las funcionalidades basándose en los datos.
# 2- Métodos de control de sensores
Esta sección consiste en varios métodos que se implementarán en el método OnEvent para gestionar las funcionalidades de nuestro producto.

tempHum()
- Este método se encarga de comprobar si la temperatura es adecuada para el trabajo. Si la temperatura es menor de 20 grados este método llamará a increaseTemp(). De lo contrario imprimirá “Temperatura correcta” por consola.

increaseTemp()
- Este método es el que enviaría un aviso para subir la temperatura controlando la calefacción. En este caso para representar esa acción este método utiliza un buzzer que pita dos veces al ejecutarse. Además se imprime “Subiendo temperatura” por consola.

LightState()
- Este método se encarga de comprobar si la luz del entorno de trabajo es adecuada. En el caso de que la luz sea inferior a 300 se llama al método increaseLight(). En el caso contrario se imprime por consola “Luz adecuada”.

increaseLight()
- Este método es el que enviaría un aviso al regulador de luz para subir la intensidad. En este caso lo hemos representado haciendo sonar el buzzer una sola vez. Además se imprime por consola “Subiendo luz”.

DistanceGrifo()
- Este método se encarga de comprobar si hay que encender el grifo o no. Utiliza el sensor de distancia y si la distancia es inferior a 15 cm se escribe por consola “Encendido GRIFO”. Si la distancia es mayor se imprime “Apagado”. Este metodo calcula el tiempo que ha estado el grifo activo y llama al método calcularAgua(tiempoDeUso) y devuelve el resultado.

calcularAgua(tiempoDeUso)
- Recibe como parámetro el tiempo de uso recogido por distanceGrifo() y en función del mismo nos devuelve la cantidad de litros de agua gastados y el tiempo que el grifo ha estado encendido.

decreaseLight()
- Igual que increase light, pero en este caso, se notificará de que se baja la intensidad de luz en caso de superar el rango de 700.

abrirPuerta()
- Imprime “Puerta Abierta” por consola

Metodos LCD Backlight (setRGB, textCommand, setText, setTextnorefresh, createChar)
- Son métodos utilizados para interactuar con la pantalla.

leerPuerta()
- Este método utiliza el sensor RFID para detectar si el usuario utilizándolo coincide con el nombre e identificación grabadas en la tarjeta. De ser así devuelve el mensaje “Puerta abierta + Nombre”. Además pasa este texto al sensor LCD RGB backlight para mostrarlo en el. Si no es correcto hace el mismo procedimiento pero con el mensaje “Credenciales incorrectas + Nombre”.

grabarNombre()
- Este método define un nuevo usuario asignado a la tarjeta y devuelve el nombre del usuario.

getDistanceSecador()
- Método que se encarga de comprobar si hay que encender el secador o no (en caso de que la distancia sea menor a 15 cm). Nos notificará  “Encendido SECADOR” o “Apagado”. A su vez llama al método calcularElectricidad() y devolverá los datos calculados por el mismo.

calcularElectricidad()
- Recibe como parámetro el tiempo de uso recogido por getDistanceSecador() y en función del mismo nos devuelve la cantidad de vatios gastados y el tiempo que el secador ha estado encendido.

pirSens()
- Método que detecta presencia y en caso de haberla dispara el método de lightState()



# 3- Inicialización de la conexión con ThingsBoard

Utiliza la siguiente linea de codigo para crear la conexión a ThingsBoard:


client = TBDeviceMqttClient(thingsboard_server, access_token)


Despues utiliza client.connect() y establece la conexión.

- thingsboard_server = 'thingsboard.cloud'
- access_token = 'SYCSlKb2Ku676Tt7OF6H'

Mediante estos dos parámetros, realizamos la conexión con el thingsboard.

# 4- Método OnEvent

Método principal que activa los sensores y hace lo explicado a continuación: 

A la hora de ejecutar el código, la raspberry empezará a recoger los datos de los sensores y enviarlos al dashboard. En primer lugar, si pulsamos el Touch Sensor, escribimos un nombre y a continuación acercamos la tarjeta al RFID Sensor grabara ese nombre en la tarjeta. Seguido, se mirará si la temperatura es menor de 24 grados, en caso de no serlo, el buzzer pitará (dos veces) y se notificará que la calefacción se encenderá.  A continuación vendría la demostración del grifo, en caso de acercar la mano al Ultra Sonic Distance Sensor nos notificara que el grifo está encendido (en caso contrario nos notificara que el grifo está apagado) y en caso de estar encendido se calculará el consumo de agua en litros. Seguido, en caso de que el Mini Pir Motion Sensor detecte presencia, el Light Sensor recogerá la luz de la sala y en caso de ser menor a 300 el buzzer pitara (una única vez) y se notificará que se está subiendo la luz y en caso de ser mayor a 700 tambien pitará una vez y se nos notificara que se está bajando la luz. A continuación se nos pedirá que pasemos la tarjeta y podremos ver el texto “Lab 3 Pase su tarjeta” en el Grove-LCD RGB Backlight al pasarla por el RFID Sensor si el nombre previamente introducido es “Jon”  el Grove-LCD RGB Backlight se pondrá verde y pondrá “Puerta abierta Jon” en caso de no ser “Jon” el nombre introducido se pondrá roja y pondrá “Credenciales incorrectas”. En cuanto al sensor de presencia se envia cunado ha detectado movimiento mediante "Movimiento" y de lo contrario con un "-". Finalmente tendremos el secador, que es lo mismo que el grifo pero midiendo el consumo eléctrico.
