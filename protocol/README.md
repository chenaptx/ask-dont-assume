# Ask, Don't Assume — 意图克制协议（v3）

让 agent：少揣测意图、少越界执行、少自作主张、保护你的隐私。口号 "Don't decide for me"。

协议分**两层**——靠 prompt 的语义层 + 靠脚本的硬门层。这篇 README 只讲一件事：**哪些拆成了脚本、你作为使用者怎么 hook、效果到什么程度。**

## 依赖地图（先看这张图）

| 文件 | 是什么层 | 干什么 | 能不能拆成脚本 |
|---|---|---|---|
| `SKILL.md` | 协议层（prompt） | 判断"要不要问""基于什么材料"——需要理解语义 | ❌ 拆不了，只能 prompt |
| `check.py` | 硬门层（脚本） | 每次工具调用前跑：隐私/范围/高危/授权判定 | ✅ 脚本 |
| `rules.json` | 硬门层（配置） | 正则白名单/黑名单、高危命令清单——你改这里不用改代码 | ✅ 纯配置 |
| `state.json` | 数据通路 | 协议层写"这次的范围/材料/授权"，硬门派读它做比对 | ✅ JSON |
| `adapters/*/settings.json` | 接线 | 把 check.py 挂到平台 hook | ✅ 配置 |

## 哪些东西被拆成了脚本

skill **不是**一个文件。所有"一见就能判"的都抽成了 `check.py` + `rules.json`（判定顺序 R1→R6）：

```
R1 授权：动作命中白名单 → 放行（显式授权不打扰）
R2 隐私：内容/路径命中隐私正则 → 拒绝（最高优先）
R3 事实：生成类动作但 state.json 没声明材料来源 → 问
R4 范围：动作超出 state.json 声明的 scope → 问
R5 高危：删除/强制推送/部署等 → 需确认
R6 成本：预估消耗超预算 → 先报数字
```

留给 SKILL.md（prompt）的只有**语义判断**：复述意图、确认基于什么材料、选问题选项——这些没有确定性答案，只能靠模型。

## 你作为使用者，怎么 hook（核心）

`check.py` 自己是脚本，但**它不会自己跑**——要把它挂到平台的"工具调用前"事件才生效。三档做法：

**① Claude Code（能做硬门）**
在 `~/.claude/settings.json` 里注册 PreToolUse，把 `adapters/claude-code/settings.json` 的内容拷进去，改成本机绝对路径。之后每次 Write/Edit/Delete/Bash/WebFetch 前自动调用 check.py，按 R1–R6 返回 allow/deny/ask。
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|Delete|Bash|WebFetch|WebSearch",
        "hooks": [{
          "type": "command",
          "command": "python3 /绝对路径/check.py --tool \"$TOOL_NAME\" --input \"$INPUT_JSON\" --state /绝对路径/state.json"
        }]
      }
    ]
  }
}
```

**② 你自己的 harness（Hermes / DSH / ZCode）**
最可控：在工具路由里直接调 `check.py --tool ... --input ...`，把返回的 deny/ask 接到拦截逻辑，想插在哪插在哪。

**③ 无 hook 的平台（TRAE 等）**
脚本挂不上 → 只剩 SKILL.md 的协议层（靠自觉）。这就是为什么 TRAE 被排除：不是 skill 不行，是平台不给 hook 入口。

## 效果边界（诚实版）

| 能拦住 | 拦不住 |
|---|---|
| 路径级、命令级、可达内容的确定性风险（隐私正则、只读路径、force 推送、删除） | 语义级判断（意图揣测、置信度）——只能靠协议层 prompt |
| 只要平台给了 hook | 无 hook 平台上的任何硬拦 |

## 一次工具调用的完整链路

```
你发出指令
  → SKILL.md（prompt层）: 复述意图、核对材料、写 state.json
  → 平台触发 PreToolUse hook
  → check.py 读 state.json + 本次工具参数 → 私密/范围/高危判定
  → allow 放行 / deny 拒绝 / ask 转达你要确认
```

## 验证

`experiment/` 冒烟测试记录：同批 bad case（GitHub 越权 / 自生成任务 / 隐私写入带远端 repo）对照各版本首轮响应。`benchmark-spec.md` 是评测打分规格——**它不属于 skill 本体**，只是研发时测拦截效果的验收工具。

## 许可

MIT。