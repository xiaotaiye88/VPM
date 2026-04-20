#!/usr/bin/env python3
"""
真实节点可用性测试 - 基于协议的实际连接测试
使用异步 TCP 连接测试节点可用性
"""
import asyncio
import base64
import re
import json
import ssl
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# 测试配置
TEST_TIMEOUT = 8.0
MAX_CONCURRENT = 20

@dataclass
class TestResult:
    node: str
    success: bool
    error: str = ""
    latency_ms: float = 0.0
    protocol: str = ""
    country: str = ""
    host: str = ""
    port: int = 0

def parse_ss_node(node: str) -> Optional[Dict[str, Any]]:
    """解析 SS 节点"""
    try:
        if not node.startswith('ss://'):
            return None
        
        content = node.split('://')[1]
        
        try:
            padding = 4 - len(content) % 4
            if padding != 4:
                content += '=' * padding
            
            decoded = base64.b64decode(content).decode('utf-8')
        except:
            if '@' in content:
                main_part = content.split('@')[0]
                try:
                    padding = 4 - len(main_part) % 4
                    if padding != 4:
                        main_part += '=' * padding
                    decoded = base64.b64decode(main_part).decode('utf-8')
                except:
                    return None
            else:
                return None
        
        if '@' in decoded:
            user_host = decoded.split('@')[1]
            if '/' in user_host:
                host_port = user_host.split('/')[0].split('?')[0]
            elif '?' in user_host:
                host_port = user_host.split('?')[0]
            else:
                host_port = user_host
            
            if ':' in host_port:
                parts = host_port.rsplit(':', 1)
                if len(parts) == 2:
                    try:
                        return {
                            'host': parts[0],
                            'port': int(parts[1])
                        }
                    except:
                        pass
        
        return None
        
    except Exception as e:
        return None

def parse_vless_node(node: str) -> Optional[Dict[str, Any]]:
    """解析 VLESS 节点"""
    try:
        if not node.startswith('vless://'):
            return None
        
        content = node.split('://')[1]
        
        if '@' not in content:
            return None
        
        host_port = content.split('?')[0].split('@')[1]
        
        if ':' in host_port:
            parts = host_port.rsplit(':', 1)
            if len(parts) == 2:
                try:
                    return {
                        'host': parts[0],
                        'port': int(parts[1])
                    }
                except:
                    pass
        
        return None
        
    except:
        return None

def parse_vmess_node(node: str) -> Optional[Dict[str, Any]]:
    """解析 VMess 节点"""
    try:
        if not node.startswith('vmess://'):
            return None
        
        content = node.split('://')[1]
        
        try:
            content = re.sub(r'[^\w+/=]', '', content)
            
            padding = 4 - len(content) % 4
            if padding != 4:
                content += '=' * padding
            
            decoded = base64.b64decode(content).decode('utf-8')
            data = json.loads(decoded)
            
            return {
                'host': data.get('add'),
                'port': data.get('port')
            }
        except:
            return None
        
    except:
        return None

def parse_trojan_node(node: str) -> Optional[Dict[str, Any]]:
    """解析 Trojan 节点"""
    try:
        if not node.startswith('trojan://'):
            return None
        
        content = node.split('://')[1]
        
        if '@' not in content:
            return None
        
        host_port = content.split('?')[0].split('#')[0].split('@')[1]
        
        if ':' in host_port:
            parts = host_port.rsplit(':', 1)
            if len(parts) == 2:
                try:
                    return {
                        'host': parts[0],
                        'port': int(parts[1])
                    }
                except:
                    pass
        
        return None
        
    except:
        return None

def parse_hysteria2_node(node: str) -> Optional[Dict[str, Any]]:
    """解析 Hysteria2 节点"""
    try:
        if not node.startswith('hysteria2://'):
            return None
        
        content = node.split('://')[1]
        
        if '@' in content:
            host_port = content.split('@')[1].split('?')[0].split('#')[0]
            
            if ':' in host_port:
                parts = host_port.rsplit(':', 1)
                if len(parts) == 2:
                    try:
                        return {
                            'host': parts[0],
                            'port': int(parts[1])
                        }
                    except:
                        pass
        
        return None
        
    except:
        return None

def extract_country(name: str) -> str:
    """从节点名称提取国家"""
    country_map = {
        '美国': 'US', '美国': 'US', 'USA': 'US', 'United': 'US',
        '日本': 'JP', '日本': 'JP', 'Japan': 'JP',
        '香港': 'HK', '香港': 'HK', 'Hong': 'HK',
        '台湾': 'TW', '台湾': 'TW', 'Taiwan': 'TW',
        '韩国': 'KR', '韩国': 'KR', 'Korea': 'KR',
        '新加坡': 'SG', '新加坡': 'SG', 'Singapore': 'SG',
        '德国': 'DE', '德国': 'DE', 'Germany': 'DE',
        '英国': 'GB', '英国': 'GB', 'UK': 'GB', 'United': 'GB',
        '法国': 'FR', '法国': 'FR', 'France': 'FR',
        '加拿大': 'CA', '加拿大': 'CA', 'Canada': 'CA',
        '澳洲': 'AU', '澳洲': 'AU', 'Australia': 'AU',
        '荷兰': 'NL', '荷兰': 'NL', 'Netherlands': 'NL',
        '越南': 'VN', '越南': 'VN', 'Vietnam': 'VN',
        '泰国': 'TH', '泰国': 'TH', 'Thailand': 'TH',
        '西班牙': 'ES', '西班牙': 'ES', 'Spain': 'ES',
        '俄罗斯': 'RU', '俄罗斯': 'RU', 'Russia': 'RU',
        '意大利': 'IT', '意大利': 'IT', 'Italy': 'IT',
        '土耳其': 'TR', '土耳其': 'TR', 'Turkey': 'TR',
        '芬兰': 'FI', '芬兰': 'FI', 'Finland': 'FI',
        '瑞典': 'SE', '瑞典': 'SE', 'Sweden': 'SE',
        '波兰': 'PL', '波兰': 'PL', 'Poland': 'PL',
        '印度': 'IN', '印度': 'IN', 'India': 'IN',
        '巴西': 'BR', '巴西': 'BR', 'Brazil': 'BR',
        '墨西哥': 'MX', '墨西哥': 'MX', 'Mexico': 'MX',
        '印尼': 'ID', '印尼': 'ID', 'Indonesia': 'ID',
        '马来西亚': 'MY', '马来西亚': 'MY', 'Malaysia': 'MY',
        '菲律宾': 'PH', '菲律宾': 'PH', 'Philippines': 'PH',
        '智利': 'CL', '智利': 'CL', 'Chile': 'CL',
        '阿根廷': 'AR', '阿根廷': 'AR', 'Argentina': 'AR',
        '沙特': 'SA', '沙特': 'SA', 'Saudi': 'SA',
        '阿联酋': 'AE', '阿联酋': 'AE', 'Dubai': 'AE',
        '迪拜': 'AE', '迪拜': 'AE', 'UAE': 'AE',
        '以色列': 'IL', '以色列': 'IL', 'Israel': 'IL',
        '南非': 'ZA', '南非': 'ZA', 'South': 'ZA',
        '乌克兰': 'UA', '乌克兰': 'UA', 'Ukraine': 'UA',
        '比利时': 'BE', '比利时': 'BE', 'Belgium': 'BE',
        '奥地利': 'AT', '奥地利': 'AT', 'Austria': 'AT',
        '瑞士': 'CH', '瑞士': 'CH', 'Switzerland': 'CH',
        '爱尔兰': 'IE', '爱尔兰': 'IE', 'Ireland': 'IE',
        '新西兰': 'NZ', '新西兰': 'NZ', 'New': 'NZ',
        '挪威': 'NO', '挪威': 'NO', 'Norway': 'NO',
        '丹麦': 'DK', '丹麦': 'DK', 'Denmark': 'DK',
        '葡萄牙': 'PT', '葡萄牙': 'PT', 'Portugal': 'PT',
        '希腊': 'GR', '希腊': 'GR', 'Greece': 'GR',
        '捷克': 'CZ', '捷克': 'CZ', 'Czech': 'CZ',
        '匈牙利': 'HU', '匈牙利': 'HU', 'Hungary': 'HU',
        '罗马尼亚': 'RO', '罗马尼亚': 'RO', 'Romania': 'RO',
        '保加利亚': 'BG', '保加利亚': 'BG', 'Bulgaria': 'BG',
        '立陶宛': 'LT', '立陶宛': 'LT', 'Lithuania': 'LT',
        '拉脱维亚': 'LV', '拉脱维亚': 'LV', 'Latvia': 'LV',
        '爱沙尼亚': 'EE', '爱沙尼亚': 'EE', 'Estonia': 'EE',
    }
    
    for cn, code in country_map.items():
        if cn in name:
            return code
    
    return "Unknown"

def parse_node(node: str) -> Optional[Dict[str, Any]]:
    """通用节点解析"""
    parsers = [
        (parse_hysteria2_node, 'hysteria2'),
        (parse_trojan_node, 'trojan'),
        (parse_vless_node, 'vless'),
        (parse_vmess_node, 'vmess'),
        (parse_ss_node, 'ss'),
    ]
    
    for parser, protocol in parsers:
        result = parser(node)
        if result:
            result['protocol'] = protocol
            
            name = node.split('#')[-1] if '#' in node else ''
            result['country'] = extract_country(name) if name else 'Unknown'
            
            return result
    
    return None

async def test_node_real(node: str, timeout: float = TEST_TIMEOUT) -> TestResult:
    """使用真实连接测试节点"""
    parsed = parse_node(node)
    
    if not parsed:
        return TestResult(
            node=node,
            success=False,
            error="无法解析节点",
            protocol="unknown"
        )
    
    protocol = parsed['protocol']
    host = parsed['host']
    port = parsed['port']
    country = parsed['country']
    
    try:
        start_time = time.time()
        
        # 根据协议类型使用不同的 SSL 配置
        if protocol in ['trojan', 'vmess', 'hysteria2']:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port, ssl=context),
                timeout=timeout
            )
        else:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=timeout
            )
        
        writer.close()
        await writer.wait_closed()
        latency = (time.time() - start_time) * 1000
        return TestResult(
            node=node,
            success=True,
            latency_ms=latency,
            protocol=protocol,
            country=country,
            host=host,
            port=port
        )
        
    except asyncio.TimeoutError:
        return TestResult(
            node=node,
            success=False,
            error="连接超时",
            protocol=protocol,
            country=country,
            host=host,
            port=port
        )
    except Exception as e:
        return TestResult(
            node=node,
            success=False,
            error=f"错误：{str(e)[:50]}",
            protocol=protocol,
            country=country,
            host=host,
            port=port
        )

async def test_all_nodes(nodes: list, max_concurrent: int = MAX_CONCURRENT) -> list:
    """批量测试节点"""
    results = []
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def test_with_limit(node):
        async with semaphore:
            return await test_node_real(node)
    
    start_time = time.time()
    
    print(f'开始测试 {len(nodes)} 个节点...\n')
    
    tasks = [test_with_limit(node) for node in nodes]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理异常情况
    final_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            final_results.append(TestResult(
                node=nodes[i],
                success=False,
                error=str(result)
            ))
        else:
            final_results.append(result)
    
    elapsed = time.time() - start_time
    
    success_count = sum(1 for r in final_results if r.success)
    
    print(f'\n测试完成，耗时 {elapsed:.1f} 秒')
    print(f'成功节点：{success_count}/{len(nodes)} ({success_count/len(nodes)*100:.1f}%)')
    
    return final_results

def save_results(results: list, output_dir: str = 'output/test_results'):
    """保存测试结果"""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存所有节点
    all_file = output_path / f'merged_{timestamp}.snippet'
    with open(all_file, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(r.node + '\n')
    
    # 保存可用节点
    available_file = output_path / f'available_{timestamp}.snippet'
    available_nodes = [r.node for r in results if r.success]
    with open(available_file, 'w', encoding='utf-8') as f:
        for node in available_nodes:
            f.write(node + '\n')
    
    # 保存详细报告
    report_file = output_path / f'report_{timestamp}.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f'测试时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'总节点数：{len(results)}\n')
        f.write(f'可用节点数：{len(available_nodes)}\n')
        f.write(f'可用率：{len(available_nodes)/len(results)*100:.1f}%\n\n')
        
        f.write('节点类型分布:\n')
        types = {}
        for r in results:
            if r.success:
                types[r.protocol] = types.get(r.protocol, 0) + 1
        
        for proto, count in sorted(types.items(), key=lambda x: -x[1]):
            f.write(f'  {proto}: {count}\n')
        
        f.write('\n国家分布:\n')
        countries = {}
        for r in results:
            if r.success:
                countries[r.country] = countries.get(r.country, 0) + 1
        
        for country, count in sorted(countries.items(), key=lambda x: -x[1]):
            f.write(f'  {country}: {count}\n')
        
        f.write('\n失败原因统计:\n')
        errors = {}
        for r in results:
            if not r.success:
                errors[r.error] = errors.get(r.error, 0) + 1
        
        for error, count in sorted(errors.items(), key=lambda x: -x[1])[:10]:
            f.write(f'  {error}: {count}\n')
    
    print(f'💾 已保存到:')
    print(f'  所有节点：{all_file}')
    print(f'  可用节点：{available_file}')
    print(f'  详细报告：{report_file}')
    
    return available_nodes

def update_base_pool(nodes: list):
    """更新基础号池"""
    with open('data/base_pool.snippet', 'w', encoding='utf-8') as f:
        for node in nodes:
            f.write(node + '\n')
    print(f'💾 已更新基础号池：data/base_pool.snippet')

async def main():
    print('='*70)
    print('🔍 真实节点可用性测试系统')
    print('='*70)
    print(f'📅 执行时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'⏱️ 超时设置：{TEST_TIMEOUT}秒')
    print(f'🔀 并发数：{MAX_CONCURRENT}')
    print()
    
    # 读取节点文件
    node_file = 'data/base_pool.snippet'
    print(f'📥 读取节点文件：{node_file}')
    
    with open(node_file, 'r', encoding='utf-8') as f:
        nodes = [line.strip() for line in f if line.strip()]
    
    print(f'共 {len(nodes)} 个节点\n')
    
    # 测试
    results = await test_all_nodes(nodes)
    
    # 保存结果
    print()
    available_nodes = save_results(results)
    
    # 更新基础号池
    print()
    update_base_pool(available_nodes)
    
    # 最终统计
    print('\n' + '='*70)
    print('✅ 测试完成!')
    print('='*70)

if __name__ == '__main__':
    asyncio.run(main())
