# 与参考样例一致的输出契约

参考样例包含十篇论文；每篇稳定共有 `source.pdf`、`notes.md`、`reading_card.md`、顶层 `.zh.md` 和 `.zh.html`。有 HTML 原件时包含 `paper.html`。提取中间件可变化，不能把某个样例额外包含的公众号文稿、压缩包或 MinerU 缓存视作每篇必需产物。

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
      <短名>.zh.html              # 可浏览预览，图片内嵌
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

`status.json` 至少记录 `title`、`source_url`、`version`、`scope`、`stage`、`completed_chunks`、`remaining`、`issues`；网络、图表、公式或译文未完整时 `stage` 不得写 `complete`。结构校验后仍须通读确认语义，最终验收才改完成状态。

HTML 样式对应示例：中文衬线字体、居中正文约 860px、清楚的标题、可横向滚动表格、等比图片、脚注和 MathJax 公式。内嵌图片不代表公式脚本完全离线可用，交付时如实说明。
