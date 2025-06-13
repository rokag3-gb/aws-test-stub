import boto3
import argparse
import json
from typing import Dict, List, Any

class AWSOrgReader:
    def __init__(self, role_arn: str, session_name: str, external_id: str, region: str = 'ap-northeast-2'):
        # STS 클라이언트 생성
        sts_client = boto3.client('sts')
        
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

def main():
    parser = argparse.ArgumentParser(description='AWS Organization 구조를 가져오는 스크립트')
    parser.add_argument('--role-arn', required=True, help='AWS Role ARN')
    parser.add_argument('--session-name', required=True, help='Session Name for STS')
    parser.add_argument('--external-id', required=True, help='External ID for STS')
    parser.add_argument('--region', default='ap-northeast-2', help='AWS Region (기본값: ap-northeast-2)')
    
    args = parser.parse_args()

    reader = AWSOrgReader(args.role_arn, args.session_name, args.external_id, args.region)
    org_structure = reader.get_org_structure()
    
    # 결과를 JSON 형식으로 출력
    print(json.dumps(org_structure, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main() 