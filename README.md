# 프랜차이즈 크롤러

한국프랜차이즈협회 웹사이트의 API를 호출하여 프랜차이즈 정보를 수집하는 파이썬 크롤러입니다.

## 설치 및 실행

### 1. 가상환경 활성화
```bash
source venv/bin/activate
```

### 2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 크롤러 실행
```bash
python franchise_crawler.py
```

## 주요 기능

- **단일 페이지 데이터 수집**: `get_franchise_list()` 메서드로 특정 페이지의 프랜차이즈 목록을 가져옵니다.
- **다중 페이지 데이터 수집**: `get_all_franchises()` 메서드로 여러 페이지의 데이터를 한 번에 수집합니다.
- **JSON 파일 저장**: 수집된 데이터를 `franchise_data.json` 파일로 저장합니다.

## API 파라미터

- `kfaTpindLv1Cd`: 업종 대분류 코드 (기본값: "TP00000052")
- `kfaTpindLv2Cd`: 업종 소분류 코드
- `pageNum`: 페이지 번호
- `pagePerRows`: 페이지당 행 수
- `pageCount`: 페이지 수
- `sortGubun`: 정렬 구분
- `minCost`/`maxCost`: 비용 범위
- `minArea`/`maxArea`: 면적 범위

## 사용 예시

```python
from franchise_crawler import FranchiseCrawler

# 크롤러 인스턴스 생성
crawler = FranchiseCrawler()

# 단일 페이지 데이터 수집
result = crawler.get_franchise_list(page_num=1, page_per_rows=20)

# 여러 페이지 데이터 수집
all_data = crawler.get_all_franchises(max_pages=5)
```

## 주의사항

- 웹사이트의 이용약관을 준수하여 사용하세요.
- 과도한 요청은 서버에 부하를 줄 수 있으므로 적절한 간격을 두고 사용하세요.
- API 응답 구조가 변경될 수 있으므로 정기적으로 확인하세요. 