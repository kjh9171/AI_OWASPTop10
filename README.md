# AI_OWASPTop10
AI_OWASPTop10 분석플랫폼
**Docker 기반의 분석 플랫폼 아키텍처** 
---

### 1. AI 모델의 공격 탐지 메커니즘

로그 데이터를 업로드하면 AI 모델(주로 NLP 기반 분류 모델)이 다음과 같은 단계를 거쳐 공격을 식별합니다.

1. **전처리 (Parsing):** 로그에서 `Client IP`, `Request Method`, `URL`, `Payload`, `Status Code` 등을 분리합니다.
2. **특징 추출 (Feature Extraction):** URL이나 Payload 내의 특수문자 비율, 특정 키워드(SELECT, `<script>`, `../` 등)의 등장 빈도를 수치화합니다.
3. **모델 분석 (Classification):** * **인젝션(A05):** SQL 구문이나 스크립트 태그 패턴 분석.
* **인증 실패(A07):** 짧은 시간 내의 반복된 401/403 에러 패턴(Brute-force) 분석.
* **접근 제어 실패(A01):** 관리자 페이지(`/admin`)에 대한 비정상적 접근 시도 분석.

---

### 2. Docker 기반 AI 분석 플랫폼 구축 가이드

이 플랫폼은 **로그 수집(Logstash) - 저장 및 검색(Elasticsearch) - AI 추론(Python Flask/FastAPI) - 시각화(Kibana)** 구조로 구성됩니다.

#### [docker-compose.yml 예시 구조]

아래는 분석을 위한 핵심 서비스 구성안입니다.

```yaml
version: '3.8'
services:
  # 1. 데이터 저장소
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  # 2. AI 분석 엔진 (사용자가 구현한 모델 서빙)
  ai-analyzer:
    build: ./ai_model_service
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/app/logs # 로그 업로드 폴더 공유

  # 3. 데이터 시각화 및 관리
  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

```

#### [AI 모델 서비스 (ai_model_service/app.py) 개념]

Python의 `Scikit-learn`이나 `PyTorch` 모델을 사용하여 업로드된 로그를 분류하는 핵심 로직입니다.

```python
from flask import Flask, request
import joblib # 학습된 AI 모델 로드

app = Flask(__name__)
model = joblib.load('owasp_classifier.pkl') # OWASP Top 10 분류 모델

@app.route('/analyze', methods=['POST'])
def analyze_log():
    log_file = request.files['file']
    # 1. 로그 읽기 및 전처리
    # 2. model.predict(data) 실행
    # 3. A01~A10 중 가장 확률이 높은 항목 반환
    return {"attack_type": "A05: Injection", "confidence": 0.98}

```

---

### 3. 분석 플랫폼 활용 시나리오

1. **로그 업로드:** 사용자가 웹 UI 또는 API를 통해 `.log` 또는 `.csv` 파일을 업로드합니다.
2. **AI 탐지 수행:** `ai-analyzer` 컨테이너가 텍스트를 분석하여 각 로그 라인별로 **OWASP 카테고리 태그**를 붙입니다.
3. **결과 확인:** Kibana 대시보드에서 "현재 우리 서버에 가장 많이 발생하는 공격은 **A05(인젝션)**이며, 주 타겟은 `/login` 페이지이다"라는 통계를 시각적으로 확인합니다.

---
