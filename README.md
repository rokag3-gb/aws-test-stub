# AWS Test Stub

AWS Organization와 AWS Budgets를 비롯하여 AWS와 STS(Security Token Service) 방식으로 접속하여 API 연동 테스트를 해보는 간단한 Python 스크립트입니다.

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 사용 방법

### 1. AWS Organization 구조 조회

스크립트는 다음과 같이 실행할 수 있습니다:

```bash
python main.py --role-arn ROLE_ARN --session-name SESSION_NAME --external-id EXTERNAL_ID [--region REGION] [--profile PROFILE] [--output OUTPUT_FILE]
```

#### 매개변수

- `--role-arn`: AWS Role ARN (필수)
- `--session-name`: STS 세션 이름 (필수)
- `--external-id`: External ID for STS (필수)
- `--region`: AWS Region (선택, 기본값: ap-northeast-2)
- `--profile`: AWS Credentials 프로필 이름 (선택, 기본값: cmp-sts-user)
- `--output`: 결과를 저장할 JSON 파일 경로 (선택)

#### 출력

스크립트는 JSON 형식으로 다음 정보를 출력합니다:
- 루트 정보
- 각 OU의 정보
- 각 OU에 속한 계정 정보

### 2. AWS Budgets 예산 조회

AWS Budgets API를 사용하여 예산 정보를 조회할 수 있습니다:

```bash
python test_budget.py --role-arn ROLE_ARN --session-name SESSION_NAME --external-id EXTERNAL_ID --account-id ACCOUNT_ID [--region REGION] [--profile PROFILE] [--budget-name BUDGET_NAME] [--output OUTPUT_FILE]
```

#### 매개변수

- `--role-arn`: AWS Role ARN (필수)
- `--session-name`: STS 세션 이름 (필수)
- `--external-id`: External ID for STS (필수)
- `--account-id`: AWS 계정 ID (필수)
- `--region`: AWS Region (선택, 기본값: ap-northeast-2)
- `--profile`: AWS Credentials 프로필 이름 (선택, 기본값: cmp-sts-user)
- `--budget-name`: 특정 예산 이름 (선택)
- `--output`: 결과를 저장할 JSON 파일 경로 (선택)

#### 기능

- `describe_budgets()`: 모든 예산 목록 조회
- `describe_budget()`: 특정 예산의 상세 정보 조회
- `get_budget_notifications()`: 예산 알림 설정 조회
- `get_budget_actions()`: 예산 액션 조회
- `get_complete_budget_info()`: 예산의 모든 정보를 종합적으로 조회

#### 출력 예시

```json
{
  "budgets": [
    {
      "BudgetName": "Monthly Budget",
      "BudgetType": "COST",
      "TimeUnit": "MONTHLY"
    }
  ],
  "budget_detail": {
    "BudgetName": "Monthly Budget",
    "BudgetType": "COST",
    "TimeUnit": "MONTHLY",
    "BudgetLimit": {
      "Amount": "1000",
      "Unit": "USD"
    }
  },
  "notifications": [...],
  "actions": [...]
}
```

## 주의사항

- 이 스크립트를 실행하기 위해서는 적절한 AWS 권한이 필요합니다.
- AWS Organizations API와 AWS Budgets API에 대한 접근 권한이 있어야 합니다.
- STS 역할에는 Organizations API와 Budgets API에 대한 적절한 권한이 부여되어 있어야 합니다.
- 크레덴셜 정보는 안전하게 관리해야 합니다. 