# LLM 上下文改造最小计划

本计划记录 fork 后续可参考 SillyTavern 的部分设计，但原则是保持当前游戏的 LLM 推演管线，不改成通用聊天器，也不大幅重排现有代码结构。

## 目标

- 优先提升月末推演、extractor 和大臣召对的上下文命中质量。
- 控制改动面，减少与原版后续 PR 的冲突。
- 复用现有高级 API 区分：主模型负责普通对话和轻量任务，advanced model 负责 simulator/extractor。
- 不新增复杂 UI、不引入向量库、不做完整 Prompt Manager。

## 暂缓事项

- 不做完整 `llm_profiles.py` 参数系统。当前已有 main/advanced API 区分，收益不足以抵消重构成本。
- 不做调试接口。后续若要做，也必须管理员可见，并过滤 API key 与敏感用户数据。
- 不做 SillyTavern 式 Prompt Manager UI。
- 不做 Data Bank / RAG / 向量检索。第一阶段最多考虑只读资料包和关键词注入。
- 不重构 `agents.py`、`decree.py`、`registry.py` 的整体调用链。

## 可做的小改动

### 1. 记忆注入质量微调

参考 SillyTavern World Info 的“命中才注入”思路，但继续使用现有 `event_memories`、`tags`、`expires_turn` 和 SQLite 检索。

候选改动：

- 关键词去噪：过滤过短、泛化、重复关键词。
- 命中去重：同一主体同一回合只保留最高重要度旧事。
- 低重要度限制：低 `importance` 且年代较远的记忆默认不进入月末推演。
- 来源保留：继续区分 `chat_message` 与演算记忆，避免大臣承诺和推演结果混淆。
- token 控制：限制最终注入条数和每条摘要长度。

预期收益：

- 月末推演更能承接前因后果。
- extractor 更容易把旧案、密令、承诺与本月诏书对应起来。
- 减少无关历史挤占上下文。

推荐位置：

- 优先只碰 `ming_sim/decree.py` 中记忆召回附近的局部逻辑。
- 如确实需要复用，再新建小模块 `ming_sim/memory_injection.py`，不要牵动 agent 工厂。

### 2. 大臣召对记忆注入小修

现状召见前会注入上回合旧事。可小幅改成“上回合 + 与当前大臣/派系/事项相关”的混合召回。

候选改动：

- 保留现有 `build_memory_brief()` 入口，避免改调用点。
- 内部使用现有 `get_relevant_event_memories()` 补少量相关记忆。
- 明确最大条数，避免聊天 prompt 膨胀。

预期收益：

- 大臣对历史承诺和派系相关事件更敏感。
- 召对更连续，但不会塞入全局旧事。

### 3. 只读资料包，后置

如果后续发现模型在制度、官职、钱粮、军制方面不稳定，可增加只读资料包。

候选路径：

- `content/rag/fiscal.md`
- `content/rag/military.md`
- `content/rag/personnel.md`
- `content/rag/history_guardrails.md`

第一版只做关键词命中，不做向量库。

## 冲突控制

- 安全层和用户隔离继续放在 `auth.py`、`secret_store.py`、`web_app.py` 的薄接入中。
- LLM 改动单独开分支，例如 `codex/llm-memory-injection-minimal`。
- 每次只动一个小块，避免同时改 UI、安全、LLM 推演。
- 高冲突文件谨慎修改：`web_app.py`、`web/src/main.tsx`、`ming_sim/decree.py`、`ming_sim/agents.py`、`ming_sim/session.py`。
- 合并原版大 PR 前先开临时分支 dry-run rebase，并启用 `git rerere` 记录重复冲突解法。

## 当前优先级

1. 先完成并测试多用户登录、会话、加密 API key、用户数据隔离。
2. 安全层稳定后，再考虑记忆注入质量微调。
3. 资料包和调试接口排到后续，除非具体问题证明它们必要。
