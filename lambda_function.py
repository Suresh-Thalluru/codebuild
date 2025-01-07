import json
import os
import io
import boto3
import datetime
from PIL import Image
from io import BytesIO

s3 = boto3.client('s3',region_name='us-east-1')
dynamodb = boto3.resource('dynamodb',region_name='us-east-1')

PROCESSED_BUCKET = os.getenv('PROCESSED_BUCKET')
DDB_TABLE = os.getenv('DDB_TABLE')

def lambda_handler(event, context):
    # TODO implement
    print(json.dumps(event))
    src_buck = event['Records'][0]['s3']['bucket']['name']
    obj_key = event['Records'][0]['s3']['object']['key']
    print(obj_key)
    response = s3.get_object(Bucket=src_buck,Key=obj_key)
    
    image_data = response['Body'].read()

    image = Image.open(io.BytesIO(image_data))
    image = image.resize((800,800))
    buffer = io.BytesIO()
    image.save(buffer,format = 'JPEG')
    buffer.seek(0)
    print(buffer)

    #processed_img = process_image(image_data)

    new_key = obj_key

    # metadata = {

    #         'artist':obj_key.split("-")[0],
    #         'copyright':obj_key.split("-")[1],
    #         'description':obj_key.split("-")[2]}

    s3.put_object(Bucket=PROCESSED_BUCKET, Key=new_key,Body = buffer)#Metadata = metadata)
    s3_url = f"s3://{PROCESSED_BUCKET}/{obj_key}"
    table = dynamodb.Table(DDB_TABLE)
    table.put_item(Item = {
            'ImgID':obj_key,
            #'Artist':metadata['artist'],
            #'Copyright':metadata['copyright'],
            #'Description':metadata['description'],
            'S3URL':s3_url,
            'UploadTimestamp':datetime.datetime.now().isoformat()
            })
    return {
        'statusCode': 200,
        'body': json.dumps('Image processed successfully')
    }
"""def process_image(image_data):
    with Image.open(BytesIO(image_data)) as img:
        grayscale_image = img.convert('L')
        #img =img.resize((50,50))
        buffer = io.BytesIO()
        grayscale_image.save(buffer,format ='JPEG')
        buffer.seek(0)
        print(buffer.read())
        return buffer.read()"""

