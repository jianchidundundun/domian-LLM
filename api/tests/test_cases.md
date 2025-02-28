# API 测试用例

## 1. 领域管理测试

### 1.1 创建领域
```bash
# 创建信号处理领域
curl -X POST http://127.0.0.1:8000/api/v1/domains \
  -H "Content-Type: application/json" \
  -d '{"name":"信号处理","description":"这是一个信号处理领域"}' | json_pp

# 预期响应
{
   "status": "success",
   "domain_id": 1
}
```

### 1.2 获取领域列表
```bash
curl http://127.0.0.1:8000/api/v1/domains | json_pp

# 预期响应
{
   "domains": [
      {
         "id": 1,
         "name": "信号处理",
         "description": "这是一个信号处理领域"
      }
   ]
}
```

## 2. 文档管理测试

### 2.1 上传文档
```bash
# 创建测试文档
echo "信号处理基础概念..." > test_documents.txt

# 上传文档
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "file=@test_documents.txt" \
  -F "domain_id=1" | json_pp

# 预期响应
{
   "status": "success",
   "document_id": 1,
   "filename": "test_documents.txt"
}
```

### 2.2 获取文档列表
```bash
curl "http://127.0.0.1:8000/api/v1/documents?domain_id=1" | json_pp

# 预期响应
{
   "documents": [
      {
         "id": 1,
         "filename": "test_documents.txt",
         "created_at": "2024-02-28T12:34:56.789Z"
      }
   ]
}
```

## 3. 错误处理测试

### 3.1 创建重复领域
```bash
# 尝试创建同名领域
curl -X POST http://127.0.0.1:8000/api/v1/domains \
  -H "Content-Type: application/json" \
  -d '{"name":"信号处理","description":"重复的领域"}' | json_pp

# 预期响应
{
   "detail": "Domain with this name already exists"
}
```

### 3.2 上传无效文件
```bash
# 尝试上传不支持的文件类型
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "file=@test.jpg" \
  -F "domain_id=1" | json_pp

# 预期响应
{
   "detail": "Unsupported file type"
}
```

### 3.3 访问不存在的领域
```bash
curl "http://127.0.0.1:8000/api/v1/documents?domain_id=999" | json_pp

# 预期响应
{
   "documents": []
}
```

## 4. 完整测试流程

1. 启动后端服务：
```bash
cd api
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

2. 执行测试：
```bash
# 1. 创建领域
curl -X POST http://127.0.0.1:8000/api/v1/domains \
  -H "Content-Type: application/json" \
  -d '{"name":"信号处理","description":"这是一个信号处理领域"}'

# 2. 上传文档
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "file=@tests/test_documents.txt" \
  -F "domain_id=1"

# 3. 查看文档列表
curl "http://127.0.0.1:8000/api/v1/documents?domain_id=1"
```

## 5. 注意事项

1. 文件大小限制：10MB
2. 支持的文件类型：.txt, .md, .pdf
3. 每个领域名称必须唯一
4. 所有 API 响应都包含 status 字段
5. 错误响应包含 detail 字段描述错误原因 