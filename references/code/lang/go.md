# Go 官方规范要点

官方来源：

- `gofmt`（格式唯一标准，不可协商）
- Effective Go：https://go.dev/doc/effective_go
- Go Code Review Comments：https://go.dev/wiki/CodeReviewComments
- Go Doc Comments：https://go.dev/doc/comment

## 格式

- 所有改动文件必须过 `gofmt`；导入分组用 `goimports`：标准库一组，空行，其余一组。
- 不讨论缩进、对齐、括号位置，`gofmt` 结果即为标准。

## 命名

- 用 `MixedCaps` / `mixedCaps`，不用下划线。
- 缩略词整体同大小写：`userID`、`ServeHTTP`、`parseURL`，不写 `userId`、`ServeHttp`。
- 包名短、全小写、单个词；不用 `util`、`common`、`misc`、`helpers` 这类无意义包名。
- 避免包名与类型名重复：`bufio.Reader`，不写 `bufio.BufReader`。
- getter 不加 `Get` 前缀：`Owner()` / `SetOwner()`。
- 单方法接口以 `-er` 结尾：`Reader`、`Closer`。
- receiver 名短且同一类型保持一致（如 `c`、`srv`），不用 `this`、`self`。

## 错误处理

- 错误作为最后一个返回值；不用 `_` 丢弃错误。
- 错误字符串小写开头、不带结尾标点：`fmt.Errorf("open config: %w", err)`。
- 用 `%w` 包装、`errors.Is` / `errors.As` 判断，不比较错误字符串。
- 先处理错误并返回，正常路径保持最少缩进；`return` 之后不写 `else`。
- 不用 `-1`、`""` 等带内值表示失败，返回额外的 `error` 或 `ok bool`。
- 正常错误流程不用 `panic`。

## 接口与类型

- 接口定义在使用方包，不在实现方包；不在没有使用者之前预先定义接口。
- 实现方返回具体类型。
- 同一类型的方法 receiver 统一用指针或统一用值，不混用。
- 空切片声明用 `var s []string`，不写 `s := []string{}`（需要序列化为 `[]` 时除外）。

## 并发与上下文

- `ctx context.Context` 作为第一个参数，不存进结构体。
- 启动 goroutine 时明确它何时退出，避免泄漏。
- 优先写同步函数，由调用方决定是否并发。

## 注释

- 导出名都要有文档注释，以该名称开头，写完整句子：`// Parse parses ...`。
- 包注释写在 `package` 子句前：`// Package foo ...`。

## 安全相关

- 密钥、token 用 `crypto/rand`，不用 `math/rand`。
- 执行外部命令用 `exec.Command(name, args...)`，不经 `sh -c` 拼接。

## 校验

- `gofmt -l <改动文件>` 输出为空。
- `go vet ./<改动包>/...`。
- 项目有 `.golangci.yml` 时运行 `golangci-lint run`；工具未安装就跳过并在交付时说明。
