import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 配置
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_INFO = json.loads(os.environ['GDRIVE_CREDENTIALS'])
FOLDER_ID = os.environ['GDRIVE_FOLDER_ID']
FILE_TO_UPLOAD = 'codebase_context.md' # 这里要和 repo2txt.py 的输出一致

def authenticate():
    creds = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def upload_file():
    service = authenticate()
    
    # 1. 先检查文件是否已存在 (为了更新而不是重复创建)
    query = f"'{FOLDER_ID}' in parents and name = '{FILE_TO_UPLOAD}' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    media = MediaFileUpload(FILE_TO_UPLOAD, mimetype='text/markdown')

    if files:
        # 如果文件存在，执行 Update
        file_id = files[0]['id']
        service.files().update(
            fileId=file_id,
            media_body=media
        ).execute()
        print(f"Updated existing file: {FILE_TO_UPLOAD} (ID: {file_id})")
    else:
        # 如果文件不存在，执行 Create
        file_metadata = {
            'name': FILE_TO_UPLOAD,
            'parents': [FOLDER_ID]
        }
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"Uploaded new file: {FILE_TO_UPLOAD}")

if __name__ == '__main__':
    upload_file()
