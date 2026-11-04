# Skills

本目录用于存放实验室共用的 Codex 科研技能。四个科研方向保留为预留目录。

## 技能维护工具

| 技能 | 用途 |
| --- | --- |
| [research-skill-creator](research-skill-creator/SKILL.md) | 创建或更新技能包，设计试用请求，根据反馈迭代并同步目录 |

## 预留目录

| 目录 | 方向 |
| --- | --- |
| [`research-survey/`](research-survey/) | 文献调研 |
| [`research-ideation/`](research-ideation/) | 研究构思 |
| [`paper-writing/`](paper-writing/) | 论文写作 |
| [`paper-review/`](paper-review/) | 以审稿人视角评审本实验室自己的稿件 |

目录内的 `.gitkeep` 用于保留空目录；加入技能文件后可删除。

## 扁平组织

每个技能直接位于 `skills/<skill-name>/`，各技能平级维护。四个预留目录是未来技能的独立位置。后续新增更细分的技能时，同样直接放在 `skills/` 下，并在根 README 中关联所属方向。

一个技能只保留一份。涉及多个科研环节时，在描述中说明其适用场景。

## 单个技能的结构

以下为结构约定，按实际需要添加资源：

```text
<skill-name>/
├── SKILL.md          # 技能入口
├── references/       # 可选：按需读取的参考资料
├── scripts/          # 可选：辅助脚本
└── assets/           # 可选：模板及输出资源
```

- `SKILL.md` 的 YAML 头部包含 `name` 和 `description`；名称与目录名一致，描述说明用途和触发场景。
- 正文围绕任务所需输入、工作流和输出组织。
- 资源放在技能自己的目录内，使用相对路径；需要外部工具或依赖时，在技能中说明。
- 分发与安装以整个技能目录为单位。

新增技能的协作约定见 [CONTRIBUTING.md](../CONTRIBUTING.md)。
