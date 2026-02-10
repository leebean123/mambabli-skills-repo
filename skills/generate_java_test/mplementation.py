import os
from jinja2 import Template
from .validators import validate_java_test
from agent.llm import call_llm  # 假设的 LLM 调用接口
from agent.state import AgentState  # 全局状态

def generate_java_test(
    state: AgentState,
    class_name: str,
    source_code: str,
    method_signature: str = None,
    framework: str = "junit5"
) -> dict:
    """
    生成 Java 单元测试的 Skill 实现
    """
    # 1. 获取项目上下文（如已知依赖）
    project_deps = state.scratchpad.get("project_dependencies", [])

    # 2. 渲染 Prompt
    with open(os.path.join(os.path.dirname(__file__), "prompt_template.j2")) as f:
        template = Template(f.read())

    prompt = template.render(
        class_name=class_name,
        method_signature=method_signature,
        source_code=source_code,
        project_deps=project_deps,
        framework=framework
    )

    # 3. 调用 LLM
    raw_output = call_llm(prompt, model="claude-3-5-sonnet")

    # 4. 校验输出
    validation = validate_java_test(raw_output)
    if not validation["valid"]:
        # 可选：自动修复或重试
        raise ValueError(f"测试生成失败: {', '.join(validation['issues'])}")

    clean_code = validation["clean_code"]

    # 5. 推导测试文件路径
    test_file_path = f"src/test/java/{class_name}Test.java"

    # 6. 写入记忆（供后续 Skill 使用）
    state.scratchpad["last_generated_test"] = {
        "class_name": class_name,
        "test_code": clean_code,
        "file_path": test_file_path
    }

    # 7. 返回结果
    return {
        "test_class": clean_code,
        "file_path": test_file_path,
        "dependencies": ["org.mockito:mockito-core", "org.junit.jupiter:junit-jupiter"]
    }