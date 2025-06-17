import argparse
import json
from aws_org_reader import AWSOrgReader, DateTimeEncoder

def main():
    parser = argparse.ArgumentParser(description='AWS Organization 구조를 가져오는 스크립트')
    parser.add_argument('--role-arn', required=True, help='AWS Role ARN')
    parser.add_argument('--session-name', required=True, help='Session Name for STS')
    parser.add_argument('--external-id', required=True, help='External ID for STS')
    parser.add_argument('--region', default='ap-northeast-2', help='AWS Region (기본값: ap-northeast-2)')
    parser.add_argument('--profile', default='cmp-sts-user', help='AWS Credentials 프로필 이름 (기본값: cmp-sts-user)')
    parser.add_argument('--output', help='결과를 저장할 JSON 파일 경로 (지정하지 않으면 stdout으로 출력)')
    
    args = parser.parse_args()

    try:
        reader = AWSOrgReader(
            role_arn=args.role_arn,
            session_name=args.session_name,
            external_id=args.external_id,
            region=args.region,
            profile_name=args.profile
        )
        
        org_structure = reader.get_org_structure()
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(org_structure, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
            print(f"결과가 {args.output}에 저장되었습니다.")
        else:
            print(json.dumps(org_structure, indent=2, ensure_ascii=False, cls=DateTimeEncoder))
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()