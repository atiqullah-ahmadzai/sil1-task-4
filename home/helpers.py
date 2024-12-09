import subprocess
from datetime import datetime, timedelta, timezone
from home.models import FlowData
from django.db.models.functions import TruncMinute
from django.db.models import Count
import numpy as np
import joblib
import pyshark
import asyncio

def get_interfaces():
    import psutil

    addrs = psutil.net_if_addrs()
    
    return addrs

## Graphs ##
def get_records_per_minute():
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)
    data = (
        FlowData.objects.filter(created_at__gte=one_hour_ago, created_at__lte=now)
        .annotate(minute=TruncMinute('created_at'))
        .values('minute')
        .annotate(count=Count('id'))
        .order_by('minute')
    )
    graph_data = []
    graph_data = [{"time": d['minute'].strftime('%H:%M'), "count": d['count']} for d in data]
    minutes = [d['minute'].strftime('%H:%M') for d in data]
    for i in range(60):
        minute = (now - timedelta(minutes=i)).strftime('%H:%M')
        if minute not in minutes:
            graph_data.append({"time": minute, "count": 0})
    graph_data = sorted(graph_data, key=lambda x: x['time'])

    for i, d in enumerate(graph_data):
        d['time']
        d['time'] = i + 1
    return graph_data

def get_label_count():
    data = {}
    data["normal"] = FlowData.objects.filter(prediction='BENIGN').count()
    data["ddos"] = FlowData.objects.filter(prediction='DDoS').count()
    return data
    

## Prediction Model ##
def predict_traffic(json_data):
    feature_names = [
        'dst_port', 'totlen_fwd_pkts', 'fwd_pkt_len_max', 'fwd_pkt_len_mean', 'bwd_pkt_len_max',
        'bwd_pkt_len_min', 'bwd_pkt_len_mean', 'bwd_pkt_len_std', 'bwd_iat_tot',
        'pkt_len_min', 'pkt_len_max', 'pkt_len_mean', 'pkt_len_std', 'pkt_len_var',
        'urg_flag_cnt', 'pkt_size_avg', 'fwd_seg_size_avg', 'bwd_seg_size_avg',
        'subflow_fwd_byts', 'fwd_seg_size_min'
    ]
    data = [json_data[feature] for feature in feature_names]
    X = np.array(data).reshape(1, -1)
    model = joblib.load('models/decision_tree_model.pkl')

    prediction = model.predict(X)
    return prediction[0]

def check_cic_process():
    process = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if 'cicflowmeter' in str(out):
        return True
    return False