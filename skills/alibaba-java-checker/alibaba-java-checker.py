#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里巴巴 Java 开发手册规范检查器（Cline Skill）
输入：{"code": "Java 代码字符串"}
输出：{"success": true, "passed": false, "issues": [...], "summary": "..."}
"""

import sys
import json
import re

def check_alibaba_java_rules(code: str):
    """检查代码是否符合阿里巴巴 Java 开发手册规范"""
    issues = []

    # 规则1: 禁止 System.out.println
    if 'System.out.println' in code:
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if 'System.out.println' in line and not line.strip().startswith('//'):
                issues.append({
                    "rule": "ALI-001",
                    "message": "禁止使用 System.out.println，请使用 SLF4J 日志框架（如 log.info(...)）",
                    "line": i + 1,
                    "severity": "error"
                })

    # 规则2: 类名必须 UpperCamelCase
    class_match = re.search(r'class\s+(\w+)', code)
    if class_match:
        class_name = class_match.group(1)
        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
            issues.append({
                "rule": "ALI-002",
                "message": f"类名 '{class_name}' 必须使用 UpperCamelCase（如 UserService）",
                "severity": "warning"
            })

    # 规则3: 魔法值检查（除 -1,0,1）
    magic_numbers = re.findall(r'(?<!\w)([+-]?\d+)(?!\w)', code)
    for num_str in set(magic_numbers):
        try:
            num = int(num_str)
            if num not in (-1, 0, 1):
                # 定位行号（简化版）
                for i, line in enumerate(code.split('\n')):
                    if num_str in line and not line.strip().startswith('//'):
                        issues.append({
                            "rule": "ALI-003",
                            "message": f"避免魔法值 {num_str}，建议定义为常量（如 private static final int MAX_RETRY = {num_str};）",
                            "line": i + 1,
                            "severity": "warning"
                        })
                        break
        except ValueError:
            continue

    # 规则4: 禁止返回 null（集合方法）
    if 'return null' in code:
        for i, line in enumerate(code.split('\n')):
            if 'return null' in line and not line.strip().startswith('//'):
                issues.append({
                    "rule": "ALI-004",
                    "message": "禁止返回 null，集合方法应返回 Collections.emptyList()",
                    "line": i + 1,
                    "severity": "error"
                })

    # 规则5: 禁止捕获 Exception
    if 'catch (Exception' in code:
        for i, line in enumerate(code.split('\n')):
            if 'catch (Exception' in line and not line.strip().startswith('//'):
                issues.append({
                    "rule": "ALI-005",
                    "message": "禁止捕获 Exception，应捕获具体异常类型（如 NullPointerException）",
                    "line": i + 1,
                    "severity": "error"
                })

    # 规则6: 空指针检查（未判空）
    null_risk = re.findall(r'(\w+)\.(\w+)\(', code)
    for var, method in null_risk:
        if var not in ['this', 'super'] and not re.search(f'if\\s+{var}\\s+!=\\s+null', code):
            issues.append({
                "rule": "ALI-006",
                "message": f"变量 '{var}' 可能为空，调用 '{method}()' 前建议判空",
                "severity": "warning"
            })

    return issues

def main():
    """Cline 调用入口"""
    try:
        input_data = json.load(sys.stdin)
        code = input_data.get('code', '')

        issues = check_alibaba_java_rules(code)

        result = {
            "success": True,
            "passed": len(issues) == 0,
            "issues": issues,
            "summary": f"共发现 {len(issues)} 个违反阿里规范的问题"
        }
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }))

if __name__ == "__main__":
    main()