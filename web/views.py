from django.shortcuts import render, redirect
import paho.mqtt.client as mqtt
from plotly.offline import plot
import plotly.graph_objs as go

from web.mqtt_functions import connection, on_message

from web.models import Device, Information


from random import sample

# Create your views here.

connected = False
clientMQTT = None


def index(request):
    context = {}
    context['page_active'] = 'index'

    device_master = Device.objects.filter(is_master=True).first()
    context['device_master'] = device_master
    context['device_slaves'] = Device.objects.filter(is_master=False)
    context['last_information'] = Information.objects.all().order_by('-timestamp')[:10]

    connect_mqtt()

    slave_master_1 = Device.objects.get(name='maria')
    master_temperature = Information.objects.filter(device=device_master).values('temp', 'hum', 'timestamp')
    slave_temperature = Information.objects.filter(device=slave_master_1).values('temp', 'timestamp')
    print('--------- slave_temperature', slave_temperature)
    print('--------- master_temperature', master_temperature)
    print('---------', master_temperature)

    # Gráfica Máster
    x_master_data = []
    y_temp_master_data = []
    y_hum_master_data = []

    for data in master_temperature:
        x_master_data.append(data['timestamp'])
        y_temp_master_data.append(data['temp'])
        y_hum_master_data.append(data['hum'])


    # Gráfica Slave 1
    x_slave_1_data = []
    y_temp_slave_1_data = []
    y_hum_slave_1_data = []
    for data in slave_temperature:
        x_slave_1_data.append(data['timestamp'])
        y_temp_slave_1_data.append(data['temp'])
        # y_hum_slave_1_data.append(data['hum'])

    # Gráfica de temperatura
    fig = go.Figure()
    scatter = go.Scatter(x=x_master_data, y=y_temp_master_data,
                         mode='lines', name='master',
                         opacity=0.8, marker_color='red')
    fig.add_trace(scatter)
    scatter2 = go.Scatter(x=x_slave_1_data, y=y_temp_slave_1_data,
                          mode='lines', name='slave1',
                          opacity=0.8, marker_color='blue')
    fig.add_trace(scatter2)
    fig.layout.template = 'plotly_dark'
    plot_div = plot(fig, output_type='div')

    context['plot_div'] = plot_div

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