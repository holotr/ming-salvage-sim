import React from "react";
import { Trash2, CheckCircle2, Sparkles, MessageSquare } from "lucide-react";
import {
  listScenarios,
  getScenario,
  createScenario,
  deleteScenario,
  activateScenario,
  deactivateScenario,
} from "../api";
import type { ScenarioFull, ScenarioManifest } from "../types";
import { ScenarioEditor } from "./scenarioEditor";
import { ScenarioChatPanel } from "./scenarioChatPanel";

export function ScenarioManagerModal({
  onClose,
  onChanged,
}: {
  onClose: () => void;
  onChanged: () => void;
}) {
  const [scenarios, setScenarios] = React.useState<ScenarioManifest[]>([]);
  const [activeId, setActiveId] = React.useState("");
  const [busy, setBusy] = React.useState("");
  const [err, setErr] = React.useState("");
  const [editing, setEditing] = React.useState<ScenarioFull | null>(null);
  const [showNew, setShowNew] = React.useState(false);
  const [chatTarget, setChatTarget] = React.useState<{ id: string; name: string } | null>(null);

  const refresh = React.useCallback(async () => {
    const data = await listScenarios();
    setScenarios(data.scenarios);
    setActiveId(data.active_id);
  }, []);

  React.useEffect(() => {
    void refresh().catch((e) => setErr(e?.message || String(e)));
  }, [refresh]);

  const guard = async (label: string, fn: () => Promise<void>) => {
    setBusy(label);
    setErr("");
    try {
      await fn();
    } catch (e: any) {
      setErr(e?.message || String(e));
    } finally {
      setBusy("");
    }
  };

  const onActivate = (id: string) =>
    guard("激活中…", async () => {
      const res = await activateScenario(id);
      setActiveId(res.active_id);
      setScenarios(res.scenarios);
      onChanged();
    });

  const onDeactivate = () =>
    guard("停用中…", async () => {
      const res = await deactivateScenario();
      setActiveId(res.active_id);
      setScenarios(res.scenarios);
      onChanged();
    });

  const onDelete = (id: string, name: string) =>
    guard("删除中…", async () => {
      if (!window.confirm(`删除剧本「${name}」？此操作不可撤销。`)) return;
      const res = await deleteScenario(id);
      setScenarios(res.scenarios);
      setActiveId(res.active_id);
      onChanged();
    });

  const onEdit = (id: string) =>
    guard("打开中…", async () => {
      const full = await getScenario(id);
      setEditing(full);
    });

  if (editing) {
    return (
      <ScenarioEditor
        scenarioId={editing.manifest.id}
        initial={{
          characters: editing.characters,
          events: editing.events,
          seed_events: editing.seed_events,
        }}
        onClose={() => {
          setEditing(null);
          void refresh();
        }}
        onSaved={() => void refresh()}
      />
    );
  }

  if (showNew) {
    return (
      <NewScenarioModal
        scenarios={scenarios}
        onClose={() => setShowNew(false)}
        onCreated={async (id, name) => {
          setShowNew(false);
          await refresh();
          setChatTarget({ id, name });
        }}
      />
    );
  }

  if (chatTarget) {
    return (
      <ScenarioChatPanel
        scenarioId={chatTarget.id}
        scenarioName={chatTarget.name}
        onClose={() => {
          setChatTarget(null);
          void refresh();
        }}
        onChanged={() => {
          void refresh();
          onChanged();
        }}
      />
    );
  }

  return (
    <div className="menu-modal-bg" onClick={onClose}>
      <div className="menu-modal scenario-manager" onClick={(e) => e.stopPropagation()}>
        <h2>自定义剧本</h2>
        <p className="menu-hint">
          剧本 = 人物 / 历史事件 / 随机事件 三套设定。一次只激活一套；激活后下次「开始游戏 / 继续」生效，
          已有存档人物只补缺、事件直接生效。
        </p>
        {err && <div className="menu-error">{err}</div>}

        <div className="scenario-toolbar">
          <button onClick={() => setShowNew(true)} disabled={!!busy}><Sparkles size={14} /> 新建剧本（AI 对话编辑）</button>
          <button onClick={onDeactivate} disabled={!!busy || !activeId}>停用当前剧本</button>
        </div>

        <div className="scenario-active-line">
          当前剧本：<b>{activeId ? (scenarios.find((s) => s.id === activeId)?.name ?? activeId) : "默认（崇祯元年）"}</b>
        </div>

        {scenarios.length === 0 ? (
          <p className="menu-empty">暂无剧本。点「新建剧本（AI 对话编辑）」开始。</p>
        ) : (
          <div className="scenario-list">
            {scenarios.map((s) => (
              <div key={s.id} className={`scenario-item ${s.id === activeId ? "active" : ""}`}>
                <div className="scenario-item-main">
                  <div className="scenario-item-name">
                    {s.name}
                    {s.id === activeId && <span className="scenario-badge"><CheckCircle2 size={12} /> 已激活</span>}
                    {s.source === "generated" && <span className="scenario-tag">AI</span>}
                  </div>
                  {s.description && <div className="scenario-item-desc">{s.description}</div>}
                  <div className="scenario-item-files">
                    {s.files.characters ? "人物 ✓" : "人物 —"} · {s.files.events ? "事项 ✓" : "事项 —"} · {s.files.seed_events ? "候选 ✓" : "候选 —"}
                  </div>
                </div>
                <div className="scenario-item-actions">
                  <button onClick={() => setChatTarget({ id: s.id, name: s.name })} disabled={!!busy}>
                    <MessageSquare size={14} /> AI 对话
                  </button>
                  <button onClick={() => onEdit(s.id)} disabled={!!busy}>表格</button>
                  {s.id === activeId ? (
                    <button onClick={onDeactivate} disabled={!!busy}>停用</button>
                  ) : (
                    <button className="primary" onClick={() => onActivate(s.id)} disabled={!!busy}>激活</button>
                  )}
                  <button className="scenario-del" title="删除" onClick={() => onDelete(s.id, s.name)} disabled={!!busy}>
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {busy && <div className="menu-busy">{busy}</div>}
        <div className="menu-modal-actions">
          <button onClick={onClose}>关闭</button>
        </div>
      </div>
    </div>
  );
}

function NewScenarioModal({
  scenarios,
  onClose,
  onCreated,
}: {
  scenarios: ScenarioManifest[];
  onClose: () => void;
  onCreated: (id: string, name: string) => Promise<void>;
}) {
  const [name, setName] = React.useState("");
  const [desc, setDesc] = React.useState("");
  const [copyFrom, setCopyFrom] = React.useState(""); // ""=空白
  const [busy, setBusy] = React.useState(false);
  const [err, setErr] = React.useState("");
  const onSave = async () => {
    setBusy(true);
    setErr("");
    try {
      const res = await createScenario(name.trim(), desc.trim(), copyFrom);
      await onCreated(res.manifest.id, name.trim());
    } catch (e: any) {
      setErr(e?.message || String(e));
      setBusy(false);
    }
  };
  return (
    <div className="menu-modal-bg" onClick={onClose}>
      <div className="menu-modal" onClick={(e) => e.stopPropagation()}>
        <h2>新建剧本</h2>
        <p className="menu-hint">建好后进入 AI 对话编辑，让助手按你的描述增删改人物与事件。</p>
        {err && <div className="menu-error">{err}</div>}
        <label>剧本名<input value={name} onChange={(e) => setName(e.target.value)} placeholder="如：宁远之战" /></label>
        <label>说明<input value={desc} onChange={(e) => setDesc(e.target.value)} placeholder="一句话简介" /></label>
        <label>
          起始内容
          <select value={copyFrom} onChange={(e) => setCopyFrom(e.target.value)}>
            <option value="">空白（助手从你的构思从零搭建）</option>
            <option value="__default__">复制默认（崇祯元年官方设定）</option>
            {scenarios.map((s) => (
              <option key={s.id} value={s.id}>复制自：{s.name}</option>
            ))}
          </select>
        </label>
        <div className="menu-modal-actions">
          <button onClick={onClose} disabled={busy}>取消</button>
          <button className="primary" onClick={onSave} disabled={busy || !name.trim()}>
            {busy ? "创建中…" : "创建并对话"}
          </button>
        </div>
      </div>
    </div>
  );
}
