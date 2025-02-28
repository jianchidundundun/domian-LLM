# 服务注册测试用例

## 1. 基础服务注册测试

### 1.1 注册 MATLAB 滤波器服务
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/services/register" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "信号处理",
    "service_name": "matlab_filters",
    "description": "MATLAB 滤波器服务",
    "endpoint_url": "http://localhost:8001/matlab",
    "service_type": "matlab",
    "methods": {
      "lowpass": {
        "parameters": {
          "signal": "array",
          "cutoff_freq": "float",
          "sampling_rate": "float"
        },
        "returns": {
          "filtered_signal": "array"
        }
      }
    }
  }'

# 预期响应
{
  "status": "success",
  "message": "Service registered successfully"
}
```

### 1.2 查询领域服务
```bash
curl "http://127.0.0.1:8000/api/v1/services/信号处理" | json_pp

# 预期响应
{
  "services": [
    {
      "id": 1,
      "name": "matlab_filters",
      "description": "MATLAB 滤波器服务",
      "endpoint_url": "http://localhost:8001/matlab",
      "service_type": "matlab",
      "methods": {
        "lowpass": {
          "parameters": {
            "signal": "array",
            "cutoff_freq": "float",
            "sampling_rate": "float"
          },
          "returns": {
            "filtered_signal": "array"
          }
        }
      }
    }
  ]
}
```

## 2. 错误处理测试

### 2.1 注册到不存在的领域
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/services/register" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "不存在的领域",
    "service_name": "test_service",
    "description": "测试服务",
    "endpoint_url": "http://localhost:8001/test",
    "service_type": "test",
    "methods": {}
  }'

# 预期响应
{
  "detail": "Domain 不存在的领域 not found"
}
```

### 2.2 使用无效的 URL
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/services/register" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "信号处理",
    "service_name": "invalid_service",
    "description": "无效服务",
    "endpoint_url": "invalid-url",
    "service_type": "test",
    "methods": {}
  }'

# 预期响应
{
  "detail": [
    {
      "loc": ["body", "endpoint_url"],
      "msg": "invalid or missing URL scheme",
      "type": "value_error.url.scheme"
    }
  ]
}
```

## 3. 服务生命周期测试

### 3.1 更新现有服务
```bash
# 使用相同的 service_name 重新注册，应该更新而不是创建新服务
curl -X POST "http://127.0.0.1:8000/api/v1/services/register" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "信号处理",
    "service_name": "matlab_filters",
    "description": "更新后的服务描述",
    "endpoint_url": "http://localhost:8001/matlab/v2",
    "service_type": "matlab",
    "methods": {
      "lowpass": {
        "parameters": {
          "signal": "array",
          "cutoff_freq": "float"
        },
        "returns": {
          "filtered_signal": "array"
        }
      }
    }
  }'
```

### 3.2 停用服务
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/services/1"

# 预期响应
{
  "status": "success",
  "message": "Service deactivated"
}
```

## 运行完整测试
```bash
cd api/tests/test_cases/service_registry
chmod +x test_api.sh
./test_api.sh
``` 