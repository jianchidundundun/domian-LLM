# 对话测试用例

## 1. 基础对话测试

### 1.1 单轮对话
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": 1,
    "message": "什么是低通滤波器？"
  }' | json_pp
```

### 1.2 多轮对话
```bash
# 第一轮
curl -X POST "http://127.0.0.1:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": 1,
    "message": "什么是滤波器？",
    "conversation_id": "new"
  }' | json_pp

# 第二轮（使用返回的conversation_id）
curl -X POST "http://127.0.0.1:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": 1,
    "message": "具体有哪些类型？",
    "conversation_id": "CONV_ID"
  }' | json_pp
```

## 2. 错误处理测试

### 2.1 无效的领域ID
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": 999,
    "message": "测试消息"
  }' | json_pp
```

### 2.2 空消息
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": 1,
    "message": ""
  }' | json_pp
``` 