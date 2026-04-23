#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三省六部 · 军机处看板生成器
生成一个单文件 HTML 看板（零外部依赖，内嵌 CSS/JS）
"""

import json
from datetime import datetime
from pathlib import Path
from state_manager import StateManager, _DEPT_NAMES

# 状态 → 中文名 & 颜色
_STATUS_META = {
    "draft":           {"label": "草稿",        "color": "#94a3b8", "bg": "#f1f5f9"},
    "taizi_sorted":    {"label": "太子分拣",    "color": "#8b5cf6", "bg": "#ede9fe"},
    "zhongshu_planned":{"label": "中书规划",    "color": "#3b82f6", "bg": "#dbeafe"},
    "menxia_reviewing":{"label": "门下审议",    "color": "#f59e0b", "bg": "#fef3c7"},
    "menxia_rejected": {"label": "门下封驳",    "color": "#ef4444", "bg": "#fee2e2"},
    "menxia_approved": {"label": "门下准奏",    "color": "#10b981", "bg": "#d1fae5"},
    "shangshu_dispatching": {"label": "尚书派发", "color": "#6366f1", "bg": "#e0e7ff"},
    "executing":       {"label": "六部执行",    "color": "#0ea5e9", "bg": "#e0f2fe"},
    "reviewing":       {"label": "待审查",      "color": "#f97316", "bg": "#ffedd5"},
    "completed":       {"label": "已完成",      "color": "#22c55e", "bg": "#dcfce7"},
    "cancelled":       {"label": "已取消",      "color": "#64748b", "bg": "#e2e8f0"},
    "blocked":         {"label": "已阻塞",      "color": "#dc2626", "bg": "#fecaca"},
    "stopped":         {"label": "已叫停",      "color": "#78716c", "bg": "#f5f5f4"},
}

# Kanban 列定义（按流程顺序）
_KANBAN_COLUMNS = [
    ["draft", "taizi_sorted"],
    ["zhongshu_planned"],
    ["menxia_reviewing", "menxia_rejected", "menxia_approved"],
    ["shangshu_dispatching", "executing", "reviewing"],
    ["completed"],
    ["cancelled", "blocked", "stopped"],
]

_COL_HEADERS = ["待分拣/待规划", "中书规划", "门下审议", "执行中", "已完成", "异常"]


class KanbanGenerator:
    def __init__(self, state_manager: StateManager = None, output_path: str = None):
        self.sm = state_manager or StateManager()
        if output_path is None:
            base = Path(__file__).resolve().parent.parent
            output_path = base / "dashboard" / "kanban.html"
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self) -> str:
        edicts = self.sm.list_edicts(limit=200)
        stats = self.sm.get_stats()

        # 按状态分组
        by_status: dict = {}
        for e in edicts:
            s = e["status"]
            by_status.setdefault(s, []).append(e)

        # 构建看板卡片 HTML
        columns_html = ""
        for col_idx, statuses in enumerate(_KANBAN_COLUMNS):
            cards = []
            for s in statuses:
                for e in by_status.get(s, []):
                    cards.append(self._card_html(e))

            meta = _STATUS_META.get(statuses[0], {"label": statuses[0], "color": "#333", "bg": "#fff"})
            count = sum(len(by_status.get(s, [])) for s in statuses)
            header = _COL_HEADERS[col_idx]

            columns_html += f'''
            <div class="kanban-col">
              <div class="col-header" style="border-color:{meta['color']}">
                <span class="col-title">{header}</span>
                <span class="col-count" style="background:{meta['bg']};color:{meta['color']}">{count}</span>
              </div>
              <div class="col-cards">
                {''.join(cards)}
              </div>
            </div>
            '''

        # 统计面板
        dept_bars = ""
        for dept, count in sorted(stats.get("by_dept", {}).items(), key=lambda x: -x[1]):
            name = _DEPT_NAMES.get(dept, dept)
            width = min(100, count * 5)
            dept_bars += f'''
            <div class="dept-bar">
              <span class="dept-name">{name}</span>
              <div class="bar-track"><div class="bar-fill" style="width:{width}%"></div></div>
              <span class="dept-count">{count}</span>
            </div>
            '''

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>军机处 · 三省六部看板</title>
<style>
:root {{
  --bg: #f8fafc;
  --card-bg: #ffffff;
  --border: #e2e8f0;
  --text: #1e293b;
  --text-secondary: #64748b;
  --radius: 12px;
  --shadow: 0 1px 3px rgba(0,0,0,0.08);
  --shadow-hover: 0 4px 12px rgba(0,0,0,0.12);
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
}}
.header {{
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: white;
  padding: 24px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}}
.header h1 {{ font-size: 22px; font-weight: 600; letter-spacing: 1px; }}
.header .subtitle {{ font-size: 13px; opacity: 0.7; margin-top: 4px; }}
.stats-row {{
  display: flex;
  gap: 16px;
}}
.stat-item {{
  background: rgba(255,255,255,0.1);
  padding: 10px 16px;
  border-radius: var(--radius);
  text-align: center;
  min-width: 80px;
}}
.stat-num {{ font-size: 20px; font-weight: 700; }}
.stat-label {{ font-size: 11px; opacity: 0.7; margin-top: 2px; }}

.main {{
  display: flex;
  gap: 20px;
  padding: 24px 32px;
  align-items: flex-start;
}}

.sidebar {{
  width: 260px;
  flex-shrink: 0;
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 20px;
}}
.sidebar h3 {{
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
.dept-bar {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 13px;
}}
.dept-name {{ width: 60px; color: var(--text-secondary); }}
.bar-track {{
  flex: 1;
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}}
.bar-fill {{
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 3px;
  transition: width 0.4s ease;
}}
.dept-count {{ width: 24px; text-align: right; color: var(--text-secondary); font-size: 12px; }}

.kanban-board {{
  flex: 1;
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
}}
.kanban-col {{
  min-width: 280px;
  max-width: 320px;
  display: flex;
  flex-direction: column;
}}
.col-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 3px solid;
  margin-bottom: 12px;
}}
.col-title {{ font-size: 14px; font-weight: 600; }}
.col-count {{
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
}}
.col-cards {{
  display: flex;
  flex-direction: column;
  gap: 10px;
}}
.card {{
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 4px solid transparent;
}}
.card:hover {{
  box-shadow: var(--shadow-hover);
  transform: translateY(-1px);
}}
.card-header {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}}
.card-title {{
  font-size: 13px;
  font-weight: 600;
  line-height: 1.4;
  word-break: break-all;
}}
.badge {{
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
}}
.card-id {{
  font-size: 11px;
  color: var(--text-secondary);
  font-family: monospace;
  margin-bottom: 6px;
}}
.card-meta {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 11px;
  color: var(--text-secondary);
}}
.card-progress {{
  display: flex;
  align-items: center;
  gap: 4px;
}}
.dot {{
  width: 6px;
  height: 6px;
  border-radius: 50%;
}}
.heartbeat-alive {{ background: #22c55e; }}
.heartbeat-stale {{ background: #f59e0b; }}
.heartbeat-dead {{ background: #ef4444; }}

/* 详情弹窗 */
.modal-overlay {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 100;
  align-items: center;
  justify-content: center;
}}
.modal-overlay.active {{ display: flex; }}
.modal {{
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}}
.modal-header {{
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.modal-header h2 {{ font-size: 16px; }}
.modal-close {{
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
}}
.modal-body {{
  padding: 20px 24px;
  overflow-y: auto;
  font-size: 13px;
  line-height: 1.7;
}}
.timeline {{
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}}
.timeline-item {{
  display: flex;
  gap: 12px;
  align-items: flex-start;
}}
.timeline-dot {{
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
  background: #cbd5e1;
}}
.timeline-content {{ flex: 1; }}
.timeline-time {{ font-size: 11px; color: var(--text-secondary); }}
.timeline-dept {{ font-weight: 600; }}

.footer {{
  text-align: center;
  padding: 16px;
  font-size: 12px;
  color: var(--text-secondary);
}}

@media (max-width: 900px) {{
  .main {{ flex-direction: column; }}
  .sidebar {{ width: 100%; }}
  .kanban-board {{ width: 100%; }}
}}
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>军机处 · 三省六部看板</h1>
    <div class="subtitle">OpenClaw Multi-Agent Orchestration Dashboard</div>
  </div>
  <div class="stats-row">
    <div class="stat-item"><div class="stat-num">{stats['total']}</div><div class="stat-label">总旨意</div></div>
    <div class="stat-item"><div class="stat-num">{stats['completion_rate']}%</div><div class="stat-label">完成率</div></div>
    <div class="stat-item"><div class="stat-num">{stats['rejection_rate']}%</div><div class="stat-label">封驳率</div></div>
    <div class="stat-item"><div class="stat-num">{stats['avg_subtasks']}</div><div class="stat-label">均子任务</div></div>
  </div>
</div>

<div class="main">
  <div class="sidebar">
    <h3>省部活跃度</h3>
    {dept_bars}
  </div>
  <div class="kanban-board">
    {columns_html}
  </div>
</div>

<div class="modal-overlay" id="modal">
  <div class="modal">
    <div class="modal-header">
      <h2 id="modal-title">任务详情</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div class="modal-body" id="modal-body"></div>
  </div>
</div>

<div class="footer">三省六部 · 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · 刷新页面获取最新数据</div>

<script>
// 嵌入的旨意数据（用于前端弹窗展示）
const EDICTS_DATA = {json.dumps(edicts, ensure_ascii=False)};

function showDetail(id) {{
  const e = EDICTS_DATA.find(x => x.id === id);
  if (!e) return;
  const meta = {json.dumps({k:v["label"] for k,v in _STATUS_META.items()})};
  const deptNames = {json.dumps(_DEPT_NAMES)};

  let html = `
    <p><strong>编号：</strong><code>${{e.id}}</code></p>
    <p><strong>状态：</strong><span style="color:${{meta[e.status] ? '#333' : '#333'}}">${{meta[e.status] || e.status}}</span></p>
    <p><strong>内容：</strong></p>
    <div style="background:#f8fafc;padding:12px;border-radius:8px;margin:8px 0;white-space:pre-wrap;">${{e.content}}</div>
  `;

  if (e.zhongshu_plan) {{
    html += `<p><strong>中书省规划：</strong></p><div style="background:#eff6ff;padding:12px;border-radius:8px;margin:8px 0;white-space:pre-wrap;">${{e.zhongshu_plan}}</div>`;
  }}
  if (e.menxia_review) {{
    html += `<p><strong>门下省审议：</strong></p><div style="background:#fffbeb;padding:12px;border-radius:8px;margin:8px 0;white-space:pre-wrap;">${{e.menxia_review}}</div>`;
  }}
  if (Object.keys(e.subtask_results || {{}}).length) {{
    html += `<p><strong>六部执行结果：</strong></p>`;
    for (const [dept, res] of Object.entries(e.subtask_results)) {{
      html += `<div style="background:#f0fdf4;padding:12px;border-radius:8px;margin:8px 0;"><strong>${{deptNames[dept] || dept}}</strong><pre style="margin:6px 0 0;white-space:pre-wrap;">${{typeof res === 'string' ? res : JSON.stringify(res, null, 2)}}</pre></div>`;
    }}
  }}

  html += `<p><strong>流转时间线：</strong></p><div class="timeline">`;
  for (const t of (e.timeline || [])) {{
    const time = t.timestamp.replace('T', ' ').slice(0, 19);
    html += `<div class="timeline-item">
      <div class="timeline-dot" style="background:${{t.stage === 'completed' ? '#22c55e' : t.stage === 'menxia_rejected' ? '#ef4444' : '#3b82f6'}}"></div>
      <div class="timeline-content">
        <div class="timeline-time">${{time}}</div>
        <div><span class="timeline-dept">${{deptNames[t.dept] || t.dept}}</span> → ${{meta[t.stage] || t.stage}} ${{t.note ? '· ' + t.note : ''}}</div>
      </div>
    </div>`;
  }}
  html += `</div>`;

  document.getElementById('modal-title').textContent = e.title;
  document.getElementById('modal-body').innerHTML = html;
  document.getElementById('modal').classList.add('active');
}}

function closeModal() {{
  document.getElementById('modal').classList.remove('active');
}}

document.getElementById('modal').addEventListener('click', e => {{
  if (e.target.id === 'modal') closeModal();
}});
</script>

</body>
</html>'''

        self.output_path.write_text(html, encoding="utf-8")
        return str(self.output_path)

    def _card_html(self, edict: dict) -> str:
        s = edict["status"]
        meta = _STATUS_META.get(s, {"label": s, "color": "#333", "bg": "#fff"})
        created = edict["created_at"].replace("T", " ")[:16]

        # 计算子任务完成进度
        subtasks = edict.get("subtasks", [])
        results = edict.get("subtask_results", {})
        progress = ""
        if subtasks:
            done = sum(1 for st in subtasks if st.get("id") in results)
            pct = int(done / len(subtasks) * 100)
            progress = f'<div class="card-progress"><div class="dot heartbeat-{"alive" if pct==100 else "stale"}"></div><span>{done}/{len(subtasks)}</span></div>'
        else:
            progress = f'<div class="card-progress"><div class="dot {"heartbeat-alive" if s=="completed" else "heartbeat-stale"}"></div><span>{meta["label"]}</span></div>'

        return f'''
        <div class="card" style="border-left-color:{meta['color']}" onclick="showDetail('{edict['id']})">
          <div class="card-header">
            <div class="card-title">{edict['title']}</div>
            <span class="badge" style="background:{meta['bg']};color:{meta['color']}">{meta['label']}</span>
          </div>
          <div class="card-id">{edict['id']}</div>
          <div class="card-meta">
            <span>{created}</span>
            {progress}
          </div>
        </div>
        '''


if __name__ == "__main__":
    sm = StateManager()
    gen = KanbanGenerator(sm)
    path = gen.generate()
    print(f"看板已生成: {path}")
