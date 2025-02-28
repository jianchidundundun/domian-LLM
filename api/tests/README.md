# API 测试文档

## 测试类别

### 1. 领域管理测试
- 创建、查询、更新、删除领域
- 错误处理和边界条件测试

### 2. 文档管理测试
- 文档上传、下载、查询
- 文件类型和大小限制测试
- 错误处理测试

### 3. 对话测试
- 基础对话功能
- 上下文管理
- 多轮对话测试
- 错误恢复测试

### 4. Mock服务器测试
- API 模拟测试
- 响应延迟测试
- 错误情况模拟

## 运行测试

1. 设置测试环境：
```bash
cd api/tests
./utils/setup.sh
```

2. 运行特定测试：
```bash
# 运行领域管理测试
./test_cases/domain_management/test_api.sh

# 运行文档管理测试
./test_cases/document_management/test_api.sh

# 运行对话测试
./test_cases/chat/test_api.sh

# 运行 Mock 服务器测试
./test_cases/mock_server/test_api.sh
```

3. 运行完整测试流程：
```bash
./integration/test_flow.sh
```

4. 清理测试环境：
```bash
./utils/cleanup.sh
```

## 注意事项

1. 确保后端服务正在运行
2. 测试前先清理数据库
3. 检查日志输出
4. 注意测试用例的依赖关系 