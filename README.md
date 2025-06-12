# AWS Test Stub

AWS Organization를 비롯하여 AWS와 연동 테스트를 해보는 간단한 Python 스크립트입니다.

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 사용 방법

스크립트는 다음과 같이 실행할 수 있습니다:

```bash
python aws_org_reader.py --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY [--region REGION]
```

### 매개변수

- `--access-key`: AWS Access Key (필수)
- `--secret-key`: AWS Secret Key (필수)
- `--region`: AWS Region (선택, 기본값: ap-northeast-2)

### 출력

스크립트는 JSON 형식으로 다음 정보를 출력합니다:
- 루트 정보
- 각 OU의 정보
- 각 OU에 속한 계정 정보

## 주의사항

- 이 스크립트를 실행하기 위해서는 적절한 AWS 권한이 필요합니다.
- AWS Organizations API에 대한 접근 권한이 있어야 합니다.
- 크레덴셜 정보는 안전하게 관리해야 합니다. 