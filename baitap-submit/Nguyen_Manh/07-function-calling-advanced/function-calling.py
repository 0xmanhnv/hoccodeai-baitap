# Bài 7

## Hướng dẫn cài đặt
"""
1. Cài đặt các package cần thiết

```bash
pip install -r requirements.txt
```

2. Tạo file `.env` và thêm các biến môi trường

```bash
OPENAI_API_KEY=<OPENAI_API_KEY>
OPENAI_BASE_URL=<OPENAI_BASE_URL>
MODEL_NAME=<MODEL_NAME>
JINA_API_KEY=<JINA_API_KEY>
WEATHER_API_KEY=<WEATHER_API_KEY>
STOCK_API_KEY=<STOCK_API_KEY>
```

3. Chạy file `function-calling.py`

```bash
python function-calling.py
```
"""

## Exammple
"""
(venv) PS D:\RnD\LLM\hoccodeai-baitap\baitap-submit\Nguyen_Manh\07-function-calling-advanced> python .\function-calling.py
Bạn: Cho anh biết thời tiết hiện tại đi nào
Bot: Đang truy vấn thông tin...
Bot: Hiện tại ở Hà Nội có thời tiết nhiều mây với nhiệt độ 16.4°C. Bạn có muốn biết thêm thông tin gì khác không? Ví dụ như dự báo thời tiết trong ngày hay các thành phố khác?
Bạn: tôi đang muốn tìm hiểu chứng cổ phiếu NVDIA, không nhớ tên nữa, nhưng mà công ty sản xuất GPU ấy
Bot: Đang truy vấn thông tin...
Bot: Hiện tại, giá cổ phiếu NVIDIA (NVDA) đang là 111.41 đô la Mỹ. Bạn có muốn tôi tìm thêm thông tin gì về cổ phiếu này không, ví dụ như biến động giá trong thời gian qua, hoặc các tin tức liên quan đến công ty?
Bạn: ok, cảm ơn nheng, tốt đấy
Bot: Rất vui vì đã giúp được bạn! Nếu bạn cần thêm thông tin gì khác, cứ hỏi nhé.
Bạn: exit
"""


import os
from pprint import pprint
from typing import TypedDict, Annotated, Literal
from pydantic import TypeAdapter
import inspect
import json
from openai import OpenAI
import requests
from dotenv import load_dotenv

load_dotenv()

MESSAGES = [
    {
        "role": "system",
        "content": "Bạn là một bot chat hỗ trợ người dùng tìm kiếm thông tin trên internet."
    }
]

# https://platform.openai.com/api-keys
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_BASE_URL')
)


def get_current_weather(location: str, unit: Literal["celsius", "fahrenheit"] = "celsius"):
    """Lấy thông tin thời tiết hiện tại ở một địa điểm cụ thể"""
    try:
        # implement https://api.weatherapi.com/v1/current.json?key=963ea3fc34e54f40b64140711253003&q=Hà Nội&aqi=yes
        url = f"https://api.weatherapi.com/v1/current.json?key={os.getenv('WEATHER_API_KEY')}&q={location}&aqi=yes"
        response = requests.get(url)
        
        if response.status_code != 200:
            return f"Không thể lấy thông tin thời tiết cho {location}. Lỗi: {response.status_code}"
            
        data = response.json()
        if unit == "celsius":
            return f"Thời tiết tại {location} là {data['current']['temp_c']}°C, {data['current']['condition']['text']}."  
        else:
            return f"Thời tiết tại {location} là {data['current']['temp_f']}°F, {data['current']['condition']['text']}."
    except Exception as e:
        # Trả về giá trị mặc định nếu có lỗi với API
        if unit == "celsius":
            return f"Thời tiết tại {location} là 22°C, trời nhiều mây."
        else:
            return f"Thời tiết tại {location} là 72°F, trời nhiều mây."


def get_stock_price(symbol: str):
    """Lấy giá cổ phiếu của một cổ phiếu cụ thể"""
    try:
        # implement https://api.stockdata.org/v1/data/quote?symbols=AAPL&api_token=1234567890
        url = f"https://api.stockdata.org/v1/data/quote?symbols={symbol}&api_token={os.getenv('STOCK_API_KEY')}"
        response = requests.get(url)
        
        if response.status_code != 200:
            return f"Không thể lấy thông tin cổ phiếu cho {symbol}. Lỗi: {response.status_code}"
            
        data = response.json()
        if data['data'] and len(data['data']) > 0:
            return f"Giá cổ phiếu của {symbol} là {data['data'][0]['price']} USD."
        else:
            return f"Không tìm thấy thông tin cổ phiếu cho {symbol}."
    except Exception as e:
        # Trả về thông báo lỗi nếu có vấn đề với API
        return f"Không thể lấy thông tin cổ phiếu cho {symbol}. Lỗi: {str(e)}"


# Bài 2: Implement hàm `view_website`, sử dụng `requests` và JinaAI để đọc markdown từ URL
def view_website(url: str):
    """Trích xuất nội dung markdown từ một trang web sử dụng JinaAI Reader"""
    try:
        # Sử dụng Jina AI Reader API
        jina_api_url = "https://r.jina.ai/"
        headers = {
            "Authorization": f"Bearer {os.getenv('JINA_API_KEY')}",
            "X-Return-Format": "markdown",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url
        }
        
        response = requests.post(jina_api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.text
        else:
            return f"Lỗi khi trích xuất nội dung: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Lỗi khi truy cập trang web: {str(e)}"


# Sử dụng inspect và TypeAdapter để định nghĩa tools
def convert_function_to_tool(func):
    schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
    
    signature = inspect.signature(func)
    for param_name, param in signature.parameters.items():
        # Lấy thông tin từ annotation
        annotation = param.annotation
        if annotation == inspect.Parameter.empty:
            # Mặc định là string nếu không có annotation
            schema["function"]["parameters"]["properties"][param_name] = {"type": "string"}
        else:
            # Xử lý các loại annotation khác nhau
            if hasattr(annotation, "__origin__") and annotation.__origin__ is Literal:
                # Xử lý Literal
                schema["function"]["parameters"]["properties"][param_name] = {
                    "type": "string",
                    "enum": list(annotation.__args__)
                }
            else:
                # Xử lý các kiểu dữ liệu cơ bản
                type_map = {str: "string", int: "integer", float: "number", bool: "boolean"}
                param_type = type_map.get(annotation, "string")
                schema["function"]["parameters"]["properties"][param_name] = {"type": param_type}
        
        # Kiểm tra xem param có required không
        if param.default == inspect.Parameter.empty and param_name != "self":
            schema["function"]["parameters"]["required"].append(param_name)
    
    return schema

def get_completion(msg, tools):
    output_required = """
    Hãy trả lời câu hỏi bằng tiếng Việt.
    Hãy tập trung trả lời trọng tâm câu hỏi gần nhất, không nên trả lời nhiều hơn cần thiết.
    Câu trả lời của bạn phải ngắn gọn, không nên dài dòng, gần gũi như người yêu thực sự.
    Hãy trả lời câu hỏi một cách tự nhiên và tự nhiên nhất có thể, có giọng điệu phù hợp với tính cách của bạn.
    """

    # Nếu có tools thì dùng tools, nếu không thì không dùng
    if tools:
        MESSAGES.append({"role": "user", "content": msg})
        chat_completion = client.chat.completions.create(
            model=os.getenv('MODEL_NAME'),
            messages=MESSAGES,
            tools=tools,
            tool_choice="auto"  # Đảm bảo LLM sẽ chọn công cụ phù hợp
        )
    else:
        MESSAGES.append({"role": "user", "content": msg + "\n<output>" + output_required + "</output>"})
        
        chat_completion = client.chat.completions.create(
            model=os.getenv('MODEL_NAME'),
            messages=MESSAGES
        )

    return chat_completion

def get_completion_with_tool_result(assistant_msg, result):
    """Gửi kết quả từ tool call lên cho LLM và lấy phản hồi cuối cùng"""
    
    MESSAGES.append(assistant_msg)
    MESSAGES.append({
        "role": "tool",
        "content": result,
        "tool_call_id": assistant_msg.tool_calls[0].id
    })
    
    final_response = client.chat.completions.create(
        model=os.getenv('MODEL_NAME'),
        messages=MESSAGES
    )

    return final_response

if __name__ == "__main__":

    # Tạo tools từ các hàm
    tools = [
        convert_function_to_tool(get_current_weather),
        convert_function_to_tool(view_website),
        convert_function_to_tool(get_stock_price)
    ]


    # Nhận input từ người dùng
    user_input = input("Bạn: ")
    while user_input != "exit":
        # Gửi message lên cho LLM
        response = get_completion(user_input, tools)
        assistant_message = response.choices[0].message
        content = assistant_message.content or ""
        
        # Kiểm tra xem có tool_calls không
        if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
            tool_call = assistant_message.tool_calls[0]
            
            # In ra thông báo đang truy vấn thông tin
            print(f"Bot: Đang truy vấn thông tin...")
            
            # Gọi hàm
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            if function_name == 'get_current_weather':
                location = arguments.get('location')
                unit = arguments.get('unit', 'celsius')
                result = get_current_weather(location, unit)
            elif function_name == 'view_website':
                url = arguments.get('url')
                result = view_website(url)
            elif function_name == 'get_stock_price':
                symbol = arguments.get('symbol')
                result = get_stock_price(symbol)
            else:
                result = f"Không tìm thấy hàm {function_name}"

            # Gửi kết quả lên cho LLM
            final_response = get_completion_with_tool_result(assistant_message, result)
            print(f"Bot: {final_response.choices[0].message.content}")
        
        # Kiểm tra định dạng [TOOL_REQUEST] trong nội dung - cách thay thế
        elif "[TOOL_REQUEST]" in content:
            print(f"Bot: Đang truy vấn thông tin...")
            
            # Trích xuất thông tin tool request từ chuỗi
            try:
                # Loại bỏ phần [TOOL_REQUEST] và [END_TOOL_REQUEST]
                tool_request = content.split("[TOOL_REQUEST]")[1].split("[END_TOOL_REQUEST]")[0].strip()
                
                # Làm sạch chuỗi JSON (loại bỏ các kí tự đặc biệt có thể gây lỗi)
                tool_request = tool_request.replace('\n', '').replace('\r', '').strip()
                if tool_request.startswith('{'):
                    # Nếu JSON hợp lệ
                    tool_data = json.loads(tool_request)
                else:
                    # Thử xử lý định dạng khác
                    lines = tool_request.split('\n')
                    json_line = ''
                    for line in lines:
                        if '{' in line and '}' in line:
                            json_line = line.strip()
                            break
                    tool_data = json.loads(json_line)
                
                function_name = tool_data.get("name")
                arguments = tool_data.get("arguments", {})
                
                # Gọi hàm tương ứng
                if function_name == 'get_current_weather':
                    location = arguments.get('location')
                    unit = arguments.get('unit', 'celsius')
                    result = get_current_weather(location, unit)
                elif function_name == 'view_website':
                    url = arguments.get('url')
                    result = view_website(url)
                elif function_name == 'get_stock_price':
                    symbol = arguments.get('symbol')
                    result = get_stock_price(symbol)
                else:
                    result = f"Không tìm thấy hàm {function_name}"
                
                # Gửi kết quả trực tiếp đến LLM với nội dung cập nhật
                updated_msg = f"Tôi đã tìm thông tin cho bạn. Đây là kết quả: {result}"
                MESSAGES.append({"role": "assistant", "content": updated_msg})
                
                # Gửi lại để LLM xử lý kết quả
                follow_up_response = client.chat.completions.create(
                    model=os.getenv('MODEL_NAME'),
                    messages=MESSAGES
                )
                
                print(f"Bot: {follow_up_response.choices[0].message.content}")
                
                # Cập nhật lại messages
                MESSAGES.append({"role": "assistant", "content": follow_up_response.choices[0].message.content})
                
            except Exception as e:
                print(f"Bot: Tôi gặp lỗi khi xử lý yêu cầu của bạn: {str(e)}")
        else:
            print(f"Bot: {content}")

        user_input = input("Bạn: ")

