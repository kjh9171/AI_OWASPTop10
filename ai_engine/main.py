from fastapi import FastAPI, UploadFile, File
from elasticsearch import Elasticsearch
import joblib
import datetime
import os

app = FastAPI()
es = Elasticsearch(os.getenv("ES_HOST", "http://elasticsearch:9200"))

# 모델 로드
MODEL_PATH = "./model/owasp_model.pkl"
VECT_PATH = "./model/vectorizer.pkl"

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECT_PATH)
else:
    model = None

@app.post("/upload-log")
async def analyze_log(file: UploadFile = File(...)):
    contents = await file.read()
    lines = contents.decode("utf-8").splitlines()
    
    for line in lines:
        if not line.strip(): continue
        
        # AI 모델 추론
        if model:
            features = vectorizer.transform([line])
            prediction = model.predict(features)[0]
            confidence = max(model.predict_proba(features)[0])
        else:
            prediction = "Model Not Found"
            confidence = 0.0

        doc = {
            "log_line": line,
            "owasp_category": prediction,
            "confidence": float(confidence),
            "timestamp": datetime.datetime.now().isoformat()
        }
        es.index(index="owasp-logs", document=doc)
            
    return {"message": "AI 분석 및 저장 완료", "processed_lines": len(lines)}