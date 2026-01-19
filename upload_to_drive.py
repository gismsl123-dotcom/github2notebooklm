import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 从环境变量读取文件名，默认为 codebase_context.txt
FILE_TO_UPLOAD = os.getenv('TARGET_FILENAME', 'codebase_context.txt')

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
    
    # 1. 确定最终在 Drive 显示的文件名 (去掉 .txt/.md 后缀，让它看起来像个真正的文档)
    file_name_no_ext = os.path.splitext(FILE_TO_UPLOAD)[0]
    
    print(f"🔄 Processing: {FILE_TO_UPLOAD} -> Google Doc: {file_name_no_ext}")
    
    # 2. 搜索同名文件 (注意：这里搜索的是 Google Doc 类型的文件)
    query = f"'{folder_id}' in parents and name = '{file_name_no_ext}' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    # 3. 如果存在，直接删除旧的 (为了保证转换万无一失，覆盖更新 Google Doc 比较麻烦)
    if files:
        for f in files:
            print(f"🗑️ Deleting old version: {f['id']}")
            service.files().delete(fileId=f['id']).execute()

    # 4. 创建新的 Google Doc
    file_metadata = {
        'name': file_name_no_ext,     # Drive 里显示的文档名
        'parents': [folder_id],
        'mimeType': 'application/vnd.google-apps.document' # 👈【关键】告诉 Drive 把它转成 Google 文档
    }

    # 上传本地文本内容
    media = MediaFileUpload(FILE_TO_UPLOAD, mimetype='text/plain', resumable=True)

    created_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    print(f"✅ Success! Created Google Doc: {file_name_no_ext} (ID: {created_file.get('id')})")

if __name__ == '__main__':
    upload_file()
