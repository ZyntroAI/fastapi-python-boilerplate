from fastapi import APIRouter

from app.agents.executor import AgentExecutor
from app.agents.planner import AgentPlanner
from app.providers.byteplus.client import BytePlusClient
from app.providers.byteplus.ecs import BytePlusECSProvider
from app.services.compute_service import ComputeService

router = APIRouter(prefix="/compute", tags=["compute"])

def get_service() -> ComputeService:
client = BytePlusClient()
provider = BytePlusECSProvider(client)

executor = AgentExecutor(provider)
planner = AgentPlanner()

return ComputeService(
    planner=planner,
    executor=executor,
)
@router.post("/instances/{instance_id}/start")
async def start_instance(instance_id: str):

service = get_service()

return await service.execute(
    action="start_instance",
    instance_id=instance_id,
)
