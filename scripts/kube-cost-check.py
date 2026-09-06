# scripts/kube-cost-check.py
import requests, os
ORBIT_TRACE_ID = os.getenv("ORBIT_TRACE_ID")

def check_budget(namespace: str, limit: float=50):
    res = requests.get("http://kubecost:9090/model/allocation",
        params={"namespace":namespace, "window":"1d"})
    cost = res.json()["data"][0]["cumulativeNetCost"]
    if cost > limit:
        print(f"🚨 BUDGET EXCEEDED: ${cost:.2f} [trace:{ORBIT_TRACE_ID}]")
        return False
    return True
