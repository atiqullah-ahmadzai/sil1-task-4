# home/views.py
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import FlowData
from home.helpers import *

    
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
    return Response({"message": "Monitoring has started started!"})

@api_view(['GET'])
def clear_db(request):
    FlowData.objects.all().delete()
    return Response({"message": "Database is cleared!"})


@api_view(['GET'])
def get_data(request):
    # order by id desc
    data = FlowData.objects.all().values('id','data', 'prediction').order_by('-id')[:50]
    # get hourly data from created_at and count 
    graph = {}
    graph["graph_1"] = get_records_per_minute()
    graph["graph_2"] = get_label_count()

    return Response({"data": list(data),"graphs":graph})
    