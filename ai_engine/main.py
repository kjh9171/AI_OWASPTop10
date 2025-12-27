from fastapi import FastAPI, UploadFile, File
from elasticsearch import Elasticsearch
import datetime

app = FastAPI()
es = Elasticsearch("http://elasticsearch:9200")

def simple_ai_logic(line):
    """임시 AI 탐지 로직 (나중에 학습된 모델로 교체 가능)"""
    line = line.lower()
    if "select" in line or "union" in line:
        return "A05:Injection (SQL)"
    elif "<script>" in line or "alert(" in line:
        return "A05:Injection (XSS)"
    elif "../" in line or "/etc/passwd" in line:
        return "A01:Broken Access Control"
    return "Normal"

@app.post("/upload-log")
async def analyze_log(file: UploadFile = File(...)):
    contents = await file.read()
    lines = contents.decode("utf-8").splitlines()
    
    for line in lines:
        if not line.strip(): continue
        
        attack_type = simple_ai_logic(line)
        doc = {
            "log_line": line,
            "owasp_category": attack_type,
            "timestamp": datetime.datetime.now().isoformat()
        }
        # Elasticsearch에 저장
        try:
            es.index(index="owasp-logs", document=doc)
        except Exception as e:
            print(f"ES Error: {e}")
            
    return {"message": "분석 완료", "processed_lines": len(lines)}