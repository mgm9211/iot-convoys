import json

def connection(client, userdata, flags, rc):
    """
    Method to subcribe to given topic
    :param client: MQTT client created with paho
    :param userdata:
    :param flags:
    :param rc:
    :return:
    """
    # Suscripcion a todos los topic de SPEA
    client.subscribe('conviot/*/*')


def on_message(client, userdata, msg):
    """
    Logic to apply when message is received
    :param client:
    :param userdata:
    :param msg:
    :return:
    """
    received_message = json.loads(msg.payload)
    topic = msg.topic
    # {'Data': '27.07;44.00;36.715820;-4.624558', 'Timestamp': 10002, 'ID': 'SoyElMaster'}
    if 'Data' in received_message:
        data = received_message['Data'].split(';')
        temp = float(data[0])
        hum = float(data[1])
        lat = float(data[2])
        lon = float(data[3])
        print('------Temperatura ', temp, '- hum', hum, '- lat ', lat, '- lon', lon)
    print('------received_message ', received_message)





def update_led_mqtt(device, clientMQTT):
    pass