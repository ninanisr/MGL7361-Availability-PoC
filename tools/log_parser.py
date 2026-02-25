from datetime import datetime
import os
import json

LOG_PATH = os.path.join("log","log.txt")
REPORT_PATH = os.path.join("report","report.txt")

def parseLogs():
    data = []  
    with open(LOG_PATH, "r") as f:
        logs = f.readlines()
    
    
    for log in logs:
        curEntry = json.loads(log)
        if curEntry["route"] == "kill":
            #start new downtime entry
            data.append({"server": curEntry["sent_to"], "down_since": datetime.strptime(curEntry["timestamp"], "%Y-%m-%d %H:%M:%S"), "service_back_up": None, "requests_during_downtime": 0, "failed_requests_during_downtime": 0})
        elif curEntry["route"] == "activateSpare":
            data[-1]["service_back_up"] = datetime.strptime(curEntry["timestamp"], "%Y-%m-%d %H:%M:%S")
        elif data and data[-1]["service_back_up"] == None and data[-1]["server"] == curEntry["sent_to"]:
            data[-1]["requests_during_downtime"] += 1
            if curEntry["code"] != 200:
                data[-1]["failed_requests_during_downtime"] += 1
    
    
    numDowntimes = len(data)
    with open(REPORT_PATH, "w") as f:
        f.write(f"Nombre de Pannes: {numDowntimes}\n\n")
        for downtime in data:
            f.write(f"--- Panne {data.index(downtime) + 1} ---\n")
            f.write(f"Serveur: {downtime['server']}\n")
            f.write(f"En panne depuis: {downtime['down_since']}\n")
            f.write(f"Service retabli: {downtime['service_back_up']}\n")
            f.write(f"Duree de la panne: {downtime['service_back_up'] - downtime['down_since']}\n")
            f.write(f"Requetes pendant la panne: {downtime['requests_during_downtime']}\n")
            f.write(f"Requetes echouees pendant la panne: {downtime['failed_requests_during_downtime']}\n")
            f.write("\n")
            
    
    
    
if __name__ == "__main__":
    parseLogs()