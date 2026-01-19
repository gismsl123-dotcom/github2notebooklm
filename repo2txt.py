import os
import argparse
from pathlib import Path

# ================= 配置区域 =================
# 想要包含的文件后缀
INCLUDE_EXTENSIONS = {
    '.py', '.js', '.ts', '.html', '.css', '.md', '.txt', 
    '.json', '.yml', '.yaml', '.toml', '.sh', '.bat', 
    '.sql', '.dockerfile', 'Dockerfile'
}

# 想要强制忽略的目录或文件
IGNORE_DIRS = {
    '.git', '__pycache__', 'node_modules', 'venv', '.venv', 
    'dist', 'build', '.idea', '.vscode', 'migrations'
}

IGNORE_FILES = {
    'package-lock.json', 'yarn.lock', '.DS_Store', '.env'
}
# ===========================================

def is_text_file(file_path):
    """简单判断是否为需要读取的文本文件"""
    return file_path.suffix.lower() in INCLUDE_EXTENSIONS or file_path.name in INCLUDE_EXTENSIONS

def process_repo(repo_path, output_file):
    repo_path = Path(repo_path)
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # 写入头部信息，告诉 NotebookLM 这是一个代码库合集
        outfile.write(f"# Project Codebase Dump\n")
        outfile.write(f"# Source: {repo_path.absolute()}\n\n")
        
        file_count = 0
        
        for root, dirs, files in os.walk(repo_path):
            # 修改 dirs 列表以原地过滤目录（避免遍历忽略的文件夹）
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                if file in IGNORE_FILES:
                    continue
                    
                file_path = Path(root) / file
                
                # 检查后缀
                if not is_text_file(file_path):
                    continue
                
                # 计算相对路径
                rel_path = file_path.relative_to(repo_path)
                
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # 写入分隔符和文件路径（这是给 NotebookLM 的关键提示）
                    outfile.write(f"\n{'='*50}\n")
                    outfile.write(f"File: {rel_path}\n")
                    outfile.write(f"{'='*50}\n\n")
                    
                    # 写入代码块（使用 markdown 格式）
                    # 尝试根据后缀推断语言，默认为 text
                    ext = file_path.suffix.lstrip('.') or 'text'
                    outfile.write(f"```{ext}\n")
                    outfile.write(content)
                    outfile.write(f"\n```\n")
                    
                    file_count += 1
                    print(f"Processed: {rel_path}")
                    
                except Exception as e:
                    print(f"Error reading {rel_path}: {e}")

        print(f"\nDone! Processed {file_count} files.")
        print(f"Output saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a code repository to a single text file for LLM context.")
    parser.add_argument("path", nargs="?", default=".", help="Path to the repository (default: current directory)")
    parser.add_argument("-o", "--output", default="codebase_context.md", help="Output filename (default: codebase_context.md)")
    
    args = parser.parse_args()
    
    process_repo(args.path, args.output)
