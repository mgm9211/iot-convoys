from django.shortcuts import render, redirect
import paho.mqtt.client as mqtt

from web.mqtt_functions import connection, on_message, update_led_mqtt

from web.models import Device

# Create your views here.

connected = False
clientMQTT = None


def index(request):
    context = {}
    context['page_active'] = 'index'

    connect_mqtt()

    context['username'] = request.session.get('username')
    return render(request, "dashboard.html", context)


def connect_mqtt():
    global connected, clientMQTT
    if not connected:
        # Defining MQTT Client, using paho library
        clientMQTT = mqtt.Client()
        # On Connection callbacks, function that execute when the connection to Client is completed
        clientMQTT.on_connect = connection
        # Setting username and password
        clientMQTT.username_pw_set(username="translucentchopper874", password="kvNTeMMYJzLHE7w9")
        # Connect to shiftr.io MQTT Client, using the url of the instace
        clientMQTT.connect("translucentchopper874.cloud.shiftr.io", 1883, 60)
        clientMQTT.loop_start()
        # On Message callbacks, function that execute when a message in subscribed topic is received
        clientMQTT.on_message = on_message
        # Set connected flag to True to avoid create a connection every time user refresh the web
        connected = True


def devices(request):
    context = {}

    context['page_active'] = 'devices'

    all_devices = Device.objects.all()
    context['all_devices'] = all_devices

    if request.POST:
        is_master = False
        if 'name' in request.POST and request.POST['name']:
            name = request.POST['name']
            if 'is_master' in request.POST and request.POST['is_master']:
                Device.objects.all().update(is_master=False)
                is_master = True
            if Device.objects.filter(name=name).exists():
                Device.objects.filter(name=name).update(is_master=is_master)
            else:
                Device.objects.create(name=name, is_master=is_master)
                global clientMQTT
                connect_mqtt()
                topic = 'conviot/' + name + '/*'
                clientMQTT.subscribe(topic)
        redirect('devices')
    return render(request, "devices.html", context)


def delete_device(request, device_id):
    if Device.objects.filter(id=device_id).exists():
        Device.objects.get(id=device_id).delete()
    return redirect('devices')