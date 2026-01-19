import os
import argparse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 这里不需要改动文件名，除非你想改
FILE_TO_UPLOAD = 'codebase_context.md'

def authenticate():
    # 使用 Refresh Token 构建凭据
    creds = Credentials(
        None, # access_token 设为 None，它会自动刷新
        refresh_token=os.environ['GDRIVE_REFRESH_TOKEN'],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ['GDRIVE_CLIENT_ID'],
        client_secret=os.environ['GDRIVE_CLIENT_SECRET']
    )
    return build('drive', 'v3', credentials=creds)

def upload_file(in_path):
    folder_id = os.environ['GDRIVE_FOLDER_ID']
    service = authenticate()
    
    # 检查文件是否存在
    query = f"'{folder_id}' in parents and name = '{FILE_TO_UPLOAD}' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    media = MediaFileUpload(in_path, mimetype='text/markdown')

    if files:
        file_id = files[0]['id']
        service.files().update(
            fileId=file_id,
            media_body=media
        ).execute()
        print(f"✅ Success: Updated existing file {FILE_TO_UPLOAD} (ID: {file_id})")
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
        print(f"✅ Success: Created new file {FILE_TO_UPLOAD}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert a code repository to a single text file for LLM context.")
    parser.add_argument("path", nargs="?", default=".", help="Path to the repository (default: current directory)")
    args = parser.parse_args()
    upload_file(args.path)
