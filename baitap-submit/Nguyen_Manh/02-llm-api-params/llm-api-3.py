# Bài 3

## Cài đặt thư viện
"""
pip install requests
pip install beautifulsoup4
"""

## Chạy chương trình
"""
python llm-api-3.py

# Nhập URL của trang web cần tóm tắt: https://tuoitre.vn/cac-nha-khoa-hoc-nga-bao-tu-manh-nhat-20-nam-sap-do-bo-trai-dat-2024051020334196.htm
"""
import os
import requests
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv()
client = openai.OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

def get_content(url):
    # Lấy nội dung trang web
    response = requests.get(url)
    html_content = response.text

    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.find('div', {'id': 'main-detail'}).text


def get_summary(content):
    # Viết prompt và gửi nội dung đã parse lên API để tóm tắt.
    prompt = """
    Tôi có nội dung sau:
    {content}
    <Output>
    Hãy tóm tắt nội dung trên thành một bài viết ngắn gọn và dễ hiểu.
    Đảm bảo nội dung tóm tắt đầy đủ và chính xác.
    Đảm bảo nội dung tóm tắt không bị mất thông tin.
    Đảm bảo nội dung tóm tắt không bị lặp lại.
    Đảm bảo nội dung tóm tắt không bị sai lệch.
    Đảm bảo nội dung tóm tắt không bị thiếu.
    Đảm bảo nội dung tóm tắt không bị dư.
    Hãy loại bỏ các ký tự đặc biệt và các từ không cần thiết.
    </Output>
    """.format(content=content)
    messages = [
        {"role": "system", "content": "Bạn là một chuyên gia tóm tắt nội dung website."},
        {"role": "user", "content": prompt}
    ]

    chat_completion = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=messages,
        temperature=0.7, # Điều chỉnh độ tự nhiên của chatbot
        stream=True
    )

    new_msg = ""
    print("Tóm tắt: ", end="", flush=True)
    for chunk in chat_completion:
        new_msg += chunk.choices[0].delta.content or ""
        print(chunk.choices[0].delta.content or "", end="", flush=True)
    print("\n--------------------------------")



if __name__ == "__main__":

    # URL của trang web cần tóm tắt
    # example_url = "https://tuoitre.vn/cac-nha-khoa-hoc-nga-bao-tu-manh-nhat-20-nam-sap-do-bo-trai-dat-2024051020334196.htm"
    url = ""
    content = ""

    url = input("Nhập URL của trang web cần tóm tắt: ")
    content = get_content(url)

    get_summary(content)
