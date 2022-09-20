from linebot import LineBotApi
from linebot.models import ImageSendMessage, VideoSendMessage
from linebot.exceptions import LineBotApiError
import os

def lambda_handler(event, context):  
    line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])

    for record in event["Records"]:
        bucket_name = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        file_type = key[-3:]
        if file_type not in ['jpg', 'mp4']:
            raise ValueError(f'Unexpected file type: {file_type}')
        
        url = f"https://{bucket_name}.s3.ap-northeast-1.amazonaws.com/{key}"
        if file_type == 'jpg':
            content = ImageSendMessage(original_content_url=url, preview_image_url=url)
        elif file_type == 'mp4':
            preview_image_url='https://security-camera-static-fa1e2d4d-3922-4286-b0c3-baa9b590789a.s3.ap-northeast-1.amazonaws.com/icon-camera.png'
            content = VideoSendMessage(original_content_url=url, preview_image_url=preview_image_url)

        try:
            print(content)
            users = os.environ['VERIFIED_USERS'].split(',')
            print(users)
            line_bot_api.multicast(users, content)
            return { 'statusCode': 200 }
        except LineBotApiError as e:
            print(e)
