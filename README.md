# VPM - 节点测试与结果

## 项目简介

本项目用于测试和验证网络节点的可用性，自动生成可用节点清单。

## 测试工具

- `test-nodes.py`: 节点可用性测试脚本，支持多种协议（SS/VLESS/Trojan/VMess/Hysteria2）

## 使用方法

```bash
# 运行测试
python3 test-nodes.py
```

## 测试结果

### 最新测试 (2026-04-20)

- **总节点数**: 531
- **可用节点数**: 216
- **可用率**: 40.7%

### 协议分布

| 协议 | 数量 |
|------|------|
| VLESS | 172 |
| SS | 28 |
| Trojan | 13 |
| VMess | 2 |
| Hysteria2 | 1 |

详细报告请查看：`output/test_results/report_20260420-140855.txt`

## 文件说明

- `test-nodes.py` - 节点测试工具
- `output/test_results/` - 测试结果目录
- `data/base_pool.snippet` - 节点数据（本地，不上传）
- `output/latest_summary.txt` - 测试摘要

## 注意事项

- 节点数据敏感，请勿公开分享
- 定期运行测试更新可用节点列表

## 贡献

欢迎提交问题和优化建议。
