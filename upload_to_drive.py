import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 读取环境变量中的文件名 (例如 vibe-coding-cn.pdf)
FILE_TO_UPLOAD = os.getenv('TARGET_FILENAME', 'output.pdf')

def authenticate():
    creds = Credentials(
        None,
        refresh_token=os.environ['GDRIVE_REFRESH_TOKEN'],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ['GDRIVE_CLIENT_ID'],
        client_secret=os.environ['GDRIVE_CLIENT_SECRET']
    )
    return build('drive', 'v3', credentials=creds)

def upload_file():
    folder_id = os.environ['GDRIVE_FOLDER_ID']
    service = authenticate()
    
    print(f"🚀 Uploading PDF: {FILE_TO_UPLOAD}")
    
    # 1. 检查是否存在同名文件 (覆盖更新)
    query = f"'{folder_id}' in parents and name = '{FILE_TO_UPLOAD}' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    media = MediaFileUpload(FILE_TO_UPLOAD, mimetype='application/pdf') # 👈 明确指定为 PDF

    if files:
        file_id = files[0]['id']
        service.files().update(
            fileId=file_id,
            media_body=media
        ).execute()
        print(f"✅ Updated existing PDF (ID: {file_id})")
    else:
        file_metadata = {
            'name': FILE_TO_UPLOAD,
            'parents': [folder_id]
        }
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"✅ Created new PDF")

if __name__ == '__main__':
    upload_file()
