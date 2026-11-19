# Node.js 官方规范要点

官方来源：

- Node.js 官方 API 文档：https://nodejs.org/api/
- Node.js 官方 Learn 指南，尤其是：
  - Don't Block the Event Loop：https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop
  - Security Best Practices：https://nodejs.org/en/learn/getting-started/security-best-practices

说明：Node.js 官方没有面向应用代码的排版规范（Node.js 核心仓库的 ESLint 配置只约束核心自身）。排版遵循项目的 ESLint / Prettier 配置；没有配置时与所在文件保持一致。以下是官方文档明确给出的写法与实践。

## 运行时与模块

- 版本以 `package.json` 的 `engines.node` 或 `.nvmrc` 为准，不使用该版本不支持的 API。
- 模块系统以 `package.json` 的 `"type"` 为准：`"module"` 用 ESM `import`，否则用 CommonJS；不在同一包里混用两种写法（`.mjs` / `.cjs` 显式指定的文件除外）。
- 内置模块用 `node:` 前缀导入：`import { readFile } from 'node:fs/promises'`。
- 优先使用内置能力，不为此新增依赖：全局 `fetch`（18+）、`node:test`、`node:assert/strict`、`AbortSignal.timeout()`、`structuredClone`、`--env-file`（20.6+）。

## 异步

- 用 Promise 版 API 配合 `async` / `await`：`node:fs/promises`、`node:timers/promises`、`node:stream/promises`。
- 同一调用链不混用回调与 Promise。
- 每个 Promise 都要被 `await` 或显式处理；未处理的 rejection 默认会终止进程（15+）。
- 流的串联用 `pipeline()`，不用 `.pipe()`，以便正确传播错误并释放资源。
- 超时与取消用 `AbortController` / `AbortSignal` 传给支持 `signal` 的 API。

## 不阻塞事件循环

- 请求处理路径不用同步 I/O（`readFileSync`、`execSync` 等）；同步 API 只用于启动阶段或 CLI 脚本。
- CPU 密集任务放 `node:worker_threads`，不在主线程上长时间计算。
- 处理不可信输入时，避免可能灾难性回溯的正则（ReDoS），并限制输入长度。
- `JSON.parse` / `JSON.stringify` 处理大体积不可信数据前先限制大小。

## 错误

- 只抛 `Error` 或其子类，不抛字符串或普通对象。
- 需要被程序判断的错误设置稳定的 `code` 属性，调用方按 `err.code` 判断，不匹配 `message`。
- 包装错误时用 `new Error('...', { cause: err })` 保留原因。
- `EventEmitter` 必须监听 `'error'` 事件，否则错误会直接抛出终止进程。

## 安全（官方 Security Best Practices）

- 执行外部命令用 `execFile` / `spawn` 并传参数数组，不用 `exec` 拼接用户输入。
- 不对不可信输入使用 `eval`、`new Function`、`vm`（`vm` 不是安全沙箱）。
- 防原型污染：不把不可信对象深合并进普通对象；动态键用 `Map` 或 `Object.create(null)`。
- 依赖用锁文件固定，CI 安装用 `npm ci`。
- 机密从 `process.env` 读取。

## 通用 JavaScript 写法

- 默认 `const`，需要重新赋值才用 `let`，不用 `var`。
- 比较用 `===` / `!==`。
- 变量与函数 `camelCase`，类 `PascalCase`，模块级常量 `UPPER_SNAKE_CASE`（与 Node.js API 文档示例一致）。
- TypeScript 文件额外遵循项目 `tsconfig.json`，不放宽 `strict` 等现有选项。

## 校验

- `node --check <改动文件>` 做语法检查（仅 JS）。
- 项目配置了 ESLint / Prettier / `tsc` 时对改动文件运行；测试用项目已有命令或 `node --test`。
- 工具不可用就跳过并在交付时说明，不新增依赖。
