---
name: paper-reading
description: 阅读和翻译论文，生成含原始 PDF、分节笔记、五段式论文卡、保留图表公式的中文 Markdown 与 HTML 的本地论文档案。适用于给出论文 PDF、arXiv 链接并要求阅读、精读、翻译或归档；仅问论文某个细节时不自动启动整篇翻译。
---

# 论文阅读与归档

## 交付约定

显式调用本 skill 并只给论文 PDF 或 arXiv 链接，等同于“完整处理”。默认按 [MoEZip 样例](references/output_contract.md#moezip-样例)交付速览、逐段主文翻译、分节笔记、五段式论文卡和原件归档。仅给 arXiv 链接即可开始：必须先把原件落实为本地文件，不因输入形式缩减范围，也不要求用户下载后重新上传。用户明确只要速览、问答、翻译某节或暂不归档时，按指定范围执行。

**完整交付必须有顶层 `<短名>.zh.md` 和 `<短名>.zh.html`。** 两者由同一份完整译文生成，均须覆盖摘要、全部主文章节及主文后的独立 Impact Statement 等正文声明（如有）。References、致谢、附录和补充材料默认保留原件。不得因缺少名为 Conclusion 的章节而漏掉末节；`notes.html`、摘要、节选或原始 `paper.html` 均不能替代完整中文 HTML。

先用简短进度消息给出摘要译文和“问题／方法／结论”三句话，再继续处理同一任务，直到交付完毕。不要以“已启动后台处理”代替实际完成，也不要在结束对话后承诺自行继续。研究方向只取用户明确提供的上下文；未提供时写“待结合具体研究方向判断”，分析一般可借鉴点，不套用他人的研究项目。

## 路径与运行环境

- 全部脚本相对于本 skill 的位置解析，不假定工作目录里有 `scripts/`。下文 `SKILL_DIR` 指当前 `SKILL.md` 的父目录；`WORKSPACE` 指用户当前项目根目录。
- 论文库默认 `WORKSPACE/papers/`；用户另指定目录时使用该目录。不得把用户给的参考输出目录当作新论文库或覆盖其中内容。
- 不依赖 MinerU、GPU、WSL、Hermes 或其他 skill。无需 API key：模型负责阅读和翻译，脚本负责提取、切块、校验和渲染。
- 先寻找项目内 `.venv-paper-reading/Scripts/python.exe`（Windows）或 `.venv-paper-reading/bin/python`（macOS/Linux）。不存在时选可用 Python 3.11+，创建项目内虚拟环境，并以该解释器安装 `SKILL_DIR/scripts/requirements.txt`。不将本机虚拟环境复制到另一台电脑。
- 当前工作区可直接使用 `.venv-paper-reading/Scripts/python.exe`。所有路径参数加引号，Windows 使用 PowerShell；不需要激活环境。

## 工作流程

1. **识别来源与范围。** 记录标题、作者、版本、日期、arXiv/DOI、领域、链接及访问日期。只给标题或来源不明确时先找原文；缺失项标明未核实。先读 [output_contract.md](references/output_contract.md)。
2. **先获取本地原件，再提取。** 对 arXiv 链接，锁定论文 ID 和版本，先检查论文目录中是否已有同版本、可打开的 `source.pdf` 和 `paper.html`；缺哪项就主动从 arXiv 下载哪项（HTML 仅在该版本提供时下载）。浏览网页、摘要或搜索片段不算取得文件。HTML 取得后优先用于提取；HTML 不可得时直接走 PDF。下载端点或工具失败时按 [pipeline.md](references/pipeline.md) 换可用方式重试；有一份可读原件就继续，并记录缺项。HTML 提取从 MathML 的 TeX 注解保留公式，从原始表格保留结构；脚本输出资源清单。PDF 轨使用 PyMuPDF 提取文本并保存逐页图片，供核对双栏顺序、公式、图表与算法。不能把 PDF 文本提取当作可靠的公式识别。扫描件无文字时依据页图逐页读取或使用已可用 OCR，并明确提取质量。
3. **确认完整性。** 对照原文列出主文章节、图、表、公式及算法编号。检查 HTML 中嵌套表格、span 形式的表格、脚注与图片是否完整。无法忠实重建的表格／算法，用 PDF 页图裁剪保留原文，加中文标题和解读；截图内数字不做伪造翻译。必要时用 `crop` 子命令截取。缺少 HTML／PDF／图表时记录原因，不能生成空文件冒充原件。
4. **准备主文。** 提取的全文为 `paper.html.md` 或 `paper.pdf.md`；据实际结构另存 `main.en.md`，保留标题、作者、摘要及全部主文。切分前按论文标题和节边界人工确认主文范围，不能仅凭第一次出现单词 References 截断。图片统一相对 `images/`，PDF 回退资源可引用 `pages/`。不必建立虚假的 `mineru/`。
5. **翻译。** 先读 [translation_prompt.md](translation_prompt.md)，建立 `glossary.md`。运行 `chunk`；逐块完整译为 `chunks_zh/chunk_NNN.zh.md`。块数不设上限；不以摘要替代翻译。参考文献引用、公式、数字及图表一一对应。全部完成后运行 `assemble` 生成顶层 `<短名>.zh.md` 与 `.zh.html`；任何公式／图片／表格结构不一致都先修复。修正英文提取错误时先依据原文修改 `main.en.md`，重新切块，避免译文默改来源。
6. **阅读产物。** 根据 [reading_card.md](reading_card.md) 填五段式论文卡；根据 [notes_template.md](references/notes_template.md) 写详细分节笔记，包括核心论证链、方法操作、实验设置、数字与证据位置、批判问题和可借鉴点。原文结论、自己的判断、尚待验证的机制分开；没有研究方向就不作私人关联评分。不自动启动实验。
7. **验收归档。** 全文对照校对：段落、列表、图表标题、公式、脚注、数值、术语与范围。运行 `check`，并在可用浏览器中查看 HTML 的正文、表格、图与公式；公式显示依赖 MathJax 网络资源，图片已内嵌，离线时仍保留 LaTeX。`check` 只能验证结构，不代表语义通过。修订后重生成 HTML。更新 `papers/README.md` 索引，只修改当前论文条目，保留已有内容。只将实际讨论中出现的待读论文按需加入 `TOREAD.md`，不自动扩展文献任务。

## 完成与中断

完整交付时直接链接 `<短名>.zh.html`、`<短名>.zh.md`、原始 PDF、笔记和论文卡。核对 HTML 已渲染到主文末节且与 Markdown 范围一致；结构检查和人工通读通过后才标记完成。若确有来源获取、翻译权限、上下文或渲染限制，保留可交付产物和已有分块，在 `status.json` 记录具体限制与缺项，明确说明部分完成；不得把笔记 HTML 或部分译文标为完整译文。恢复时只处理未完成或受修改影响的块。
