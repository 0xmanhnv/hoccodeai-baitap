# Đề bài 5: Dùng bot để... giải bài tập lập trình. Viết ứng dụng console cho phép bạn đưa câu hỏi vào, bot sẽ viết code Python/JavaScript. Sau đó, viết code lưu đáp án vào file `final.py` và chạy thử. (Dùng Python sẽ dễ hơn JavaScript nhé!)

# Cài đặt thư viện
"""
pip install openai
pip install python-dotenv
"""

# Hướng dẫn chạy
"""
python llm-api-5.py

# Nhập câu hỏi
"""

# Example
"""
Nhập câu hỏi: Hãy viết chương trình tính tổng a và b
Kết quả: 
Nhập số a: 23
Nhập số b: 34
Tổng của 23.0 và 34.0 là: 57.0
"""


import os
from dotenv import load_dotenv
import openai

load_dotenv()

client = openai.OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)


def get_code(question):
    prompt = f"""
    Viết code Python cho câu hỏi sau:
    {question}

    Đảm bảo code chạy được và đúng đáp án.
    Đảm bảo code được viết bằng ngôn ngữ Python.
    <output>
    Chỉ viết code, không viết gì thêm.
    </output>
    """

    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "system", "content": "Bạn là một chuyên gia lập trình Python."},
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content

def handle_response(response):
    # Lấy code từ response
    code = response.split("```python")[1].split("```")[0]
    return code

def save_code(code):
    with open("final.py", "w", encoding='utf-8') as f:
        f.write(code)


if __name__ == "__main__":
    question = input("Nhập câu hỏi: ")
    code = get_code(question)
    code = handle_response(code)
    save_code(code)

    # Chạy code
    print("Kết quả: ")
    os.system("python final.py")



