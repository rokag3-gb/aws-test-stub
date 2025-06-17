import boto3
import argparse
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

class AWSOrgReader:
    def __init__(self, role_arn: str, session_name: str, external_id: str, region: str = 'ap-northeast-2', profile_name: str = 'cmp-sts-user'):
        # AWS 자격 증명 파일에서 프로필 읽기
        config = configparser.ConfigParser()
        credentials_path = os.path.join(os.getcwd(), '.aws', 'credentials')
        
        # 디버깅을 위한 파일 경로 출력
        #print(f"자격 증명 파일 경로: {credentials_path}")
        #print(f"파일 존재 여부: {os.path.exists(credentials_path)}")
        
        if not os.path.exists(credentials_path):
            raise ValueError(f"자격 증명 파일을 찾을 수 없습니다: {credentials_path}")
            
        config.read(credentials_path)
        
        # 디버깅을 위한 프로필 목록 출력
        #print(f"사용 가능한 프로필: {config.sections()}")
        
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

        # 임시 자격 증명으로 organizations 클라이언트 생성
        self.client = boto3.client(
            'organizations',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=region
        )

    def get_roots(self) -> List[Dict[str, Any]]:
        """조직의 루트 정보를 가져옵니다."""
        try:
            response = self.client.list_roots()
            return response.get('Roots', [])
        except Exception as e:
            print(f"루트 정보 조회 중 오류 발생: {str(e)}")
            return []

    def get_ous_for_parent(self, parent_id: str) -> List[Dict[str, Any]]:
        """특정 부모 ID에 속한 OU 목록을 가져옵니다."""
        try:
            response = self.client.list_organizational_units_for_parent(ParentId=parent_id)
            return response.get('OrganizationalUnits', [])
        except Exception as e:
            print(f"OU 목록 조회 중 오류 발생: {str(e)}")
            return []

    def get_accounts_for_parent(self, parent_id: str) -> List[Dict[str, Any]]:
        """특정 부모 ID에 속한 계정 목록을 가져옵니다."""
        try:
            response = self.client.list_accounts_for_parent(ParentId=parent_id)
            return response.get('Accounts', [])
        except Exception as e:
            print(f"계정 목록 조회 중 오류 발생: {str(e)}")
            return []

    def get_org_structure(self) -> Dict[str, Any]:
        """전체 조직 구조를 재귀적으로 가져옵니다."""
        org_structure = {
            'roots': [],
            'ous': {},
            'accounts': {}
        }

        # 루트 정보 가져오기
        roots = self.get_roots()
        #print(f"roots={roots}")
        org_structure['roots'] = roots

        # 각 루트에 대해 OU와 계정 정보 수집
        for root in roots:
            root_id = root['Id']
            self._collect_ou_and_accounts(root_id, org_structure)

        return org_structure

    def _collect_ou_and_accounts(self, parent_id: str, org_structure: Dict[str, Any]) -> None:
        """재귀적으로 OU와 계정 정보를 수집합니다."""
        # OU 목록 가져오기
        ous = self.get_ous_for_parent(parent_id)
        org_structure['ous'][parent_id] = ous

        # 계정 목록 가져오기
        accounts = self.get_accounts_for_parent(parent_id)
        org_structure['accounts'][parent_id] = accounts

        # 각 OU에 대해 재귀적으로 정보 수집
        for ou in ous:
            self._collect_ou_and_accounts(ou['Id'], org_structure)