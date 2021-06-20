import json, re, datetime
from web.models import Device, Information


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
    # conviot / name / data
    if re.match(r'conviot/[A-Za-z]+/data', topic):
        data_topic = topic.split('/')
        device_name = data_topic[1]
        if Device.objects.filter(name=device_name).exists():
            device = Device.objects.get(name=device_name)
            if 'Data' in received_message:
                data = received_message['Data'].split(';')
                temp = float(data[0])
                hum = float(data[1])
                lat = float(data[2])
                lon = float(data[3])
            now = datetime.datetime.now()
            Information.objects.create(device=device, temp=temp, hum=hum, lat=lat, lon=lon, timestamp=now)


def update_led_mqtt(device, clientMQTT):
    pass