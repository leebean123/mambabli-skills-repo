---
name: alibaba-java-checker
description: 《阿里巴巴 Java 开发手册》规范检查器
version: 1.0.0
author: Cline Team
input:
  code:
    type: string
    description: "需要检查的 Java 代码（字符串）"
output:
  passed:
    type: boolean
    description: "是否通过规范检查（true=通过，false=未通过）"
  issues:
    type: array
    description: "违反规范的问题列表（每个问题包含 rule, message, line, severity）"
  summary:
    type: string
    description: "检查结果摘要"
---
基于《阿里巴巴 Java 开发手册》的静态代码检查，自动识别命名、日志、魔法值等常见问题。