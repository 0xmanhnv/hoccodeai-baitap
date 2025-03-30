# Đề bài 4
# Cài đặt thư viện
"""
pip install openai
pip install python-dotenv
"""

# Hướng dẫn chạy
"""
python llm-api-4.py

# Nhập đường dẫn file gốc và ngôn ngữ dịch
file_path = "./data-4.txt"
output_file_path = "./data-4-translated.txt"
target_language = "Vietnamese"
"""

import os
import openai
from dotenv import load_dotenv


load_dotenv()
client = openai.OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

def file_to_chunks(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Chia nội dung thành các phần có độ dài 4000 token
    chunks = [content[i:i+500] for i in range(0, len(content), 500)]
    return chunks

# lưu thêm vào file, không ghi đè
def save_content_translated(content, file_path):
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(content)



def translate_content(content, target_language):

    # Tạo prompt để set giọng văn, v...v
    prompt = f"""
    Dịch nội dung sau đây sang ngôn ngữ {target_language}:
    {content}

    Đảm bảo dịch chính xác và hoàn chỉnh.
    Đảm bảo dịch đúng ngữ pháp và ngữ cảnh.
    """

    # Gửi nội dung đến API để dịch
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "system", "content": "Bạn là một người dịch chuyên nghiệp, dịch chính xác và hoàn chỉnh."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=700,
        temperature=0.4
    )

    # Lấy kết quả dịch
    translated_content = response.choices[0].message.content

    return translated_content


if __name__ == "__main__":
    load_dotenv()

    # Nhập đường dẫn file gốc và ngôn ngữ dịch
    file_path = "./data-4.txt"
    output_file_path = "./data-4-translated.txt"
    target_language = "Vietnamese"

    print(f"Đang dịch file: {file_path} sang {target_language}")

    chunks = file_to_chunks(file_path)

    for chunk in chunks:
        translated_content = translate_content(chunk, target_language)
        save_content_translated(translated_content, output_file_path)








