from fastapi import FastAPI, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import os
from models import SessionLocal, Article

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/articles")
def read_articles(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    articles = db.query(Article).offset(skip).limit(limit).all()
    return templates.TemplateResponse("index.html", {"request": request, "articles": articles})

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join("downloads", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
