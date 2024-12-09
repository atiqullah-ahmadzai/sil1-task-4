# home/views.py
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import FlowData
from home.helpers import *
import subprocess
import sys
import os

    
def home(request):
    interfaces = get_interfaces()
    return render(request, 'main/index.html', {'interfaces': interfaces})

@api_view(['GET', 'POST'])
def post_flow(request):
    if request.method == 'POST':
        data = request.data
        prediction = predict_traffic(data)
        flow_data = FlowData.objects.create(name='Flow Data', data=data, prediction=prediction)
        return Response({"message": "Got some data!", "prediction": prediction})
    else:
        return Response({"message": "Got some data!"})
    

@api_view(['POST'])
def start_interface(request):
    interface = request.data.get('interface')
    cicflowmeter_path = os.path.join(os.path.dirname(sys.executable), 'cicflowmeter')
    command = [
        cicflowmeter_path,
        "-i", interface,
        "-u", "http://localhost:8000/post_flow"
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("cicflowmeter is now running in the background with PID:", process.pid)

    return Response({"message": "Monitoring has started started!"})

@api_view(['GET'])
def clear_db(request):
    FlowData.objects.all().delete()
    return Response({"message": "Database is cleared!"})


@api_view(['GET'])
def stop_interface(request):
    process = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode('utf-8', errors='replace')
    for line in out.splitlines():
        if 'cicflowmeter' in line:
            print(line)
            parts = line.split(None, 10)  
            if len(parts) > 1:
                pid = int(parts[1])
                os.kill(pid, 9)
                return Response({"message": "cicflowmeter has been stopped!"})
    
    return Response({"message": "cicflowmeter is not running!"})


@api_view(['GET'])
def get_data(request):
    
    # get limit from url
    if 'num_records' in request.GET:
        rows_limit = int(request.GET['num_records'])
        if rows_limit == 0:
            rows_limit = 50
        if rows_limit == 1:
            rows_limit = 5000
    else:
        rows_limit = 50
    
    data = FlowData.objects.all().values('id','data', 'prediction').order_by('-id')[:rows_limit]
    graph = settings = {}
    graph["graph_1"]    = get_records_per_minute()
    graph["graph_2"]    = get_label_count()
    settings["cic_status"] = check_cic_process()

    return Response({"data": list(data),"graphs":graph,"settings":settings})
    