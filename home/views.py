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
    process   = start_cicflowmeter(interface)

    create_config('interface',interface)
    create_config('cic_status',True)
    
    return Response({"message": "Monitoring has started started!"})

@api_view(['GET'])
def clear_db(request):
    FlowData.objects.all().delete()
    return Response({"message": "Database is cleared!"})


@api_view(['GET'])
def stop_interface(request):
    
    stop_cicflowmeter()
            
    create_config('interface',False)
    create_config('cic_status',False)
    
    return Response({"message": "cicflowmeter has been stopped!"})


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
    
    print("Data:", rsp)

    return Response(rsp)
    