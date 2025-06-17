import boto3
import configparser
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class AWSCostExplorer:
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

        # 임시 자격 증명으로 cost explorer 클라이언트 생성
        self.client = boto3.client(
            'ce',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=region
        )

    def get_cost_and_usage(
        self,
        start_date: str,
        end_date: str,
        granularity: str = 'MONTHLY',
        metrics: List[str] = ['UnblendedCost'],
        group_by: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        AWS Cost Explorer API를 통해 비용 데이터를 조회합니다.
        
        Args:
            start_date (str): 시작 날짜 (YYYY-MM-DD 형식)
            end_date (str): 종료 날짜 (YYYY-MM-DD 형식)
            granularity (str): 데이터 세분화 단위 (DAILY, MONTHLY, HOURLY)
            metrics (List[str]): 조회할 메트릭 목록
            group_by (List[Dict[str, str]]): 그룹화 기준 (예: [{'Type': 'DIMENSION', 'Key': 'SERVICE'}])
        
        Returns:
            Dict[str, Any]: 비용 데이터
        """
        try:
            params = {
                'TimePeriod': {
                    'Start': start_date,
                    'End': end_date
                },
                'Granularity': granularity,
                'Metrics': metrics
            }

            if group_by:
                params['GroupBy'] = group_by

            response = self.client.get_cost_and_usage(**params)
            return response

        except Exception as e:
            print(f"비용 데이터 조회 중 오류 발생: {str(e)}")
            raise

    def get_cost_forecast(
        self,
        start_date: str,
        end_date: str,
        metric: str = 'UNBLENDED_COST',
        granularity: str = 'MONTHLY'
    ) -> Dict[str, Any]:
        """
        AWS Cost Explorer API를 통해 비용 예측 데이터를 조회합니다.
        
        Args:
            start_date (str): 시작 날짜 (YYYY-MM-DD 형식)
            end_date (str): 종료 날짜 (YYYY-MM-DD 형식)
            metric (str): 예측할 메트릭
            granularity (str): 데이터 세분화 단위 (DAILY, MONTHLY, HOURLY)
        
        Returns:
            Dict[str, Any]: 비용 예측 데이터
        """
        try:
            response = self.client.get_cost_forecast(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Metric=metric,
                Granularity=granularity
            )
            return response

        except Exception as e:
            print(f"비용 예측 데이터 조회 중 오류 발생: {str(e)}")
            raise

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='AWS Cost Explorer 데이터를 조회하는 스크립트')
    parser.add_argument('--role-arn', required=True, help='AWS Role ARN')
    parser.add_argument('--session-name', required=True, help='Session Name for STS')
    parser.add_argument('--external-id', required=True, help='External ID for STS')
    parser.add_argument('--region', default='ap-northeast-2', help='AWS Region (기본값: ap-northeast-2)')
    parser.add_argument('--profile', default='cmp-sts-user', help='AWS Credentials 프로필 이름 (기본값: cmp-sts-user)')
    parser.add_argument('--start-date', required=True, help='시작 날짜 (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='종료 날짜 (YYYY-MM-DD)')
    parser.add_argument('--granularity', default='MONTHLY', choices=['DAILY', 'MONTHLY', 'HOURLY'], help='데이터 세분화 단위')
    parser.add_argument('--output', required=True, help='결과를 저장할 JSON 파일 경로')
    parser.add_argument('--forecast', action='store_true', help='비용 예측 데이터 조회 여부')
    
    args = parser.parse_args()

    try:
        explorer = AWSCostExplorer(
            role_arn=args.role_arn,
            session_name=args.session_name,
            external_id=args.external_id,
            region=args.region,
            profile_name=args.profile
        )

        if args.forecast:
            result = explorer.get_cost_forecast(
                start_date=args.start_date,
                end_date=args.end_date,
                granularity=args.granularity
            )
        else:
            result = explorer.get_cost_and_usage(
                start_date=args.start_date,
                end_date=args.end_date,
                granularity=args.granularity,
                group_by=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )

        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
        print(f"결과가 {args.output}에 저장되었습니다.")

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()