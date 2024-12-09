# home/views.py
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import FlowData, FirewallStatus, Settings
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
        if prediction == 'DDoS':
            if not FirewallStatus.objects.filter(ip=data['src_ip']).exists():
                FirewallStatus.objects.create(ip=data['src_ip'], status='Blocked')
                print("Blocked IP:", data['src_ip'])
                print("Call XDP Tool Command")
            
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

    create_config('interface',interface)
    create_config('cic_status',True)
    
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
            
    create_config('interface',False)
    create_config('cic_status',False)
    
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
    blocked = FirewallStatus.objects.all().values('id','ip', 'status').order_by('-id')[:rows_limit]
    
    graphs   = {}
    graphs["graph_1"]      = get_records_per_minute()
    graphs["graph_2"]      = get_label_count()
    
    settings = {}
    settings["cic_status"] = check_cic_process()
    settings["interface"]  = get_config('interface')
    
    rsp = {}
    rsp["data"]     = list(data)
    rsp["graphs"]   = graphs
    rsp["settings"] = settings
    rsp["blocked"]  = list(blocked)

    return Response(rsp)
    