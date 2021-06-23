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
                speed = float(data[2])
                lat = float(data[3])
                lon = float(data[4])
                master_device = Device.objects.filter(is_master=True).first()
                last_speed = Information.objects.filter(device=master_device).last().speed
                if device_name != master_device.name:
                    if (speed - last_speed) > 20:
                        client.publish(topic=f'conviot/{device_name}/frena', payload=10, qos=1)
                    elif (last_speed - speed) > 20:
                        client.publish(topic=f'conviot/{device_name}/acelera', payload=10, qos=1)

            now = datetime.datetime.now()
            Information.objects.create(device=device, temp=temp, hum=hum, lat=lat, lon=lon, speed=speed, timestamp=now)


def update_led_mqtt(device, clientMQTT):
    pass