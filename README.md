# 🔬 EfficientAI Research Skills

**EfficientAI-USTC 实验室共用的科研技能库。** 面向 Codex，围绕文献调研、研究构思、论文写作和投稿前模拟审稿，沉淀可复用的科研工作流。

[技能方向](#-技能方向) · [科研工作流](#-科研工作流) · [使用方式](#-使用方式) · [参与贡献](#-参与贡献)

## ✨ 技能方向

| 方向 | 目录 | 用途 | 状态 |
| --- | --- | --- | --- |
| 📚 文献调研 | [`research-survey`](skills/research-survey/) | 检索与阅读文献，梳理方法、研究脉络和开放问题 |
| 💡 研究构思 | [`research-ideation`](skills/research-ideation/) | 构思研究问题、方法方案和实验思路 |
| ✍️ 论文写作 | [`paper-writing`](skills/paper-writing/) | 组织论文故事线、章节结构与学术表达 |
| 🔍 模拟审稿 | [`paper-review`](skills/paper-review/) | 以审稿人视角评审本实验室稿件，提出潜在质疑和修改建议 |


## 🔄 科研工作流

```mermaid
flowchart LR
    A["📚 文献调研"] --> B["💡 研究构思"]
    B --> C["✍️ 论文写作"]
    C --> D["🔍 模拟审稿"]
    D -->|修改建议| C
```

四个方向围绕科研过程衔接，也可根据具体任务单独使用。

## 📚 文献调研 · research-survey

围绕研究主题组织文献检索、论文阅读与方法比较，梳理研究现状、技术脉络和待解决的问题。

## 💡 研究构思 · research-ideation

从已有研究和实际问题出发，形成研究问题与方法设想，逐步明确贡献、实验思路和研究方案。

## ✍️ 论文写作 · paper-writing

围绕论文故事线组织章节与段落，辅助大纲设计、稿件撰写、学术表达和内容修改。

## 🔍 模拟审稿 · paper-review

以审稿人视角评审本实验室自己的稿件，围绕创新性、方法、实验、论证和表达提出潜在质疑，帮助作者确定修改重点。

## 📦 使用方式

技能目录格式和资源组织约定见 [skills/README.md](skills/README.md)。

## 🗂️ 仓库结构

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
    ├── README.md
    ├── research-survey/
    ├── research-ideation/
    ├── paper-writing/
    └── paper-review/
```

## 🤝 参与贡献

欢迎实验室成员分享和完善日常科研中使用的工作流。新增或修改技能的目录、命名和提交约定见 [贡献指南](CONTRIBUTING.md)。

## 致谢

仓库展示与组织方式参考 [EvoScientist/EvoSkills](https://github.com/EvoScientist/EvoSkills)。
