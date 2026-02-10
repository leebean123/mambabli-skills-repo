# JUnit 5 最佳实践

## 注解使用
- @Test - 标记测试方法
- @BeforeEach - 每个测试前执行
- @AfterEach - 每个测试后执行
- @ExtendWith - 扩展测试行为（Mockito, Spring）

## 断言方式
- 使用 AssertJ（更流畅）：assertThat(actual).isEqualTo(expected)
- 避免 JUnit 原生断言（不够直观）

## 异常测试
- 使用 assertThatThrownBy(() -> {...}).isInstanceOf(...)
- 避免 @Test(expected = ...)
  EOF

# 4. 提交并测试
git add .opencode/skills/java-unit-test-generator/
git commit -m "feat: add java unit test generator skill"
killall -9 opencode 2>/dev/null
opencode

# 5. 使用
# 输入：为 UserService 生成单元测试