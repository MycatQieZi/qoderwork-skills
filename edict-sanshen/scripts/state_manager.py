#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三省六部 · 状态管理核心 (State Manager)
负责：旨意生命周期、状态机校验、JSON 持久化、权限矩阵
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Literal

# 状态定义
STATUS = Literal[
    "draft",           # 草稿（刚创建）
    "taizi_sorted",    # 太子分拣完毕
    "zhongshu_planned",# 中书省规划完毕
    "menxia_reviewing",# 门下省审议中
    "menxia_rejected", # 门下省封驳
    "menxia_approved", # 门下省准奏
    "shangshu_dispatching", # 尚书省派发中
    "executing",       # 六部执行中
    "reviewing",       # 待审查
    "completed",       # 已完成
    "cancelled",       # 已取消
    "blocked",         # 已阻塞
    "stopped",         # 已叫停
]

# 合法状态转换路径（状态机）
_VALID_TRANSITIONS: Dict[str, List[str]] = {
    "draft": ["taizi_sorted"],
    "taizi_sorted": ["zhongshu_planned"],
    "zhongshu_planned": ["menxia_reviewing"],
    "menxia_reviewing": ["menxia_rejected", "menxia_approved"],
    "menxia_rejected": ["zhongshu_planned", "cancelled"],  # 封驳后：重规划 或 取消
    "menxia_approved": ["shangshu_dispatching"],
    "shangshu_dispatching": ["executing"],
    "executing": ["reviewing", "blocked", "stopped"],
    "reviewing": ["completed", "executing"],  # 审查不通过可回退执行
    "blocked": ["executing", "cancelled"],
    "stopped": ["executing", "cancelled"],
    "completed": [],  # 终态
    "cancelled": [],  # 终态
}

# 权限矩阵：哪个部门可以推动到哪个状态
_DEPARTMENT_ACTIONS: Dict[str, List[str]] = {
    "taizi": ["taizi_sorted"],
    "zhongshu": ["zhongshu_planned"],
    "menxia": ["menxia_reviewing", "menxia_rejected", "menxia_approved"],
    "shangshu": ["shangshu_dispatching", "executing", "reviewing", "completed"],
    "hubu": ["executing"],
    "libu": ["executing"],
    "bingbu": ["executing"],
    "xingbu": ["executing"],
    "gongbu": ["executing"],
    "libu_hr": ["executing"],
    "user": ["cancelled", "stopped"],  # 皇上可直接叫停/取消
}

# 部门中文名映射
_DEPT_NAMES: Dict[str, str] = {
    "taizi": "太子",
    "zhongshu": "中书省",
    "menxia": "门下省",
    "shangshu": "尚书省",
    "hubu": "户部",
    "libu": "礼部",
    "bingbu": "兵部",
    "xingbu": "刑部",
    "gongbu": "工部",
    "libu_hr": "吏部",
    "zaochao": "早朝官",
    "user": "皇上",
}

class StateManager:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            base = Path(__file__).resolve().parent.parent
            data_dir = base / "data" / "edicts"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _edict_path(self, edict_id: str) -> Path:
        return self.data_dir / f"{edict_id}.json"

    def create_edict(self, title: str, content: str, source: str = "user") -> Dict:
        """
        创建新旨意（皇上下旨）
        """
        edict_id = f"ED-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        edict = {
            "id": edict_id,
            "title": self._clean_title(title),
            "content": content,
            "source": source,
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "timeline": [
                {"stage": "draft", "dept": "user", "timestamp": datetime.now().isoformat(), "note": "皇上下旨"}
            ],
            "zhongshu_plan": None,      # 中书省规划方案
            "menxia_review": None,      # 门下省审议意见
            "subtasks": [],             # 尚书省拆解的子任务
            "subtask_results": {},      # 六部执行结果
            "memorial": None,           # 最终奏折
            "metadata": {
                "rejection_count": 0,   # 被封驳次数
                "retry_count": 0,       # 重试次数
                "assignees": [],        # 被指派的六部
                "priority": "normal",   # 优先级
                "tags": [],
            },
        }
        self._save(edict)
        return edict

    def transition(self, edict_id: str, new_status: str, dept: str, note: str = "") -> Dict:
        """
        状态转换（含状态机校验 + 权限校验）
        """
        edict = self.load_edict(edict_id)
        current = edict["status"]

        # 1. 状态机校验
        if new_status not in _VALID_TRANSITIONS.get(current, []):
            raise ValueError(
                f"[状态机违规] 旨意 {edict_id}: 非法跳转 '{current}' → '{new_status}'. "
                f"允许的路径: {_VALID_TRANSITIONS.get(current, [])}"
            )

        # 2. 权限校验
        allowed_statuses = _DEPARTMENT_ACTIONS.get(dept, [])
        if new_status not in allowed_statuses and dept not in ["user", "system"]:
            raise PermissionError(
                f"[权限不足] 部门 '{dept}' 无权将状态设为 '{new_status}'."
            )

        # 3. 执行转换
        edict["status"] = new_status
        edict["updated_at"] = datetime.now().isoformat()
        edict["timeline"].append({
            "stage": new_status,
            "dept": dept,
            "timestamp": datetime.now().isoformat(),
            "note": note or f"{_DEPT_NAMES.get(dept, dept)} 操作",
        })

        # 4. 特殊状态处理
        if new_status == "menxia_rejected":
            edict["metadata"]["rejection_count"] += 1
        elif new_status == "completed":
            edict["memorial"] = self._generate_memorial_draft(edict)

        self._save(edict)
        return edict

    def update_edict(self, edict_id: str, field: str, value, dept: str) -> Dict:
        """
        更新旨意字段（带审计日志）
        """
        edict = self.load_edict(edict_id)
        if field not in edict:
            raise KeyError(f"旨意中不存在字段 '{field}'")

        old_value = edict[field]
        edict[field] = value
        edict["updated_at"] = datetime.now().isoformat()

        # 记录修改日志
        if "audit_log" not in edict:
            edict["audit_log"] = []
        edict["audit_log"].append({
            "timestamp": datetime.now().isoformat(),
            "dept": dept,
            "field": field,
            "old": old_value,
            "new": value,
        })

        self._save(edict)
        return edict

    def load_edict(self, edict_id: str) -> Dict:
        path = self._edict_path(edict_id)
        if not path.exists():
            raise FileNotFoundError(f"旨意不存在: {edict_id}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_edicts(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        列出租有旨意（可选按状态过滤）
        """
        edicts = []
        for f in sorted(self.data_dir.glob("ED-*.json"), reverse=True):
            with open(f, "r", encoding="utf-8") as fp:
                e = json.load(fp)
                if status is None or e["status"] == status:
                    edicts.append(e)
        return edicts[:limit]

    def get_stats(self) -> Dict:
        """
        获取统计信息（用于看板）
        """
        all_edicts = self.list_edicts(limit=9999)
        stats = {
            "total": len(all_edicts),
            "by_status": {},
            "by_dept": {},
            "completion_rate": 0.0,
            "rejection_rate": 0.0,
            "avg_subtasks": 0.0,
        }
        completed = 0
        rejected = 0
        total_subtasks = 0

        for e in all_edicts:
            s = e["status"]
            stats["by_status"][s] = stats["by_status"].get(s, 0) + 1

            # 统计各部门操作次数
            for t in e.get("timeline", []):
                d = t["dept"]
                stats["by_dept"][d] = stats["by_dept"].get(d, 0) + 1

            if s == "completed":
                completed += 1
            if e["metadata"]["rejection_count"] > 0:
                rejected += 1
            total_subtasks += len(e.get("subtasks", []))

        if all_edicts:
            stats["completion_rate"] = round(completed / len(all_edicts) * 100, 1)
            stats["rejection_rate"] = round(rejected / len(all_edicts) * 100, 1)
            stats["avg_subtasks"] = round(total_subtasks / len(all_edicts), 1)

        return stats

    def _save(self, edict: Dict):
        path = self._edict_path(edict["id"])
        with open(path, "w", encoding="utf-8") as f:
            json.dump(edict, f, ensure_ascii=False, indent=2)

    def _clean_title(self, title: str) -> str:
        """
        旨意标题数据清洗：剥离文件路径、元数据前缀
        """
        import re
        # 去掉文件路径前缀
        title = re.sub(r"^[\w\-]+[/\\]", "", title)
        # 去掉常见元数据前缀
        title = re.sub(r"^(feat|fix|docs|test|chore|refactor)[\s:]", "", title, flags=re.I)
        # 去掉时间戳前缀
        title = re.sub(r"^\d{4}-\d{2}-\d{2}\s+", "", title)
        return title.strip()

    def _generate_memorial_draft(self, edict: Dict) -> str:
        """
        自动生成奏折草稿
        """
        lines = [
            f"# 奏折 · {edict['title']}",
            "",
            f"**旨意编号**: `{edict['id']}`",
            f"**下旨时间**: {edict['created_at']}",
            f"**完成时间**: {edict['updated_at']}",
            f"**封驳次数**: {edict['metadata']['rejection_count']}",
            "",
            "---",
            "",
            "## 一、圣旨原文",
            "",
            edict["content"],
            "",
            "---",
            "",
            "## 二、中书省规划方案",
            "",
            edict.get("zhongshu_plan", "（无规划记录）") or "（无规划记录）",
            "",
            "---",
            "",
            "## 三、门下省审议",
            "",
            edict.get("menxia_review", "（无审议记录）") or "（无审议记录）",
            "",
            "---",
            "",
            "## 四、六部执行结果",
            "",
        ]
        results = edict.get("subtask_results", {})
        if results:
            for dept, result in results.items():
                dept_name = _DEPT_NAMES.get(dept, dept)
                lines.append(f"### {dept_name}（{dept}）")
                lines.append("")
                lines.append(str(result))
                lines.append("")
        else:
            lines.append("（无执行记录）")

        lines.extend([
            "",
            "---",
            "",
            "## 五、流转时间线",
            "",
        ])
        for t in edict.get("timeline", []):
            ts = t["timestamp"].replace("T", " ")[:19]
            dept_name = _DEPT_NAMES.get(t["dept"], t["dept"])
            lines.append(f"- `{ts}` | **{dept_name}** → {t['stage']} | {t.get('note', '')}")

        lines.extend([
            "",
            "---",
            "",
            "*此奏折由三省六部系统自动生成，存档于奏折阁。*",
        ])
        return "\n".join(lines)


if __name__ == "__main__":
    # 简单测试
    sm = StateManager()
    e = sm.create_edict("设计用户注册系统", "需要RESTful API + PostgreSQL + JWT")
    print(f"Created: {e['id']} - {e['title']}")

    sm.transition(e["id"], "taizi_sorted", "taizi", "闲聊已过滤，确认为旨意")
    sm.transition(e["id"], "zhongshu_planned", "zhongshu", "已拆解为5个子任务")
    sm.transition(e["id"], "menxia_reviewing", "menxia", "开始审议")
    sm.transition(e["id"], "menxia_approved", "menxia", "方案完备，准奏")
    sm.transition(e["id"], "shangshu_dispatching", "shangshu", "派发至兵部、工部、礼部")
    sm.transition(e["id"], "executing", "shangshu", "六部开始执行")

    print("Stats:", json.dumps(sm.get_stats(), ensure_ascii=False, indent=2))
