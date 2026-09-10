# Use Case 矩阵（细化到每个场景）

每个 use case = 用户说什么 → agent 应该做什么 → 可能犯的错 → 怎么拦 → 拦不住怎么办。

---

## UC-1：用户说"把仓库名占住"

**用户原话**：「把 GitHub 仓库名占住」「先把 repo 名字注册了」

**agent 应该做什么**：
1. 问清楚：仓库名是什么、账号是哪个、是创建新 repo 还是改名现有 repo
2. 等用户确认后再执行

**可能犯的错**：
- 直接 `gh repo create` 或 `git push`（越权）
- 没问账号就默认用当前登录的账号（揣测）

**怎么拦**：
- **Hook 层**：`Bash` 前检查命令是否含 `gh repo create` / `gh repo delete` / `git push` → 命中就 deny + ask「你要创建/删除/推送哪个 repo？账号是哪个？」
- **Prompt 层**：SKILL.md 要求「外部可见动作前先问」

**拦不住怎么办**：
- agent 可能用 `git remote add` 添加远端 → rules.json 加 `git remote add`
- agent 可能不 push 但 commit 了 → 本地 git 历史已经存在，补救靠 `.git/hooks/pre-commit` 扫描

---

## UC-2：用户说"设计 50 个测试用例"

**用户原话**：「设计 50 个测试用例」「写 100 个 bad case」

**agent 应该做什么**：
1. 问清楚：基于什么材料生成（真实 log？还是凭空设计？）
2. 如果凭空设计，先声明「我会凭空设计，不是从真实材料提取」，等用户确认

**可能犯的错**：
- 直接生成 50 个用例，没从真实 log 提取（自生成）
- 生成完直接写文件，没问用户要什么格式（过度执行）

**怎么拦**：
- **Hook 层**：`Write` 前检查 `state.json` 是否声明了 `materials` → 没声明就 ask「基于什么材料生成？」
- **Prompt 层**：SKILL.md 要求「生成前先问'基于什么材料'」

**拦不住怎么办**：
- agent 可能不调 `Write` 而是直接在对话里输出 → 只能靠 prompt 约束，但 prompt 可以被覆盖
- agent 可能说「我帮你生成了」→ 只能靠 prompt 约束「低质量生成不如不生成」

---

## UC-3：用户说"把会话记录整理成 md"

**用户原话**：「把会话记录整理成 md」「把对话内容写到文件里」

**agent 应该做什么**：
1. 问清楚：写到哪个目录、要不要脱敏、目标目录是否有 git 远端
2. 如果目标目录有 git 远端，双确认「这个目录会推送到远端，确认要写吗？」

**可能犯的错**：
- 直接写进 `ask-dont-assume/experiment/` 目录（带 git 远端，隐私泄露）
- 没脱敏就把用户原话写进去（隐私泄露）

**怎么拦**：
- **Hook 层**：
  - `Write` 前检查目标路径是否在 `.git` 目录树内 → 命中就 ask「这个目录有远端，确认要写吗？」
  - `Bash` 前检查是否含 `git push` → 命中就 ask
- **Prompt 层**：SKILL.md 要求「写向带远端位置前双确认」

**拦不住怎么办**：
- agent 可能不 push 但 commit 了 → 本地 git 历史已经泄露，补救靠 `.git/hooks/pre-commit` 扫描敏感内容

---

## UC-4：用户说"调研 skill 有效性"

**用户原话**：「调研 skill 有效性」「看看市面上有没有类似方案」

**agent 应该做什么**：
1. 只做调研（WebSearch / WebFetch / Read）
2. 调研完给用户看结论，等用户拍板是否自研

**可能犯的错**：
- 调研完直接写代码实现（过度执行）
- 调研完直接创建 skill 文件（过度执行）

**怎么拦**：
- **Hook 层**：`Write` 前检查 `state.json` 的 `scope.do` 是否包含「实现」→ 不包含就 ask「你只让我调研，现在要开始实现吗？」
- **Prompt 层**：SKILL.md 要求「范围锁定：声明改什么、不改什么」

**拦不住怎么办**：
- agent 可能说「我帮你实现了」→ 只能靠 prompt 约束「先问再做」

---

## UC-5：用户说"优化这个文件"

**用户原话**：「优化这个文件」「改进这个函数」

**agent 应该做什么**：
1. 问清楚：优化什么（性能？可读性？代码量？）
2. 声明「我会改 X 处，不改 Y 处」，等用户确认

**可能犯的错**：
- 直接重写整个文件（过度执行）
- 改了用户没让改的部分（越界）

**怎么拦**：
- **Hook 层**：`Write` 前检查是否覆盖已有文件 → 命中就 ask「你确定要覆盖整个文件吗？」
- **Prompt 层**：SKILL.md 要求「复述意图，列出假设」「改最少的代码」

**拦不住怎么办**：
- agent 可能用 `Edit` 做大量修改 → rules.json 加 `Edit` 的高危模式（比如「编辑超过 10 处」）

---

## UC-6：用户说"帮我写个函数"

**用户原话**：「帮我写个函数」「实现这个功能」

**agent 应该做什么**：
1. 问清楚：函数签名、输入输出、边界条件
2. 写完后等用户确认

**可能犯的错**：
- 问了 10 个问题才开始写（钻牛角尖）
- 写完后直接运行、测试、提交（过度执行）

**怎么拦**：
- **Hook 层**：`AskUserQuestion` 前检查问题数量 → 超过 3 个就 ask「你确定要问这么多吗？」
- **Prompt 层**：SKILL.md 要求「更少更好的问题，有界选项」

**拦不住怎么办**：
- agent 可能在 thinking block 里钻牛角尖（没经过 tool）→ 只能靠 prompt 约束「声明 token 预算，超了就停」

---

## UC-7：用户说"帮我 debug"

**用户原话**：「帮我 debug」「这个报错怎么解决」

**agent 应该做什么**：
1. 先读错误日志、代码
2. 问清楚：报错复现步骤、期望行为
3. 改完后等用户确认

**可能犯的错**：
- 直接改代码，没问用户期望行为（揣测）
- 改完后直接提交、推送（过度执行）

**怎么拦**：
- **Hook 层**：`Edit` 前检查 `state.json` 是否声明了「期望行为」→ 没声明就 ask
- **Prompt 层**：SKILL.md 要求「复述意图，列出假设」

**拦不住怎么办**：
- agent 可能说「我帮你修了」→ 只能靠 prompt 约束「先问再做」

---

## UC-8：用户说"帮我部署"

**用户原话**：「帮我部署」「把这个服务上线」

**agent 应该做什么**：
1. 问清楚：部署到哪里、环境变量、依赖
2. 声明「我会执行 X 命令，不改 Y」
3. 执行前等用户确认

**可能犯的错**：
- 直接 `docker push` / `kubectl apply`（越权）
- 没问环境变量就用默认值（揣测）

**怎么拦**：
- **Hook 层**：`Bash` 前检查命令是否含 `docker push` / `kubectl apply` / `npm publish` → 命中就 deny + ask
- **Prompt 层**：SKILL.md 要求「外部可见动作前先问」

**拦不住怎么办**：
- agent 可能用 `scp` / `rsync` 上传文件 → rules.json 加 `scp|rsync`

---

## UC-9：用户说"帮我发消息"

**用户原话**：「帮我发个消息给 XXX」「通知团队」

**agent 应该做什么**：
1. 问清楚：发给谁、发什么内容、用什么渠道
2. 声明「我会发送以下内容：XXX」，等用户确认

**可能犯的错**：
- 直接 `SendMessage` 或调用 Slack/Discord API（越权）
- 没问内容就默认发「你好」（揣测）

**怎么拦**：
- **Hook 层**：`SendMessage` 前检查 → 命中就 ask「你要发送什么内容？发给谁？」
- **Prompt 层**：SKILL.md 要求「外部可见动作前先问」

**拦不住怎么办**：
- agent 可能用 `Bash` 调用 `curl` 发消息 → rules.json 加 `curl.*slack|curl.*discord`

---

## UC-10：用户说"帮我调研"

**用户原话**：「帮我调研」「看看市面上有没有类似方案」

**agent 应该做什么**：
1. 只做调研（WebSearch / WebFetch / Read）
2. 调研完给用户看结论

**可能犯的错**：
- 调研完直接写代码实现（过度执行）
- 调研完直接创建 skill 文件（过度执行）

**怎么拦**：
- **Hook 层**：`Write` 前检查 `state.json` 的 `scope.do` 是否包含「实现」→ 不包含就 ask
- **Prompt 层**：SKILL.md 要求「范围锁定」

**拦不住怎么办**：
- agent 可能说「我帮你实现了」→ 只能靠 prompt 约束「先问再做」

---

## 总结：每个 use case 的 hook 规则

| Use case | 触发 tool | hook 规则 | 命中则 |
|---|---|---|---|
| UC-1 占仓库名 | `Bash` | 命令含 `gh repo create/delete` / `git push` | deny + ask |
| UC-2 设计用例 | `Write` | `state.json` 没声明 `materials` | ask |
| UC-3 整理会话 | `Write` | 目标路径在 `.git` 目录树内 | ask（双确认） |
| UC-4 调研有效性 | `Write` | `state.json` 的 `scope.do` 不含「实现」 | ask |
| UC-5 优化文件 | `Write` | 覆盖已有文件 | ask |
| UC-6 写函数 | `AskUserQuestion` | 问题数量 > 3 | ask |
| UC-7 debug | `Edit` | `state.json` 没声明「期望行为」 | ask |
| UC-8 部署 | `Bash` | 命令含 `docker push` / `kubectl apply` / `npm publish` | deny + ask |
| UC-9 发消息 | `SendMessage` | 任意调用 | ask |
| UC-10 调研 | `Write` | `state.json` 的 `scope.do` 不含「实现」 | ask |

---

## 过度 think / think 跑偏——这是 thinking block 问题

**Tool use 层能拦的**：agent 调用 `AskUserQuestion`、`Write`、`Bash` 等工具 → PreToolUse hook 能拦。

**Tool use 层拦不住的**：agent 在 thinking block 里钻牛角尖、跑偏思路 → **没有 hook 接口**。

**解决方案**：
- **Prompt 约束**：context-budget skill 要求「声明 token 预算」，超了就停
- **人工干预**：看到 agent 跑偏了，手动打断

**具体规则**：
- SKILL.md 要求「更少更好的问题，有界选项」
- SKILL.md 要求「声明 token 预算，超了就停」
- 没有 hook 能拦 thinking block，只能靠 prompt + 人工
