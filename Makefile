.PHONY: build run shell clean logs help

# 变量
IMAGE_NAME := node-tester
CONTAINER_NAME := node-tester

# 默认目标
help:
	@echo "节点测试 Docker 操作指南"
	@echo ""
	@echo "可用的命令:"
	@echo "  make build       - 构建 Docker 镜像"
	@echo "  make run         - 运行节点测试"
	@echo "  make shell       - 进入交互式容器"
	@echo "  make logs        - 查看日志"
	@echo "  make clean       - 清理容器"
	@echo "  make all         - 构建并运行"

# 构建镜像
build:
	@echo "🔨 正在构建 Docker 镜像..."
	docker-compose build --no-cache

# 运行测试
run:
	@echo "🚀 正在运行节点测试..."
	docker-compose run --rm node-tester

# 进入交互式容器
shell:
	@echo "📟 进入交互式容器..."
	docker-compose run --rm node-tester-shell

# 查看日志
logs:
	docker-compose logs -f node-tester

# 清理容器
clean:
	@echo "🧹 正在清理容器..."
	docker-compose down

# 一键构建并运行
all: build run
