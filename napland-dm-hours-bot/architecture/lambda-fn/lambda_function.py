import json
import boto3
import os

s3 = boto3.client('s3')
bucket_name = os.getenv('S3_BUCKET_NAME')

def lambda_handler(event, context):
    dm_name = event['dm_name']
    date = event['date']
    hours = event['hours']
    session_name = event['session_name']
    
    data = {
        'dm_name': dm_name,
        'date': date,
        'hours': hours,
        'session_name': session_name
    }
    
    file_name = f"{dm_name}_{date}.json"
    
    s3.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=json.dumps(data)
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Session data stored successfully!')
    }