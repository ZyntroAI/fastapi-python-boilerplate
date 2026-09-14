from abc import ABC, abstractmethod

class ComputeProvider(ABC):
    @abstractmethod
    async def list_instances(self): raise NotImplementedError
    @abstractmethod
    async def start_instance(self, instance_id: str): raise NotImplementedError
    @abstractmethod
    async def stop_instance(self, instance_id: str): raise NotImplementedError
    @abstractmethod
    async def reboot_instance(self, instance_id: str): raise NotImplementedError
