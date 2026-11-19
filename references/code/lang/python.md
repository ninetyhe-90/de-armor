# Python 官方规范要点

官方来源：

- **PEP 8** 代码风格：https://peps.python.org/pep-0008/
- **PEP 257** 文档字符串：https://peps.python.org/pep-0257/
- **PEP 484 / 585 / 604** 类型注解
- Python 官方文档（tutorial、`subprocess`、`pickle`、`secrets` 等模块文档）

Black、Ruff 等是社区工具，与 PEP 8 兼容；项目已配置时直接使用。

## 语言版本

- 以项目声明为准（`pyproject.toml` 的 `requires-python`、`.python-version`）。
- 3.9 及以上用内置泛型 `list[int]`、`dict[str, int]`（PEP 585）；3.10 及以上用 `X | None`（PEP 604）。

## 布局

- 缩进 4 个空格，不用 Tab。
- 行宽 79，文档字符串与注释 72；团队约定可放宽到 99。
- 顶层函数与类之间空两行，方法之间空一行。

## 导入

- 写在文件顶部，分三组并以空行隔开：标准库、第三方、本地。
- 优先绝对导入；不用 `from x import *`。
- 每行导入一个模块：`import os` 与 `import sys` 分开写。

## 命名

- 模块、包：短的全小写名，模块可用下划线。
- 函数、变量、方法：`snake_case`。
- 类、异常：`CapWords`；异常类名以 `Error` 结尾（确为错误时）。
- 常量：`UPPER_SNAKE_CASE`，定义在模块级。
- 非公开成员加单下划线前缀 `_name`。
- 实例方法第一个参数是 `self`，类方法是 `cls`。

## 编程建议

- 与 `None` 比较用 `is` / `is not`。
- 类型判断用 `isinstance()`，不用 `type(x) == T`。
- 空序列直接作布尔值：`if not items:`；不写 `== True`。
- 前后缀判断用 `str.startswith()` / `str.endswith()`，不用切片比较。
- 资源用 `with` 管理。
- 同一函数的 `return` 风格保持一致：要么都返回表达式，要么都不返回。
- 不用可变对象作默认参数（官方 tutorial：默认值只求值一次），改用 `None` 并在函数内创建。

## 异常

- 不写裸 `except:`，捕获具体异常类型。
- `try` 块只包住可能抛出该异常的最少代码。
- 自定义异常继承 `Exception`，不继承 `BaseException`。
- 转换异常时用 `raise NewError(...) from err` 保留原因链。

## 文档字符串与类型

- 文档字符串用三个双引号；首行是以句号结尾的摘要；多行时摘要后空一行再写详情（PEP 257）。
- 公开函数写类型注解（PEP 484）。

## 安全相关

- 不对不可信数据使用 `pickle` / `marshal`；YAML 用 `yaml.safe_load`。
- `subprocess` 传参数列表，不用 `shell=True` 拼接用户输入。
- 令牌与密钥用 `secrets` 模块，不用 `random`（PEP 506）。

## 校验

- 项目配置了 Ruff / Flake8 / Black / mypy 时，对改动文件运行对应命令。
- 无配置时，若已安装可运行 `python -m pycodestyle <改动文件>`；未安装就跳过并在交付时说明，不新增依赖。
- `python -m py_compile <改动文件>` 做最低限度的语法检查。
