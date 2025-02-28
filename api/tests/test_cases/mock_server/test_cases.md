# Mock 服务器测试用例

## 1. 模拟正常响应

### 1.1 模拟成功响应
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/mock/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": 1,
    "message": "测试消息"
  }' | json_pp
```

## 2. 模拟错误情况

### 2.1 模拟超时
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/mock/chat?delay=5000" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": 1,
    "message": "测试消息"
  }' | json_pp
```

### 2.2 模拟服务器错误
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/mock/chat?error=500" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": 1,
    "message": "测试消息"
  }' | json_pp
``` 