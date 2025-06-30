import argparse
import json
from aws_budget import AWSBudgetReader, DateTimeEncoder

def main():
    parser = argparse.ArgumentParser(description='AWS Budgets API 테스트 스크립트')
    parser.add_argument('--role-arn', required=True, help='AWS Role ARN')
    parser.add_argument('--session-name', required=True, help='Session Name for STS')
    parser.add_argument('--external-id', required=True, help='External ID for STS')
    parser.add_argument('--region', default='ap-northeast-2', help='AWS Region (기본값: ap-northeast-2)')
    parser.add_argument('--profile', default='cmp-sts-user', help='AWS Credentials 프로필 이름 (기본값: cmp-sts-user)')
    parser.add_argument('--account-id', required=True, help='AWS 계정 ID (필수)')
    parser.add_argument('--budget-name', help='특정 예산 이름 (선택사항)')
    parser.add_argument('--output', help='결과를 저장할 JSON 파일 경로 (지정하지 않으면 stdout으로 출력)')
    
    args = parser.parse_args()

    try:
        reader = AWSBudgetReader(
            role_arn=args.role_arn,
            session_name=args.session_name,
            external_id=args.external_id,
            region=args.region,
            profile_name=args.profile
        )
        
        result = {}
        
        # 1. 예산 목록 조회
        print("=== 예산 목록 조회 중... ===")
        budgets = reader.describe_budgets(args.account_id)
        result['budgets'] = budgets
        print(f"총 {len(budgets)}개의 예산을 찾았습니다.")
        
        for budget in budgets:
            print(f"- {budget.get('BudgetName', 'N/A')} ({budget.get('BudgetType', 'N/A')})")
        
        # 2. 특정 예산 상세 정보 조회 (예산 이름이 제공된 경우)
        if args.budget_name:
            print(f"\n=== 예산 '{args.budget_name}' 상세 정보 조회 중... ===")
            budget_detail = reader.describe_budget(args.budget_name, args.account_id)
            result['budget_detail'] = budget_detail
            
            if budget_detail:
                print(f"예산 이름: {budget_detail.get('BudgetName', 'N/A')}")
                print(f"예산 타입: {budget_detail.get('BudgetType', 'N/A')}")
                print(f"시간 단위: {budget_detail.get('TimeUnit', 'N/A')}")
                
                # 예산 알림 설정 조회
                print(f"\n=== 예산 '{args.budget_name}' 알림 설정 조회 중... ===")
                notifications = reader.get_budget_notifications(args.budget_name, args.account_id)
                result['notifications'] = notifications
                print(f"총 {len(notifications)}개의 알림 설정을 찾았습니다.")
                
                # 예산 액션 조회
                print(f"\n=== 예산 '{args.budget_name}' 액션 조회 중... ===")
                actions = reader.get_budget_actions(args.budget_name, args.account_id)
                result['actions'] = actions
                print(f"총 {len(actions)}개의 액션을 찾았습니다.")
            else:
                print(f"예산 '{args.budget_name}'을 찾을 수 없습니다.")
        
        # 3. 첫 번째 예산의 상세 정보 조회 (예산 이름이 제공되지 않은 경우)
        elif budgets:
            first_budget = budgets[0]
            budget_name = first_budget.get('BudgetName')
            print(f"\n=== 첫 번째 예산 '{budget_name}' 상세 정보 조회 중... ===")
            
            complete_info = reader.get_complete_budget_info(budget_name, args.account_id)
            result['complete_budget_info'] = complete_info
            
            budget_detail = complete_info['budget']
            if budget_detail:
                print(f"예산 이름: {budget_detail.get('BudgetName', 'N/A')}")
                print(f"예산 타입: {budget_detail.get('BudgetType', 'N/A')}")
                print(f"시간 단위: {budget_detail.get('TimeUnit', 'N/A')}")
                print(f"알림 설정 수: {len(complete_info['notifications'])}")
                print(f"액션 수: {len(complete_info['actions'])}")
        
        # 결과 출력
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
            print(f"\n결과가 {args.output}에 저장되었습니다.")
        else:
            print(f"\n=== 전체 결과 ===")
            print(json.dumps(result, indent=2, ensure_ascii=False, cls=DateTimeEncoder))
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main() 