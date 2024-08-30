from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base, Report
from .utils import generate_report
import uuid
from datetime import datetime
from fastapi.responses import FileResponse

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/trigger_report")
async def trigger_report(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    report_id = str(uuid.uuid4())
    new_report = Report(id=report_id, status="Running", created_at=datetime.utcnow())
    db.add(new_report)
    db.commit()

    background_tasks.add_task(generate_report, report_id)
    return {"report_id": report_id}

@app.get("/get_report/{report_id}")
async def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.status == "Running":
        return {"status": "Running"}
    elif report.status == "Complete":
        return {
            "status": "Complete",
            "report_url": f"/download_report/{report_id}"
        }

@app.get("/download_report/{report_id}")
async def download_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report or report.status != "Complete":
        raise HTTPException(status_code=404, detail="Report not found or not ready")

    file_path = f"reports/{report_id}.csv"
    return FileResponse(file_path, media_type="text/csv", filename=f"report_{report_id}.csv")