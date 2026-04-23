#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三省六部 · 命令行入口 (Edict CLI)
用法:
  python edict_cli.py create "旨意标题" "旨意内容"     # 创建旨意
  python edict_cli.py list [--status STATUS]           # 列出租有旨意
  python edict_cli.py show <edict_id>                  # 查看旨意详情
  python edict_cli.py transition <id> <status> <dept> [--note NOTE]  # 状态转换
  python edict_cli.py kanban                           # 生成看板
  python edict_cli.py memorial <edict_id>              # 导出奏折
  python edict_cli.py stats                            # 查看统计
"""

import argparse
import json
import sys
from pathlib import Path

# 确保同级模块可导入
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from state_manager import StateManager
from kanban_generator import KanbanGenerator


def cmd_create(args):
    sm = StateManager()
    e = sm.create_edict(args.title, args.content, source=args.source)
    print(f"旨意已创建: {e['id']}")
    print(f"标题: {e['title']}")
    print(f"状态: {e['status']}")
    return e['id']


def cmd_list(args):
    sm = StateManager()
    edicts = sm.list_edicts(status=args.status, limit=args.limit)
    if not edicts:
        print("暂无旨意。")
        return
    print(f"{'编号':<22} {'状态':<18} {'标题'}")
    print("-" * 70)
    for e in edicts:
        print(f"{e['id']:<22} {e['status']:<18} {e['title']}")


def cmd_show(args):
    sm = StateManager()
    try:
        e = sm.load_edict(args.id)
    except FileNotFoundError:
        print(f"旨意不存在: {args.id}")
        return
    print(json.dumps(e, ensure_ascii=False, indent=2))


def cmd_transition(args):
    sm = StateManager()
    try:
        e = sm.transition(args.id, args.status, args.dept, note=args.note or "")
        print(f"状态转换成功: {e['id']}")
        print(f"新状态: {e['status']}")
    except (ValueError, PermissionError) as err:
        print(f"[错误] {err}")
        sys.exit(1)


def cmd_kanban(args):
    sm = StateManager()
    gen = KanbanGenerator(sm)
    path = gen.generate()
    print(f"看板已生成: {path}")


def cmd_memorial(args):
    sm = StateManager()
    try:
        e = sm.load_edict(args.id)
    except FileNotFoundError:
        print(f"旨意不存在: {args.id}")
        return

    if e["status"] != "completed":
        print(f"警告: 该旨意尚未完成（当前状态: {e['status']}），奏折可能不完整。")

    memorial = sm._generate_memorial_draft(e)
    out_dir = BASE / "data" / "memorials"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.id}.md"
    out_path.write_text(memorial, encoding="utf-8")
    print(f"奏折已导出: {out_path}")


def cmd_stats(args):
    sm = StateManager()
    stats = sm.get_stats()
    print(json.dumps(stats, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="三省六部 · Edict CLI")
    sub = parser.add_subparsers(dest="command", help="子命令")

    # create
    p_create = sub.add_parser("create", help="创建新旨意")
    p_create.add_argument("title", help="旨意标题")
    p_create.add_argument("content", help="旨意内容")
    p_create.add_argument("--source", default="cli", help="来源标识")

    # list
    p_list = sub.add_parser("list", help="列出租有旨意")
    p_list.add_argument("--status", default=None, help="按状态过滤")
    p_list.add_argument("--limit", type=int, default=100, help="最大条数")

    # show
    p_show = sub.add_parser("show", help="查看旨意详情")
    p_show.add_argument("id", help="旨意编号")

    # transition
    p_trans = sub.add_parser("transition", help="状态转换")
    p_trans.add_argument("id", help="旨意编号")
    p_trans.add_argument("status", help="目标状态")
    p_trans.add_argument("dept", help="操作部门")
    p_trans.add_argument("--note", default="", help="备注")

    # kanban
    sub.add_parser("kanban", help="生成看板")

    # memorial
    p_mem = sub.add_parser("memorial", help="导出奏折")
    p_mem.add_argument("id", help="旨意编号")

    # stats
    sub.add_parser("stats", help="查看统计")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    globals()[f"cmd_{args.command}"](args)


if __name__ == "__main__":
    main()
