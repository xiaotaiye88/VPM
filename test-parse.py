#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/jim')

import base64
import re
import json

def parse_ss_node(node: str):
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
        except Exception as e:
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
        print(f"SS 解析错误：{e}")
        return None

def parse_vless_node(node: str):
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
        
    except Exception as e:
        print(f"VLESS 解析错误：{e}")
        return None

def parse_vmess_node(node: str):
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
        
    except Exception as e:
        print(f"VMess 解析错误：{e}")
        return None

def parse_trojan_node(node: str):
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
        
    except Exception as e:
        print(f"Trojan 解析错误：{e}")
        return None

def parse_hysteria2_node(node: str):
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
        
    except Exception as e:
        print(f"Hysteria2 解析错误：{e}")
        return None

def parse_node(node: str):
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
            
            return result
    
    return None

# 读取一些示例节点
with open('/Users/jim/data/base_pool.snippet', 'r', encoding='utf-8') as f:
    nodes = [line.strip() for line in f if line.strip()][:10]

print("示例节点解析测试:")
for node in nodes:
    result = parse_node(node)
    print(f"\n节点类型：{node.split('://')[0] if '://' in node else 'unknown'}")
    print(f"前 80 字符：{node[:80]}...")
    print(f"解析结果：{result}")
