# qoderwork-skills

个人 Agent Skills 仓库。每个顶层目录 = 一个技能，目录名即技能名，入口一律是 `SKILL.md`。

## 目录结构

```
skill-name/
├── SKILL.md              # 必需：主指令 + YAML frontmatter
├── *.md                  # 可选：参考文档、模板、例句库
├── report-template.html  # 可选：输出骨架
├── scripts/              # 可选：工具脚本
└── .skill-metadata.yaml  # 可选：QoderWork 示例提示词
```

`SKILL.md` 的 frontmatter 约定：

| 字段 | 说明 |
|------|------|
| `name` | 小写字母/数字/连字符，≤64 字符，与目录名一致 |
| `version` | 语义化版本，如 `1.0.0` |
| `description` | 英文，第三人称，写清 **做什么（WHAT）+ 何时用（WHEN）** |
| `description_zh` | 对应的中文描述 |

编写规范见 [create-skill](create-skill/SKILL.md)：SKILL.md 正文控制在 500 行以内，详细内容按渐进式披露拆到同级文件，引用只做一层。

## 技能清单（15 个）

### 文档与办公

| 技能 | 说明 |
|------|------|
| [docx](docx/SKILL.md) | Word 文档工具集：内容提取、生成、页面操作、表单填写 |
| [pdf](pdf/SKILL.md) | PDF 工具集：文本/表格提取、生成、合并拆分、表单与水印 |
| [pptx](pptx/SKILL.md) | PowerPoint 工具集：幻灯片生成、内容修改、演示文稿分析 |
| [xlsx](xlsx/SKILL.md) | Excel 工具集：数据提取、生成、格式处理、公式计算 |
| [meeting-minutes](meeting-minutes/SKILL.md) | 会议纪要：提纲确认 → 内容收集 → 输出独立 HTML 报告 |

> `docx` / `pdf` / `pptx` / `xlsx` 为 Proprietary 授权，完整条款见各技能声明的 `LICENSE.txt`。

### 工程方法与质量

| 技能 | 说明 |
|------|------|
| [create-skill](create-skill/SKILL.md) | 创建新技能的元技能：需求收集、结构设计、编写规范与反模式 |
| [scope-anchor](scope-anchor/SKILL.md) | 范围锚点：把领域/作用对象/基础目标/非目标写入 `SCOPE.md`，偏离时提示但不阻断 |
| [test-module-designer](test-module-designer/SKILL.md) | 验证模块设计：工程项目出 `TESTPLAN.md`，调研类项目出 `INQUIRY.md` |
| [token-cost-estimator](token-cost-estimator/SKILL.md) | 开工前按低/中/高/超高四档预估 token 成本，高成本先确认再动手 |

### 编排与协作

| 技能 | 说明 |
|------|------|
| [edict-sanshen](edict-sanshen/SKILL.md) | 三省六部多智能体工作流：规划 → 强制审计 → 并行执行 → 看板 |

### 平台与生态

| 技能 | 说明 |
|------|------|
| [find-skills](find-skills/SKILL.md) | 发现并安装开源生态中的技能 |
| [install-skill-dependency](install-skill-dependency/SKILL.md) | 诊断并修复技能缺失的依赖、二进制与运行时 |
| [plugin-creator](plugin-creator/SKILL.md) | 创建/定制 QoderWork 专家套件（角色向技能包） |

### 互动与氛围

| 技能 | 说明 |
|------|------|
| [conversation-opener](conversation-opener/SKILL.md) | 每组新对话开头给一句贴合项目类型的中文名言/鼓励语 |
| [drink-recommender](drink-recommender/SKILL.md) | 按关键词情绪 + 当前地址推荐附近咖啡店的一杯咖啡/奶茶 |

## 安装

把需要的技能目录放到运行时对应的 skills 目录下即可：

| 环境 | 路径 |
|------|------|
| Host（macOS/Linux） | `~/.qoderwork/skills/<skill-name>/` |
| Host（Windows） | `%USERPROFILE%\.qoderwork\skills\<skill-name>\` |
| VM / Container | `/root/.qoderwork/skills/<skill-name>/` |

## 新增技能

1. 建目录（小写连字符），写 `SKILL.md` + frontmatter。
2. 详细资料拆到同级文件，引用保持一层深度。
3. 在本 README 对应分类表格里补一行。
4. 提交并推送到 `main`。
