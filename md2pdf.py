import sys
import markdown
from weasyprint import HTML, CSS

def convert_md_to_pdf(input_path, output_path):
    print(f"📖 Reading: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 1. 将 Markdown 转为 HTML (启用 fenced_code 处理代码块)
    html_body = markdown.markdown(md_content, extensions=['fenced_code', 'tables', 'sane_lists'])

    # 2. 定义 PDF 样式 (关键：pre-wrap 让代码自动换行)
    css = CSS(string="""
        @page { margin: 1cm; size: A4; }
        body { 
            font-family: sans-serif; 
            font-size: 10pt; 
            line-height: 1.4; 
            color: #333;
        }
        /* 代码块样式 */
        pre { 
            background-color: #f6f8fa; 
            padding: 12px; 
            border-radius: 6px; 
            border: 1px solid #e1e4e8;
            white-space: pre-wrap;       /* 核心：强制保留空白并允许换行 */
            word-wrap: break-word;       /* 核心：长单词强制断行 */
            font-family: 'Courier New', monospace;
            font-size: 9pt;
        }
        /* 标题和分隔线 */
        h1 { color: #0366d6; border-bottom: 2px solid #eaecef; padding-bottom: 0.3em; }
        h2 { border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
        hr { border: 0; border-top: 1px solid #eaecef; margin: 20px 0; }
    """)

    # 3. 生成 PDF
    print("🔄 Rendering PDF...")
    HTML(string=html_body).write_pdf(output_path, stylesheets=[css])
    print(f"✅ PDF Created: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python md2pdf.py input.md output.pdf")
        sys.exit(1)
    
    convert_md_to_pdf(sys.argv[1], sys.argv[2])
