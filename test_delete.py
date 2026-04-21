import requests
import json

# 测试创建笔记
def test_create_note():
    url = "http://localhost:8000/api/notes"
    data = {
        "raw_content": "测试删除功能",
        "source_type": "test"
    }
    response = requests.post(url, json=data)
    print(f"创建笔记响应: {response.status_code}")
    print(f"响应内容: {response.text}")
    if response.status_code == 200:
        return response.json()
    return None

# 测试获取笔记列表
def test_get_notes():
    url = "http://localhost:8000/api/notes"
    response = requests.get(url)
    print(f"获取笔记列表响应: {response.status_code}")
    print(f"响应内容: {response.text}")
    if response.status_code == 200:
        return response.json()
    return None

# 测试删除笔记
def test_delete_note(note_id):
    url = f"http://localhost:8000/api/notes/{note_id}"
    response = requests.delete(url)
    print(f"删除笔记响应: {response.status_code}")
    print(f"响应内容: {response.text}")
    return response.status_code

if __name__ == "__main__":
    print("=== 测试删除功能 ===")
    
    # 创建测试笔记
    note = test_create_note()
    if not note:
        print("创建笔记失败")
        exit(1)
    
    note_id = note.get("id")
    print(f"创建的笔记ID: {note_id}")
    
    # 获取笔记列表确认创建成功
    notes = test_get_notes()
    print(f"当前笔记数量: {notes.get('total', 0)}")
    
    # 测试删除笔记
    status_code = test_delete_note(note_id)
    if status_code == 200:
        print("删除笔记成功!")
    else:
        print("删除笔记失败!")
    
    # 再次获取笔记列表确认删除成功
    notes = test_get_notes()
    print(f"删除后笔记数量: {notes.get('total', 0)}")
    print("=== 测试完成 ===")
