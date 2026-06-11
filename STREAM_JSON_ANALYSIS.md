# 流式 JSON 解析可靠性审查报告

## 1. 流式接口与 force_json_output 配置审查

### 1.1 已配置 force_json_output=True 的接口（✓ 正确）

| Agent | 调用位置 | force_json | stream | 状态 |
|-------|---------|-----------|--------|------|
| score_extractor_module | simulation.py:1258 | ✓ | ✓ | 正确 |
| json_sanitizer | simulation.py:1266, agents.py:749 | ✓ | ✓ | 正确 |
| chapter_memory | memories.py:243 | ✓ | ✓ | 正确 |
| minister_recap | memories.py:305 | ✓ | ✓ | 正确 |
| scenario_generator | agents.py:743 | ✓ | ✓ | 正确 |

### 1.2 未配置 force_json_output 的流式接口（⚠️ 风险）

| Agent | 调用位置 | force_json | stream | 问题 |
|-------|---------|-----------|--------|------|
| season_simulator | simulation.py:542 | ✗ | ✓ | 输出包含 <<DECISION>> 块，非纯 JSON |
| decree_writer | decree.py:190 | ✗ | ✓ | 输出纯文本诏书，非 JSON |
| ending_summary | decree.py:635 | ✗ | ✓ | 输出纯文本史评，非 JSON |
| issue_log_compact | issues.py:614 | ✓ | ✓ | **缺少配置！** |

**关键发现**：`issue_log_compact` agent 未配置 `force_json_output=True`，但需要 JSON 输出。

---

## 2. parse_agent_json 四重容错机制分析

```python
def parse_agent_json(raw: str, stage: str) -> Dict[str, Any]:
    # 试 1：原文直解
    # 试 2：截取 {...} 最外层再解
    # 试 3：净化 control char 后再解
    # 试 4：截取首个平衡 {...} 子串（防 LLM 重发拼接）
```

### 2.1 容错能力评估

| 场景 | 容错级别 | 能否处理 | 备注 |
|------|---------|---------|------|
| 前后有思考/解释文字 | Level 2 | ✓ | 截取 {...} |
| Markdown fence（```json）| Level 0 | ✓ | strip_json_fence 预处理 |
| 控制字符混入 | Level 3 | ✓ | 正则清洗 |
| LLM 重发导致 `{...}{...}` | Level 4 | ✓ | 括号平衡匹配 |
| 尾随逗号 | - | ✗ | json.loads 无法容忍 |
| 注释（//、/* */）| - | ✗ | json.loads 无法容忍 |
| 字符串内未转义引号 | - | ✗ | 破坏 JSON 结构 |
| 截断的不完整 JSON | - | ✗ | 括号不平衡 |
| 空响应 | - | ✗ | abort_llm_contract |

### 2.2 流式特有风险

**流式拼接可能产生的畸形 JSON**：

1. **编码问题**：多字节 UTF-8 字符在 chunk 边界被切断
   - run_agent_stream_text:273 `"".join(pieces)` 可能拼出乱码
   
2. **重发累加**：某些 LLM 流式重发同一段（dashscope 已知问题）
   - Level 4 容错能匹配首个 {...}，但若 `{"a":1}{"a":2}` 会丢失后半
   
3. **思考/正文交织**：reasoning_content 和 content 可能插入顺序错乱
   - 当前逻辑：reasoning_buf 独立，pieces 只收 content → 理论安全
   
4. **流中断**：网络抖动导致 JSON 输出中途截断
   - Level 4 会因括号不匹配抛 LLMContractError

---

## 3. sanitizer 死循环风险分析

### 3.1 当前调用链

```
extractor (stream) 失败
  → sanitizer (stream) 重整
    → parse_agent_json
      → 失败 → 抛异常（无循环）
```

### 3.2 死循环判定

**结论：不存在死循环**

理由：
1. sanitizer 被调用时已在 `except Exception as parse_err` 块内
2. sanitizer 输出再经 parse_agent_json 失败时，会**直接抛异常**
3. 无代码路径会在 sanitizer 失败后再次调用 sanitizer
4. simulation.py:1256-1275 有 3 次重试，但每次重试都是**重新跑 extractor**，不是重跑 sanitizer

### 3.3 但存在资源浪费风险

场景：sanitizer 自身也是流式 + force_json_output，若它输出畸形 JSON：
- 已消耗 1 次 extractor 调用（失败）
- 已消耗 1 次 sanitizer 调用（失败）
- 当前重试会再跑 1 次 extractor（可能再触发 sanitizer）
- 最坏情况：3 次 extractor × 2 次调用（本体+sanitizer）= 6 次 LLM 调用

---

## 4. 所有 JSON 解析失败场景清单

### 4.1 流式拼接层面（run_agent_stream_text）

| 场景 | 原因 | 概率 | 能否检测 |
|------|------|------|---------|
| UTF-8 多字节字符截断 | chunk 边界切分 | 低 | ✗ 拼接后乱码 |
| LLM 流式重发段落 | 模型 bug | 中 | ✓ Level 4 取首块 |
| 思考/正文混杂 | 事件顺序错乱 | 极低 | ✓ 独立 buffer |
| 网络中断截断 | httpx timeout | 中 | ✓ 转 LLMUnavailable |
| 空响应 | 模型异常/限流 | 低 | ✓ abort_llm_contract |

### 4.2 JSON 格式层面（parse_agent_json）

| 场景 | force_json 能防 | parse 容错 | 最终状态 |
|------|----------------|-----------|---------|
| 前后有解释文字 | ✓ | ✓ Level 2 | 成功 |
| Markdown fence | 部分 | ✓ strip_fence | 成功 |
| 控制字符混入 | ✗ | ✓ Level 3 | 成功 |
| 尾随逗号 | ✓ | ✗ | 失败 → sanitizer |
| JSON 注释 | ✓ | ✗ | 失败 → sanitizer |
| 字段重复（重发导致）| ✗ | ✓ Level 4 | 成功（取首块）|
| 字符串内引号未转义 | ✓ | ✗ | 失败 → sanitizer |
| 括号不匹配 | ✓ | ✗ | 失败 → sanitizer |
| 顶层是数组非对象 | ✗ | ✗ | 失败（abort）|

### 4.3 sanitizer 失效场景

| 场景 | 原因 | 后果 |
|------|------|------|
| sanitizer 自身输出畸形 JSON | 模型能力不足 | 重试（最多 3 次）|
| sanitizer 改变数据结构 | 过度修复（把 object 改成 array）| 结算字段缺失 |
| sanitizer 丢失字段 | 输入过长截断 | 结算使用默认值 |
| sanitizer 输出空响应 | 模型限流/异常 | LLMContractError |

### 4.4 模型兼容性问题

| 模型 | force_json 支持 | 已知问题 |
|------|----------------|---------|
| dashscope/qwen | ✓ extra_body | 流式偶发重发 |
| deepseek | ✓ response_format | 前缀缓存命中时首 token 慢 |
| minimax | ✓ response_format | thinking 过长 |
| openai o1/o3 | 部分（reasoning_effort）| 不支持 response_format + reasoning |

---

## 5. 关键代码片段审查

### 5.1 run_agent_stream_text 拼接逻辑（agents.py:246-273）

```python
# 风险点 1：pieces 直接 append delta，未做编码检查
pieces.append(delta)  # 若 delta 是截断的多字节字符？

# 风险点 2：拼接后未验证 JSON 完整性
streamed = "".join(pieces).strip()
```

**问题**：若最后一个 delta 是不完整 UTF-8，join 可能产生 � 替换字符。

**实测**：httpx/openai SDK 的流式解码已处理 UTF-8 边界，delta 保证是完整字符。
**结论**：理论风险，实际未遇到。

### 5.2 parse_agent_json Level 4 容错（agents.py:318-355）

```python
# 截取首个平衡 {...} 子串
if best_end > 0:
    first_block = snippet[: best_end + 1]
    # 风险：若首块是 {"a":1}，后续 {"a":2} 被丢弃
```

**问题**：重发时可能丢失**更新后的字段值**。

**缓解**：force_json_output 减少重发；extractor 有 3 次重试。

### 5.3 sanitizer 配置（agents.py:610-627）

```python
# 正确：force_json_output=True, enable_thinking=False
model=create_chat_model(
    llm_config,
    temperature=0.0,  # 确定性输出
    force_json_output=True,  # ✓
)
```

**审查结果**：配置正确，temperature=0 降低随机性。

---

## 6. 遗漏配置发现

### 6.1 issue_log_compact agent（issues.py:589-607）

```python
# ⚠️ 问题：缺少 force_json_output=True
Agent(
    name="事项日志压缩员",
    model=create_chat_model(
        llm_config,
        temperature=0.0,
        top_p=0.7,
        max_tokens=max(800, llm_config.max_tokens),
        enable_thinking=False,
        # force_json_output=True,  # 缺失！
    ),
    instructions=["...只输出合法 JSON：{\"log\":\"...\"}..."],
)
```

**影响**：
- 该 agent 输出要求 `{"log":"..."}` JSON
- 未配置 force_json 时，模型可能输出 Markdown fence 或解释文字
- issues.py:619 有 parse_agent_json 调用，会触发容错
- 但若模型输出 `压缩结果如下：{"log":"..."}` 则 Level 2 容错可救

**风险等级**：中等（有容错但不稳定）

---

## 7. 修复建议

### 7.1 立即修复

1. **issues.py:596** - 添加 `force_json_output=True`

```python
model=create_chat_model(
    llm_config,
    temperature=0.0,
    top_p=0.7,
    max_tokens=max(800, llm_config.max_tokens),
    enable_thinking=False,
    force_json_output=True,  # 新增
)
```

### 7.2 增强容错

2. **agents.py:273** - 拼接后验证 JSON 起止字符

```python
streamed = "".join(pieces).strip()
if streamed and not (streamed.startswith("{") or streamed.startswith("[")):
    tlog(f"[{tag}] 警告：流式输出不以 {{ 或 [ 开头，可能截断")
```

3. **agents.py:345** - Level 4 容错记录丢弃内容

```python
if best_end > 0 and best_end < len(snippet) - 10:
    discarded = snippet[best_end + 1:][:100]
    tlog(f"[{stage}] JSON 截取丢弃尾部：{discarded}")
```

### 7.3 监控告警

4. 统计 sanitizer 调用频率，若 > 5% 则告警模型配置问题
5. 记录 parse_agent_json 触发的容错级别分布

---

## 8. 总结

### 8.1 核心发现

1. **5/6 个流式 JSON agent 已正确配置 force_json_output**
2. **issue_log_compact 缺少 force_json_output 配置**（唯一遗漏）
3. **parse_agent_json 四重容错基本足够**，覆盖常见畸形场景
4. **不存在 sanitizer 死循环**，但最坏消耗 6 次 LLM 调用
5. **流式拼接逻辑本身无重大缺陷**（UTF-8 边界由 SDK 处理）

### 8.2 剩余风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| LLM 重发导致字段覆盖 | 低 | 中 | Level 4 取首块 + 重试 |
| sanitizer 自身失败 | 低 | 高 | 3 次重试 + 降级逻辑 |
| 网络中断 JSON 截断 | 中 | 高 | 转 LLMUnavailable 提示用户 |
| issue_log_compact 输出非 JSON | 中 | 低 | 容错 Level 2 可救 + 兜底截断 |

### 8.3 修复优先级

1. **P0**: 修复 issue_log_compact force_json 缺失（1 行代码）
2. **P1**: 增加流式输出起止字符验证（防御性日志）
3. **P2**: 监控 sanitizer 调用率（运营指标）
