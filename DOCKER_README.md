# Docker 节点测试系统

## 快速开始

### 1. 构建镜像
```bash
docker-compose build
```

### 2. 运行测试
```bash
docker-compose run --rm node-tester
```

### 3. 查看结果
测试结果保存在 `output/` 目录

## 常用命令

```bash
# 构建镜像
docker-compose build

# 运行测试
docker-compose run --rm node-tester

# 进入交互式 shell
docker-compose run --rm node-tester-shell

# 查看日志
docker-compose logs -f

# 清理容器
docker-compose down
```

## 目录结构

```
.
├── Dockerfile          # Docker 镜像定义
├── docker-compose.yml  # Docker 编排配置
├── Makefile           # 便捷命令
├── requirements.txt   # Python 依赖
├── test-nodes.py      # 测试脚本
├── test-parse.py      # 解析测试
├── data/              # 节点数据目录
├── output/            # 测试结果输出目录
└── README.md          # 项目说明
```

## 数据持久化

- `data/base_pool.snippet` - 输入节点池（自动读取）
- `output/test_results/` - 输出测试结果

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| TEST_TIMEOUT | 8 | 超时时间（秒） |
| MAX_CONCURRENT | 20 | 并发连接数 |

## 使用 Makefile（推荐）

```bash
# 一键构建并运行
make all

# 运行测试
make run

# 进入 shell
make shell

# 查看日志
make logs

# 清理
make clean
```

## 故障排查

### 测试失败
- 检查节点文件格式是否正确
- 查看输出日志中的错误信息

### 网络连接问题
- 确保 Docker 容器可以访问互联网
- 检查防火墙设置

## 注意事项

- 节点数据敏感，请勿将 `data/` 目录提交到公开仓库
- 建议定期运行测试更新可用节点列表
