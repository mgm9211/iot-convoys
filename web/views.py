from django.shortcuts import render, redirect
from datetime import date
import time
import paho.mqtt.client as mqtt
from plotly.offline import plot
import plotly.graph_objs as go
from web.mqtt_functions import connection, on_message
from web.models import Device, Information

from random import sample

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Create your views here.

connected = False
clientMQTT = None


def send_order(order, name):
    global clientMQTT
    connect_mqtt()
    if order == 1:
        # Accelerate
        clientMQTT.publish(topic=f'conviot/{name}/acelera', payload=10, qos=1)
    elif order == 2:
        # Brake
        clientMQTT.publish(topic=f'conviot/{name}/frena', payload=10, qos=1)
    elif order == 3:
        # Buzz
        clientMQTT.publish(topic=f'conviot/{name}/alarma', payload=order, qos=1)
    elif order == 4:
        # Start Master
        clientMQTT.publish(topic=f'conviot/{name}/start', payload=order, qos=1)
        clientMQTT.publish(topic=f'conviot/{name}/alarma', payload=order, qos=1)
        # Start Slave 1
        slaves_devices = Device.objects.filter(is_master=False)
        for slave in slaves_devices:
            time.sleep(4)
            clientMQTT.publish(topic=f'conviot/{slave.name}/start', payload=order, qos=1)
            clientMQTT.publish(topic=f'conviot/{slave.name}/alarma', payload=order, qos=1)



def index(request):
    context = {}
    context['page_active'] = 'index'

    device_master = Device.objects.filter(is_master=True).first()
    context['device_master'] = device_master
    context['device_slaves'] = Device.objects.filter(is_master=False)

    today = date.today()
    year = today.year
    month = today.month
    day = today.day
    context['last_information'] = Information.objects.all().order_by('-timestamp')[:10]

    connect_mqtt()
    master_temperature = Information.objects.filter(device=device_master, timestamp__year=year, timestamp__month=month,
                                                    timestamp__day=day).values('temp', 'hum', 'timestamp')

    # Gr??fica M??ster
    x_master_data = []
    y_temp_master_data = []
    y_hum_master_data = []

    for data in master_temperature:
        x_master_data.append(data['timestamp'])
        y_temp_master_data.append(data['temp'])
        y_hum_master_data.append(data['hum'])

    # Gr??fica Slave 1
    slaves_devices = Device.objects.filter(is_master=False)
    data_slaves_devices = []
    for slave in slaves_devices:
        dict_data_slave = {}
        x_slave_data = []
        y_temp_slave_data = []
        y_hum_slave_data = []
        slave_data = Information.objects.filter(device=slave, timestamp__year=year, timestamp__month=month,
                                                timestamp__day=day).values('temp', 'hum', 'timestamp')
        for data in slave_data:
            x_slave_data.append(data['timestamp'])
            y_temp_slave_data.append(data['temp'])
            y_hum_slave_data.append(data['hum'])
        dict_data_slave = {
            'name': slave.name,
            'x_slave_data': x_slave_data,
            'y_temp_slave_data': y_temp_slave_data,
            'y_hum_slave_data': y_hum_slave_data,
        }
        data_slaves_devices.append(dict_data_slave)

    # Gr??ficas de temperatura y humedad
    fig_temperature = go.Figure()
    fig_humidity = go.Figure()
    device_master_name = ''
    if device_master.name:
        device_master_name = device_master.name
    name_scatter = 'Lider-' + device_master_name
    scatter_temperature = go.Scatter(x=x_master_data, y=y_temp_master_data, mode='lines', name=name_scatter,
                                     opacity=0.8, marker_color='red')
    scatter_humidity = go.Scatter(x=x_master_data, y=y_hum_master_data, mode='lines', name=name_scatter,
                                  opacity=0.8, marker_color='red')
    fig_temperature.add_trace(scatter_temperature)
    fig_humidity.add_trace(scatter_humidity)

    # Gr??ficas slaves:
    cont = 1
    colors = ['blue', 'green', 'orange']

    for slave in data_slaves_devices:
        name_scatter = 'Slave-' + slave['name']
        fig_temperature.add_trace(go.Scatter(x=slave['x_slave_data'], y=slave['y_temp_slave_data'],
                                             mode='lines', name=name_scatter, opacity=0.8, marker_color=colors[cont]))
        fig_humidity.add_trace(go.Scatter(x=slave['x_slave_data'], y=slave['y_hum_slave_data'],
                                          mode='lines', name=name_scatter, opacity=0.8, marker_color=colors[cont]))
        cont += 1

    fig_temperature.layout.template = 'plotly_dark'
    fig_humidity.layout.template = 'plotly_dark'
    plot_div_temperature = plot(fig_temperature, output_type='div')
    plot_div_humidity = plot(fig_humidity, output_type='div')
    context['plot_div_temperature'] = plot_div_temperature
    context['plot_div_humidity'] = plot_div_humidity

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
        return redirect('devices')
    return render(request, "devices.html", context)


def map(request):
    context = {}

    context['page_active'] = 'map'

    today = date.today()

    year = today.year
    month = today.month
    day = today.day

    locations = []
    device_master = Device.objects.get(is_master=True)
    master_locations = Information.objects.filter(device=device_master, timestamp__year=year, timestamp__month=month,
                                                  timestamp__day=day).values('lat', 'lon')
    for location in master_locations:
        locations.append([location['lat'], location['lon']])
    context['locations'] = locations
    return render(request, "map.html", context)


def speed_up(request, device_id):
    name = Device.objects.filter(id=device_id).first().name
    send_order(1, name)
    send_order(3, name)
    return redirect('index')


def brake(request, device_id):
    name = Device.objects.filter(id=device_id).first().name
    send_order(2, name)
    send_order(3, name)
    return redirect('index')


def start(request, device_id):
    name = Device.objects.filter(id=device_id).first().name
    send_order(4, name)
    return redirect('index')


def delete_device(request, device_id):
    if Device.objects.filter(id=device_id).exists():
        Device.objects.get(id=device_id).delete()
    return redirect('devices')
