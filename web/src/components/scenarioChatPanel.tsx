import React from "react";
import { Loader2, Send, Table2, CheckCircle2 } from "lucide-react";
import { streamScenarioChat, getScenario, activateScenario } from "../api";
import type { ScenarioFull, ScenarioChatResult } from "../types";
import { ScenarioEditor } from "./scenarioEditor";

type Msg = { role: "user" | "assistant"; content: string; changes?: { tool: string; result: string }[] };

const TOOL_CN: Record<string, string> = {
  upsert_character: "改人物",
  delete_character: "删人物",
  upsert_faction: "改派系",
  delete_faction: "删派系",
  upsert_event: "改事件",
  delete_event: "删事件",
};

export function ScenarioChatPanel({
  scenarioId,
  scenarioName,
  onClose,
  onChanged,
}: {
  scenarioId: string;
  scenarioName: string;
  onClose: () => void;
  onChanged: () => void;
}) {
  const [messages, setMessages] = React.useState<Msg[]>([]);
  const [input, setInput] = React.useState("");
  const [streaming, setStreaming] = React.useState("");
  const [busy, setBusy] = React.useState(false);
  const [err, setErr] = React.useState("");
  const [scenario, setScenario] = React.useState<ScenarioFull | null>(null);
  const [showEditor, setShowEditor] = React.useState(false);
  const [editorFocus, setEditorFocus] = React.useState<{ tab: "characters" | "events" | "seed_events"; key?: string } | null>(null);
  const transcriptRef = React.useRef<HTMLDivElement>(null);

  const openEditor = (tab: "characters" | "events" | "seed_events", key?: string) => {
    setEditorFocus({ tab, key });
    setShowEditor(true);
  };

  const loadScenario = React.useCallback(async () => {
    try {
      setScenario(await getScenario(scenarioId));
    } catch (e: any) {
      setErr(e?.message || String(e));
    }
  }, [scenarioId]);

  React.useEffect(() => {
    void loadScenario();
  }, [loadScenario]);

  React.useEffect(() => {
    transcriptRef.current?.scrollTo({ top: transcriptRef.current.scrollHeight });
  }, [messages, streaming]);

  const send = async () => {
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    setErr("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setBusy(true);
    setStreaming("");
    try {
      let acc = "";
      const result: ScenarioChatResult = await streamScenarioChat(scenarioId, text, (d) => {
        acc += d;
        setStreaming(acc);
      });
      setMessages((m) => [...m, { role: "assistant", content: result.reply, changes: result.changes }]);
      setStreaming("");
      setScenario(result.scenario);
      if (result.validation) setErr(`⚠ 暂未通过加载校验：${result.validation}`);
      onChanged();
    } catch (e: any) {
      setErr(e?.message || String(e));
      setStreaming("");
    } finally {
      setBusy(false);
    }
  };

  const onActivate = async () => {
    setBusy(true);
    setErr("");
    try {
      await activateScenario(scenarioId);
      onChanged();
      setErr("");
      setMessages((m) => [...m, { role: "assistant", content: "✓ 已激活此剧本，下次「开始游戏 / 继续」生效。" }]);
    } catch (e: any) {
      setErr(e?.message || String(e));
    } finally {
      setBusy(false);
    }
  };

  if (showEditor && scenario) {
    return (
      <ScenarioEditor
        scenarioId={scenarioId}
        initial={{ characters: scenario.characters, events: scenario.events, seed_events: scenario.seed_events }}
        initialTab={editorFocus?.tab}
        focusKey={editorFocus?.key}
        onClose={() => {
          setShowEditor(false);
          setEditorFocus(null);
          void loadScenario();
        }}
        onSaved={() => void loadScenario()}
      />
    );
  }

  const chars = scenario?.characters;
  const factions = chars?.factions ?? [];
  const characters = chars?.characters ?? [];
  const events = scenario?.events ?? [];
  const seeds = scenario?.seed_events ?? [];

  return (
    <div className="menu-modal-bg" onClick={busy ? undefined : onClose}>
      <div className="menu-modal scenario-chat" onClick={(e) => e.stopPropagation()}>
        <div className="scenario-chat-head">
          <h2>AI 对话编辑 · {scenarioName}</h2>
          <div className="scenario-chat-head-actions">
            <button onClick={() => openEditor("characters")} disabled={!scenario}><Table2 size={14} /> 表格编辑</button>
            <button className="primary" onClick={onActivate} disabled={busy}><CheckCircle2 size={14} /> 激活此剧本</button>
          </div>
        </div>
        {err && <div className="menu-error">{err}</div>}

        <div className="scenario-chat-body">
          {/* 左：对话 */}
          <div className="scenario-chat-left">
            <div className="scenario-chat-transcript" ref={transcriptRef}>
              {messages.length === 0 && !streaming && (
                <div className="scenario-chat-hint">
                  告诉我你想怎么改这套剧本。例如：「加一个辽东派系，再加袁崇焕、满桂、祖大寿三名辽东武将」，
                  或「把崇祯元年的财政危机随机事件门槛调低一点」。
                </div>
              )}
              {messages.map((m, i) => (
                <div key={i} className={`scenario-bubble ${m.role}`}>
                  <div className="scenario-bubble-content">{m.content}</div>
                  {m.changes && m.changes.length > 0 && (
                    <div className="scenario-bubble-changes">
                      {m.changes.map((ch, j) => (
                        <div key={j} className="scenario-change-row">
                          <span className="scenario-change-tool">{TOOL_CN[ch.tool] || ch.tool}</span>
                          <span>{ch.result}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {streaming && (
                <div className="scenario-bubble assistant">
                  <div className="scenario-bubble-content">{streaming}<span className="scenario-cursor">▋</span></div>
                </div>
              )}
            </div>
            <div className="scenario-chat-input">
              <textarea
                rows={2}
                value={input}
                placeholder="描述你想要的改动…（Enter 发送，Shift+Enter 换行）"
                disabled={busy}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    void send();
                  }
                }}
              />
              <button className="primary" onClick={send} disabled={busy || !input.trim()}>
                {busy ? <Loader2 size={16} className="spin" /> : <Send size={16} />}
              </button>
            </div>
          </div>

          {/* 右：实时预览 */}
          <div className="scenario-chat-preview">
            <div className="scenario-preview-counts">
              派系 {factions.length} · 人物 {characters.length} · 历史事件 {events.length} · 随机事件 {seeds.length}
            </div>
            <PreviewSection title={`派系（${factions.length}）`}>
              {factions.map((f, i) => (
                <button key={i} className="scenario-preview-item" onClick={() => openEditor("characters", f.name)}>{f.name}</button>
              ))}
            </PreviewSection>
            <PreviewSection title={`人物（${characters.length}）`}>
              {characters.map((c, i) => (
                <button key={i} className="scenario-preview-item" onClick={() => openEditor("characters", c.name)}>
                  {c.name} <span className="dim">· {c.faction} · {c.office}</span>
                </button>
              ))}
            </PreviewSection>
            <PreviewSection title={`历史事件（${events.length}）`}>
              {events.map((e, i) => (
                <button key={i} className="scenario-preview-item" onClick={() => openEditor("events", e.id)}>
                  {e.title} <span className="dim">· {e.id}</span>
                </button>
              ))}
            </PreviewSection>
            <PreviewSection title={`随机事件（${seeds.length}）`}>
              {seeds.map((e, i) => (
                <button key={i} className="scenario-preview-item" onClick={() => openEditor("seed_events", e.id)}>
                  {e.title} <span className="dim">· {e.id}</span>
                </button>
              ))}
            </PreviewSection>
          </div>
        </div>

        <div className="menu-modal-actions">
          <button onClick={onClose} disabled={busy}>关闭</button>
        </div>
      </div>
    </div>
  );
}

function PreviewSection({ title, children }: { title: string; children: React.ReactNode }) {
  const [open, setOpen] = React.useState(true);
  const items = React.Children.toArray(children);
  return (
    <div className="scenario-preview-section">
      <button className="scenario-preview-toggle" onClick={() => setOpen((o) => !o)}>
        {open ? "▾" : "▸"} {title}
      </button>
      {open && (items.length ? <div className="scenario-preview-list">{items}</div> : <div className="scenario-preview-empty">（无）</div>)}
    </div>
  );
}
