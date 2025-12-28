import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 1. 학습용 기초 데이터 (실제 환경에서는 더 많은 로그 데이터가 필요합니다)
data = {
    'payload': [
        "SELECT * FROM users WHERE id='1' OR '1'='1'",      # A05: Injection
        "admin' --",                                        # A05: Injection
        "<script>alert('XSS')</script>",                    # A05: Injection (XSS)
        "javascript:alert(1)",                              # A05: Injection
        "../../etc/passwd",                                 # A01: Broken Access Control
        "../wp-config.php",                                 # A01: Broken Access Control
        "GET /index.html HTTP/1.1",                         # Normal
        "GET /images/logo.png HTTP/1.1",                    # Normal
        "User-Agent: Mozilla/5.0",                          # Normal
        "POST /login.php HTTP/1.1",                         # Normal
        "cat /etc/shadow",                                  # A05: Injection (OS Command)
        "curl http://malicious-site.com"                   # A01: SSRF/Injection
    ],
    'label': [
        "A05:Injection", "A05:Injection", "A05:Injection", "A05:Injection",
        "A01:Broken Access Control", "A01:Broken Access Control",
        "Normal", "Normal", "Normal", "Normal",
        "A05:Injection", "A01:Broken Access Control"
    ]
}

# 2. 데이터프레임 생성 및 전처리
df = pd.DataFrame(data)

# 텍스트 데이터를 수치화 (TF-IDF 벡터화)
vectorizer = TfidfVectorizer(ngram_range=(1, 2), analyzer='char')
X = vectorizer.fit_transform(df['payload'])
y = df['label']

# 3. 모델 학습 (Random Forest)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 4. 모델 및 벡터라이저 저장 (Docker 내부에서 읽을 파일)
joblib.dump(model, 'owasp_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

print("AI 모델 및 벡터라이저 생성 완료!")
print(f"학습된 카테고리: {model.classes_}")