import boto3
import json
from typing import Dict, List, Any
import configparser
import os
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class AWSBudgetReader:
    def __init__(self, role_arn: str, session_name: str, external_id: str, region: str = 'ap-northeast-2', profile_name: str = 'cmp-sts-user'):
        # AWS 자격 증명 파일에서 프로필 읽기
        config = configparser.ConfigParser()
        credentials_path = os.path.join(os.getcwd(), '.aws', 'credentials')
        
        if not os.path.exists(credentials_path):
            raise ValueError(f"자격 증명 파일을 찾을 수 없습니다: {credentials_path}")
            
        config.read(credentials_path)
        
        if profile_name not in config:
            raise ValueError(f"프로필 '{profile_name}'을(를) .aws/credentials 파일에서 찾을 수 없습니다.")
            
        # STS 클라이언트 생성
        sts_client = boto3.client(
            'sts',
            aws_access_key_id=config[profile_name]['aws_access_key_id'],
            aws_secret_access_key=config[profile_name]['aws_secret_access_key'],
            region_name=region
        )
        
        # 역할 가정
        assumed_role = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name,
            ExternalId=external_id
        )

        credentials = assumed_role['Credentials']

        # 임시 자격 증명으로 budgets 클라이언트 생성
        self.client = boto3.client(
            'budgets',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=region
        )

    def describe_budgets(self, account_id: str) -> List[Dict[str, Any]]:
        """예산 목록을 조회합니다."""
        try:
            response = self.client.describe_budgets(AccountId=account_id)
            return response.get('Budgets', [])
        except Exception as e:
            print(f"예산 목록 조회 중 오류 발생: {str(e)}")
            return []

    def describe_budget(self, budget_name: str, account_id: str = None) -> Dict[str, Any]:
        """특정 예산의 상세 정보를 조회합니다."""
        try:
            if account_id:
                response = self.client.describe_budget(
                    AccountId=account_id,
                    BudgetName=budget_name
                )
            else:
                response = self.client.describe_budget(
                    BudgetName=budget_name
                )
            
            return response.get('Budget', {})
        except Exception as e:
            print(f"예산 상세 정보 조회 중 오류 발생: {str(e)}")
            return {}

    def get_budget_notifications(self, budget_name: str, account_id: str = None) -> List[Dict[str, Any]]:
        """특정 예산의 알림 설정을 조회합니다."""
        try:
            if account_id:
                response = self.client.describe_notifications_for_budget(
                    AccountId=account_id,
                    BudgetName=budget_name
                )
            else:
                response = self.client.describe_notifications_for_budget(
                    BudgetName=budget_name
                )
            
            return response.get('Notifications', [])
        except Exception as e:
            print(f"예산 알림 설정 조회 중 오류 발생: {str(e)}")
            return []

    def get_budget_actions(self, budget_name: str, account_id: str = None) -> List[Dict[str, Any]]:
        """특정 예산의 액션을 조회합니다."""
        try:
            if account_id:
                response = self.client.describe_budget_actions_for_budget(
                    AccountId=account_id,
                    BudgetName=budget_name
                )
            else:
                response = self.client.describe_budget_actions_for_budget(
                    BudgetName=budget_name
                )
            
            return response.get('Actions', [])
        except Exception as e:
            print(f"예산 액션 조회 중 오류 발생: {str(e)}")
            return []

    def get_complete_budget_info(self, budget_name: str, account_id: str = None) -> Dict[str, Any]:
        """특정 예산의 모든 정보를 종합적으로 조회합니다."""
        budget_info = {
            'budget': {},
            'notifications': [],
            'actions': []
        }

        # 예산 상세 정보
        budget_info['budget'] = self.describe_budget(budget_name, account_id)
        
        # 알림 설정
        budget_info['notifications'] = self.get_budget_notifications(budget_name, account_id)
        
        # 액션 정보
        budget_info['actions'] = self.get_budget_actions(budget_name, account_id)

        return budget_info 