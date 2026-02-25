import requests
import os, time

PRIMARY = int(os.getenv("PORT", "5001"))
SPARE = int(os.getenv("PORT", "5002"))
BALANCER =  int(os.getenv("PORT", "5000"))
ACTIVE = PRIMARY

TIMELAPSE = 2
THRESHOLD = 4

def flipServer():
    global ACTIVE
    if ACTIVE == PRIMARY:
        ACTIVE = SPARE
    else:
        ACTIVE = PRIMARY

#checks the health of the active server every TIMELAPSE seconds, if it fails THRESHOLD times, it tells the balancer to activate the spare server
if __name__ == "__main__":
    failureCount = 0
    while True:
        response = requests.get(f"http://localhost:{ACTIVE}/health", timeout=1)
        if response.status_code != 200:
            failureCount += 1
        else:
            failureCount = 0
        
        if failureCount >= THRESHOLD:
            response = requests.post(f"http://localhost:{BALANCER}/activateSpare")
            if response.status_code == 200:
                flipServer()
                print(f"Activated spare server, new active: {ACTIVE}")
                failureCount = 0
        print(f"Checked {ACTIVE} health, failure count: {failureCount}")
        
        time.sleep(TIMELAPSE)
        
