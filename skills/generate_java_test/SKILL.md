# Generate Java Unit Test

为指定的 Java 类或方法生成符合 JUnit 5 规范的单元测试代码。

## 功能说明
- 自动生成高覆盖率的 JUnit 5 测试类
- 自动识别依赖并建议 Mockito mock
- 遵循命名规范（XxxTest）
- 输出可直接写入项目的测试文件

## 输入参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `class_name` | string | ✅ | 被测 Java 类名（如 `UserService`） |
| `source_code` | string | ✅ | 被测类的完整源代码 |
| `method_signature` | string | ❌ | 可选：仅针对特定方法生成测试 |
| `framework` | string | ❌ | 测试框架，默认 `junit5` |

## 输出结果
```json
{
  "test_class": "string",      // 生成的测试类 Java 代码
  "file_path": "string",       // 建议保存路径（如 src/test/java/UserServiceTest.java）
  "dependencies": ["string"]   // 需要添加的 Maven/Gradle 依赖
}