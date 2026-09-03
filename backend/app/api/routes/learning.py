from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.models.database import FeedbackRecord,TrainingLabelRecord,get_db
from app.models.schemas import LearningFeedbackInput,TrainingLabelInput
from app.services.learning import learning_status,train_all
from app.core.security import require_admin

router=APIRouter(prefix="/api/learning",tags=["continuous learning"])

@router.get("/status")
def status():return learning_status()

@router.post("/labels",status_code=201)
def add_label(payload:TrainingLabelInput,db:Session=Depends(get_db),_:None=Depends(require_admin)):
    record=TrainingLabelRecord(**payload.model_dump(),source="human_review");db.add(record);db.commit();db.refresh(record);return {"id":record.id,"accepted":True}

@router.post("/feedback",status_code=201)
def add_feedback(payload:LearningFeedbackInput,db:Session=Depends(get_db),_:None=Depends(require_admin)):
    record=FeedbackRecord(**payload.model_dump());db.add(record);db.commit();db.refresh(record);return {"id":record.id,"accepted":True}

@router.post("/train")
def train(_:None=Depends(require_admin)):return train_all()
