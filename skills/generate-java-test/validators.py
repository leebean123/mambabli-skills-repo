import re
import logging
from typing import Dict, List, Any, Tuple

# 配置日志（可选）
logger = logging.getLogger(__name__)

class JavaTestValidator:
    """Java 测试代码校验器"""

    def __init__(self):
        # 常见安全敏感模式（防止 LLM 生成危险代码）
        self.dangerous_patterns = [
            (r'\b(Runtime|ProcessBuilder)\.getRuntime\(\)', "禁止使用 Runtime 执行系统命令"),
            (r'\bexec\(', "禁止调用 exec()"),
            (r'new ProcessBuilder', "禁止创建进程"),
            (r'System\.exit', "禁止调用 System.exit()"),
        ]

        # JUnit 5 必需元素
        self.junit5_required_imports = [
            "org.junit.jupiter.api.Test",
            "org.junit.jupiter.api.BeforeEach",
            "org.junit.jupiter.api.AfterEach",
        ]

    def validate(self, raw_output: str, target_class_name: str = None) -> Dict[str, Any]:
        """
        主校验入口

        Args:
            raw_output: LLM 原始输出（可能含 markdown）
            target_class_name: 被测类名（用于语义校验）

        Returns:
            {
                "valid": bool,
                "clean_code": str,      # 清理后的纯 Java 代码
                "errors": List[str],    # 致命错误（导致无效）
                "warnings": List[str],  # 警告（可接受但不推荐）
                "suggestions": List[str] # 改进建议
            }
        """
        result = {
            "valid": False,
            "clean_code": "",
            "errors": [],
            "warnings": [],
            "suggestions": []
        }

        # Step 1: 提取 Java 代码块
        code = self._extract_java_code(raw_output)
        if not code:
            result["errors"].append("未找到有效的 ```java 代码块")
            return result

        result["clean_code"] = code

        # Step 2: 安全校验（首要！）
        safe, safety_issues = self._check_safety(code)
        if not safe:
            result["errors"].extend(safety_issues)
            return result

        # Step 3: 基础语法与结构校验
        struct_issues = self._check_structure(code, target_class_name)
        result["errors"].extend(struct_issues.get("errors", []))
        result["warnings"].extend(struct_issues.get("warnings", []))
        result["suggestions"].extend(struct_issues.get("suggestions", []))

        # Step 4: 决定是否有效
        result["valid"] = len(result["errors"]) == 0

        return result

    def _extract_java_code(self, text: str) -> str:
        """从 LLM 输出中提取 Java 代码"""
        # 匹配 ```java ... ``` 或 ``` ... ```
        code_block_match = re.search(r"```(?:java)?\s*\n?(.*?)\n?```", text, re.DOTALL | re.IGNORECASE)
        if code_block_match:
            return code_block_match.group(1).strip()

        # 如果没有代码块，尝试整个文本（保守策略）
        lines = text.strip().split('\n')
        if lines and (lines[0].startswith('public class') or lines[0].startswith('import')):
            return text.strip()

        return ""

    def _check_safety(self, code: str) -> Tuple[bool, List[str]]:
        """检查危险代码模式"""
        issues = []
        for pattern, msg in self.dangerous_patterns:
            if re.search(pattern, code):
                issues.append(msg)
        return len(issues) == 0, issues

    def _check_structure(self, code: str, target_class_name: str = None) -> Dict[str, List[str]]:
        """检查测试结构合规性"""
        issues = {"errors": [], "warnings": [], "suggestions": []}

        # 检查 JUnit 5 导入
        has_junit_import = any(
            imp in code for imp in [
                "import org.junit.jupiter.api.Test;",
                "import static org.junit.jupiter.api.Assertions.*;"
            ]
        )
        if not has_junit_import:
            issues["errors"].append("缺少 JUnit 5 相关导入（应包含 @Test）")

        # 检查测试类命名
        test_class_match = re.search(r"public\s+class\s+(\w+)", code)
        if not test_class_match:
            issues["errors"].append("未找到 public class 定义")
        else:
            test_class_name = test_class_match.group(1)
            if not test_class_name.endswith("Test"):
                issues["warnings"].append(f"测试类名 '{test_class_name}' 应以 'Test' 结尾")

            # 如果知道被测类名，检查是否匹配
            if target_class_name and not test_class_name.startswith(target_class_name):
                issues["suggestions"].append(
                    f"建议测试类命名为 '{target_class_name}Test' 以匹配被测类"
                )

        # 检查至少一个 @Test 方法
        test_methods = re.findall(r"@Test\b", code)
        if len(test_methods) == 0:
            issues["errors"].append("未找到任何 @Test 注解的方法")

        # 检查是否包含 main 方法（不应有）
        if "public static void main" in code:
            issues["warnings"].append("测试类中不应包含 main 方法")

        # 检查 Mockito 使用（如果用了 mock 但没导入）
        if "mock(" in code or "when(" in code or "verify(" in code:
            if "import org.mockito" not in code:
                issues["warnings"].append("检测到 Mockito 用法但缺少相关导入")

        return issues


# 全局函数接口（便于外部调用）
def validate_java_test(
    raw_output: str,
    target_class_name: str = None,
    strict: bool = True
) -> Dict[str, Any]:
    """
    校验 Java 测试代码的便捷函数

    Args:
        raw_output: LLM 原始输出
        target_class_name: 被测类名（用于命名建议）
        strict: 是否将警告视为错误（默认 True）

    Returns:
        校验结果字典
    """
    validator = JavaTestValidator()
    result = validator.validate(raw_output, target_class_name)

    # 严格模式：警告也视为错误
    if strict and result["warnings"]:
        result["errors"].extend(result["warnings"])
        result["valid"] = False

    logger.debug(f"Java test validation result: {result}")
    return result