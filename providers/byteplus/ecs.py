from app.providers.base import ComputeProvider
from app.providers.byteplus.client import BytePlusClient

class BytePlusECSProvider(ComputeProvider):

def __init__(self, client: BytePlusClient):
    self.client = client

async def list_instances(self):
    # Call BytePlus ECS DescribeInstances
    return []

async def start_instance(self, instance_id: str):
    # Call BytePlus ECS StartInstance
    return {
        "instance_id": instance_id,
        "status": "starting",
    }

async def stop_instance(self, instance_id: str):
    return {
        "instance_id": instance_id,
        "status": "stopping",
    }

async def reboot_instance(self, instance_id: str):
    return {
        "instance_id": instance_id,
        "status": "rebooting",
    }
