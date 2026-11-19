# Java 官方规范要点

官方来源：

- Oracle **Code Conventions for the Java Programming Language**：https://www.oracle.com/java/technologies/javase/codeconventions-contents.html（Oracle 已归档、不再更新，但仍是唯一官方编码规范）
- Oracle **How to Write Doc Comments for the Javadoc Tool**：https://www.oracle.com/technical-resources/articles/java/javadoc-tool.html
- The Java Tutorials（异常、try-with-resources）与 Java 语言规范（JLS）

Google Java Style 等属于社区规范，不是官方。

## 语言版本

- 以项目声明的版本为准（`maven.compiler.release`、Gradle `toolchain`），`record`、`var`、switch 表达式、文本块等只在版本支持时使用。

## 文件组织

- 每个文件一个 public 顶级类型，文件名与类型名一致。
- 顺序：`package`、`import`、类型声明。
- 类内顺序：静态变量（public -> protected -> 包级 -> private）、实例变量（同序）、构造器、方法（按功能分组，不按访问级别）。

## 命名

- 包：全小写，反向域名，如 `com.example.order`。
- 类、接口：`UpperCamelCase`，类用名词。
- 方法：`lowerCamelCase`，用动词开头。
- 变量：`lowerCamelCase`，除循环临时变量外不用单字母名。
- 常量：`UPPER_SNAKE_CASE`，声明为 `static final`。

## 格式

- 缩进单位 4 个空格。
- 每行一个声明。
- `if`、`else`、`for`、`while`、`do` 一律使用大括号，即使只有一条语句。
- `switch` 每个有意贯穿的 `case` 加注释说明，并始终写 `default`。
- 官方行宽为 80；项目格式化配置另有规定时以项目为准。

## 编程实践

- 实例变量与类变量不无理由设为 `public`，通过方法访问。
- 静态成员通过类名访问，不通过实例访问。
- 除 `-1`、`0`、`1` 外，数字字面量提取为具名常量。
- 覆写方法加 `@Override`。
- 实现 `AutoCloseable` 的资源用 try-with-resources 管理。

## 异常

- 可恢复的情况用受检异常，编程错误用非受检异常（Java Tutorials：Unchecked Exceptions — The Controversy）。
- 不捕获后忽略；不捕获 `Throwable` / `Error`。
- 重新抛出时保留原因：`throw new XxxException("...", e)`。

## Javadoc

- public / protected API 写 `/** ... */`。
- 首句是独立的摘要句。
- 按顺序使用 `@param`、`@return`、`@throws`。

## 校验

- 用 `javac -Xlint:all` 或项目构建命令（`mvn -q compile`、`gradle compileJava`）编译改动模块。
- 项目配置了 Checkstyle / Spotless / PMD 时按其运行；未配置不新增插件，工具不可用时在交付时说明。
