# EfficientAI Research Skills

EfficientAI-USTC 实验室共用的 Codex 科研技能库。目前仅建立目录架构和维护约定，尚未收录具体技能。

## 目录架构

```text
research-skills/
├── README.md
├── CONTRIBUTING.md
├── AGENTS.md
├── .gitignore
├── .gitattributes
├── .github/
│   └── pull_request_template.md
└── skills/
    ├── literature-review/    # 调研
    ├── peer-review/          # 以审稿人视角评审本实验室稿件
    ├── ideation/             # 构思 idea
    └── paper-writing/        # 论文写作
```

各分类内的 `.gitkeep` 仅用于在 Git 中保留空目录；新增首个技能后可删除。

## 分类边界

| 分类 | 收录范围 |
| --- | --- |
| `literature-review` | 文献检索、阅读、比较与研究现状梳理 |
| `peer-review` | 以审稿人视角评审本实验室自己的稿件，检查创新性、论证、实验和表达，识别潜在质疑并提出修改建议 |
| `ideation` | 研究问题、假设、方法构思与验证方案设计 |
| `paper-writing` | 论文结构、段落写作、学术表达与稿件修改 |

按科研任务分类，不按研究方向或模型再建一套重复目录。跨环节的技能根据主要交付物选择一个分类，在描述中说明其他用途。

## 后续技能的存放方式

每个技能独立占一个目录：`skills/<category>/<skill-name>/SKILL.md`。

- `SKILL.md` 是入口，头部包含 `name` 和 `description`。
- `references/`、`scripts/`、`assets/` 按实际需要放在该技能目录内。
- 技能名称在整个仓库中唯一，使用小写字母、数字和连字符。
- 分类目录用于整理仓库；分发或安装时以单个技能文件夹为单位。

本阶段不添加具体技能、依赖或自动化工具。待首批技能明确后，再按实际需要加入安装与校验能力。

## 协作

新增和修改通过分支与 PR 提交，约定见 [CONTRIBUTING.md](CONTRIBUTING.md)。仓库许可证待实验室确定。

技能格式依据：[OpenAI 官方技能文档](https://learn.chatgpt.com/docs/build-skills)。
