from datetime import datetime
import os
import json

LOG_PATH = os.path.join("log","log.txt")
REPORT_PATH = os.path.join("report","report.txt")

def parseLogs():
    data = []  
    with open(LOG_PATH, "r") as f:
        logs = f.readlines()
    
    requests = []
    
    for log in logs:
        curEntry = json.loads(log)
        if curEntry["route"] == "kill":
            #start new downtime entry
            data.append({"server": curEntry["sent_to"], "down_since": datetime.strptime(curEntry["timestamp"], "%Y-%m-%d %H:%M:%S"), "service_back_up": None, "requests_around_downtime": 0, "failed_requests_during_downtime": 0})
        elif curEntry["route"] == "activateSpare":
            data[-1]["service_back_up"] = datetime.strptime(curEntry["timestamp"], "%Y-%m-%d %H:%M:%S")
        else:
           requests.append((datetime.strptime(curEntry["timestamp"], "%Y-%m-%d %H:%M:%S"), curEntry["code"], curEntry["sent_to"]))
    
    for curEntry in requests:
        req_ts = curEntry[0].timestamp()
        for downtime in data:
            start_ts = downtime["down_since"].timestamp() - 5
            end_ts = downtime["service_back_up"].timestamp() + 5  
            if downtime["server"] == curEntry[2] and start_ts <= req_ts and req_ts <= end_ts:
                downtime["requests_around_downtime"] += 1
                if curEntry[1] != 200:
                    downtime["failed_requests_during_downtime"] += 1
    
    
    numDowntimes = len(data)
    with open(REPORT_PATH, "w") as f:
        f.write(f"Nombre de Pannes: {numDowntimes}\n\n")
        for downtime in data:
            f.write(f"--- Panne {data.index(downtime) + 1} ---\n")
            f.write(f"Serveur: {downtime['server']}\n")
            f.write(f"Debut de la panne: {downtime['down_since']}\n")
            f.write(f"Service retabli: {downtime['service_back_up']}\n")
            f.write(f"Duree de la panne (Temps de bascule): {downtime['service_back_up'] - downtime['down_since']}\n")
            f.write(f"Nombre de requetes autour de la panne (Fenetre de 5s avant et apres): {downtime['requests_around_downtime']}\n")
            f.write(f"Requetes echouees pendant la panne: {downtime['failed_requests_during_downtime']}\n")
            error_rate = int((downtime['failed_requests_during_downtime'] / downtime['requests_around_downtime']) * 100)
            f.write(f"Taux d'erreurs pendant la bascule: {downtime['failed_requests_during_downtime']}/{downtime['requests_around_downtime']} = ~{error_rate}%\n")
            f.write("\n")
            
    
    
    
if __name__ == "__main__":
    parseLogs()