class CanvasCreate(BaseModel):
    title: str
    description: Optional[str]
    context: Dict = {}

class CanvasUpdate(BaseModel):
    title: Optional[str]
    status: Optional[str]
    context: Optional[Dict]
    artifacts: Optional[Dict]

class CanvasResponse(BaseModel):
    id: int
    title: str
    status: str
    context: Dict
    artifacts: Dict
    change_log: List[Dict]
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
