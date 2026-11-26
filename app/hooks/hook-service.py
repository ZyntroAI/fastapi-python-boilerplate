from app.hooks.events import HookEvent from app.hooks.registry import registry

class HookService: @staticmethod async def emit(event: HookEvent, payload: dict) -> None: await registry.dispatch(event=event, payload=payload)  
