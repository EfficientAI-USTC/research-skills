# 与参考样例一致的输出契约

## MoEZip 样例

以工作区的 `papers/llm-methods/2610.30206_MoEZip/` 为默认参考。可直接对照 [MoEZip.zh.html](../../../../papers/llm-methods/2610.30206_MoEZip/MoEZip.zh.html)、[MoEZip.zh.md](../../../../papers/llm-methods/2610.30206_MoEZip/MoEZip.zh.md)、[notes.md](../../../../papers/llm-methods/2610.30206_MoEZip/notes.md) 和 [reading_card.md](../../../../papers/llm-methods/2610.30206_MoEZip/reading_card.md)。样例在其他工作区不可用时，按下列契约执行。

示例调用：`$paper-reading https://arxiv.org/abs/2610.30206`。MoEZip 的完整译文覆盖摘要和第 1–6 节；两种格式同步保留图表、公式、编号和脚注，原件、笔记和论文卡另存。新论文以各自实际主文范围为准。HTML 应内嵌图像，完整展示译文直到主文末节，并在最终回复中提供可直接打开的链接。

## 目录与验收

完整归档包含 `source.pdf`、`notes.md`、`reading_card.md` 和顶层的 `.zh.md`、`.zh.html`；有原始 HTML 时另存 `paper.html`。提取中间件按来源变化，样例中特有的文件不自动成为要求。

```text
papers/
  README.md
  ai-agents/
    <arxivID或其他稳定标识>_<短名>/
      source.pdf                  # 完整原始 PDF；不可得则注明
      paper.html                  # 原始网页；仅取得时保存
      paper.html.md               # HTML 全文提取；或 paper.pdf.md
      main.en.md                  # 人工核定范围的英文主文
      glossary.md                 # 本篇术语表
      <短名>.zh.md                # 完整主文译文，目录顶层
      <短名>.zh.html              # 完整主文中文 HTML，与 Markdown 同源，图片内嵌
      notes.md                    # 详细阅读笔记
      reading_card.md             # 五段式论文卡 + 摘要译文
      images/                     # 原图、表格/算法裁剪
      pages/                      # PDF 轨逐页图，按需保留
      chunks_zh/
        manifest.json
        chunk_001.md
        chunk_001.zh.md
        ...
      status.json                 # 来源、版本、范围、进度和问题
      extraction.json             # 提取清单与异常
```

无 arXiv ID 时使用 DOI 的安全文件名或 `年份_短名`，不伪造 ID。路径每段避免 Windows 非法字符、设备保留名与末尾空格/句点；同论文不同版本不能静默混合。已存在归档先确认版本，保留用户修改，必要时新建版本后缀目录。

`status.json` 至少记录 `title`、`source_url`、`version`、`scope`、`stage`、`completed_chunks`、`remaining`、`issues`；原件、图表、公式或译文有缺项，或者完整的 `.zh.html` 未生成时，`stage` 不得写 `complete`。结构校验后仍须通读确认语义，最终验收才改完成状态。

HTML 样式对应示例：中文衬线字体、居中正文约 860px、清楚的标题、可横向滚动表格、等比图片、脚注和 MathJax 公式。内嵌图片不代表公式脚本完全离线可用，交付时如实说明。
