import httpx
import json

url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding"
api_key = "sk-46727326c28142b09852ab8b28dd6c98"

payload = {
    "model": "tongyi-embedding-vision-plus-2026-03-06",
    "input": {"contents": [{"text": "test embedding dimensions"}]},
    "parameters": {"dimensions": 1024},
}

print(f"[TEST] request payload: {json.dumps(payload, ensure_ascii=False)}")
resp = httpx.post(
    url,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json=payload,
    timeout=60,
)
data = resp.json()
print(f"[TEST] status_code: {resp.status_code}")
if "output" in data:
    emb = data["output"]["embeddings"][0]["embedding"]
    print(f"[TEST] actual dimensions: {len(emb)}")
else:
    print(f"[TEST] full response: {json.dumps(data, ensure_ascii=False)}")
