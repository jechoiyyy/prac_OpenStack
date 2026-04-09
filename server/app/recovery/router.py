from fastapi import APIRouter
from pydantic import BaseModel
import uuid
from app.recovery.service import recover_vm

router = APIRouter()

class RecoveryRequest(BaseModel):
    vm_name: str
    backup_image_path: str
    flavor_id: str
    network_id: str
    required_vcpu: int
    required_ram_mb: int
    required_disk_gb: int


@router.post("/vm")
async def request_recovery(request: RecoveryRequest):
    # 1. task_id 생성 uuid.uuid4()
    task_id = uuid.uuid4()
    # 2. Redis Queue에 작업 적재
    
    # 3. 즉시 반환
    
    pass