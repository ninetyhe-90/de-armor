# C++ 官方规范要点

官方来源：ISO C++ 基金会维护的 **C++ Core Guidelines**（Stroustrup / Sutter，https://isocpp.github.io/CppCoreGuidelines/）。C++ 没有官方格式化标准；Google / LLVM 风格属于社区规范，不是官方。

括号内为 Core Guidelines 条目编号，便于查证。

## 语言版本

- 以项目声明的标准为准（`CMAKE_CXX_STANDARD`、`-std=`），不使用超出该版本的特性。

## 资源与所有权

- 资源由 RAII 自动管理，不手写配对的释放逻辑（R.1）。
- 不显式调用 `new` / `delete`，用 `std::make_unique` / `std::make_shared`（R.11、C.150、C.151）。
- 用 `std::unique_ptr` 表达独占所有权，确需共享才用 `std::shared_ptr`（R.20、R.21）。
- 不通过裸指针 `T*` 或引用 `T&` 转移所有权（I.11）。
- 锁用 `std::lock_guard` / `std::scoped_lock`，不手写 `lock()` / `unlock()`（CP.20）。

## 函数与参数

- 廉价可拷贝的入参按值传递，其余按 `const&` 传递（F.16）。
- 优先返回值，不用输出参数（F.20、F.21）。
- 连续序列用 `std::span`（C++20）或容器引用，不传「指针 + 长度」（F.24、I.13）。

## 类与对象

- 能不定义默认操作就不定义（rule of zero，C.20）；定义或 `=delete` 了任一拷贝/移动/析构，就全部定义或 `=delete`（C.21）。
- 基类析构函数要么 `public virtual`，要么 `protected` 非虚（C.35）。
- 虚函数只写 `virtual`、`override`、`final` 三者之一（C.128）。
- 用 `enum class`，不用普通 `enum`（Enum.3）。

## 表达式与常量

- 对象一律初始化（ES.20），优先使用 `{}` 初始化（ES.23）。
- 默认不可变：变量与成员函数默认 `const`，编译期常量用 `constexpr`（Con.1、Con.2、Con.5）。
- 避免有损窄化转换（ES.46）；尽量不转型，必须转型时用具名转型 `static_cast` 等，不用 C 风格转型（ES.48、ES.49）。
- `auto` 用于避免重复写类型名，不用来掩盖重要类型（ES.11）。

## 错误处理

- 函数无法完成职责时抛异常（E.2），用专门设计的异常类型，不抛内置类型（E.14）。
- 按值抛出，按引用捕获（E.15）。
- 不用错误码与异常混搭；项目若明确禁用异常（`-fno-exceptions`），沿用项目既有错误返回约定。

## 头文件与命名

- 所有头文件加 include guard 或 `#pragma once`（SF.8）。
- 头文件全局作用域不写 `using namespace`（SF.7）。
- 命名优先 `underscore_style`（NL.10）；`ALL_CAPS` 只用于宏（NL.9、ES.9）。
- 类成员按约定顺序声明：类型、构造、赋值、析构、函数、数据；`public` 在前、`private` 在后（NL.16）。
- 声明符贴近类型：`int* p`（NL.18）。

## 校验

- 项目有 `.clang-format` 时只格式化改动行（`git clang-format`）。
- 项目有 `.clang-tidy` 时按其配置运行；无配置可用 `clang-tidy -checks='cppcoreguidelines-*'` 检查改动文件。
- 工具未安装就跳过，并在交付时说明未执行，不为此新增依赖。
