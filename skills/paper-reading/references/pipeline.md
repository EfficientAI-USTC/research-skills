# 脚本操作

`PY` 表示具备 `scripts/requirements.txt` 依赖的 Python；`PIPE` 是本 skill 下 `scripts/paper_pipeline.py` 的绝对路径。PowerShell 中用 `& $PY $PIPE ...`。脚本不会调用模型或付费 API，翻译块由当前模型撰写。

## 提取

```powershell
& $PY $PIPE extract-html --url 'https://arxiv.org/html/论文IDv版本' --out '论文目录'
# 已下载网页：相对图片优先从网页同目录读，缺失时以 --url 作 base 下载
& $PY $PIPE extract-html --file '原始paper.html' --url 'https://arxiv.org/html/论文IDv版本' --out '论文目录'
& $PY $PIPE extract-pdf --pdf '原始论文.pdf' --out '论文目录'
```

arXiv 用相同 ID 和版本的 PDF 地址保存为 `source.pdf`（使用当前可用下载工具）；HTML 和 PDF 都获取失败时说明缺项。HTML 失败可直接转 PDF；不安装 MinerU。PDF 命令会保存原件、全文提取和 140dpi 页图；逐页核对后构造可靠的 `main.en.md`。页图可完整保留图表，不能以页图存在推断翻译完整。

```powershell
& $PY $PIPE crop --pdf '论文目录/source.pdf' --page 3 --rect 20 80 580 420 --out '论文目录/images/table_1.png'
```

页码从 1 起，坐标为 PDF point，按实际页面尺寸选择；省略 `--rect` 截整页。

## 翻译和预览

人工从全文生成 `main.en.md` 后：

```powershell
& $PY $PIPE chunk --source '论文目录/main.en.md' --out '论文目录/chunks_zh'
# 读取 translation_prompt.md 与 glossary.md，写全部 chunk_NNN.zh.md
& $PY $PIPE assemble --paper '论文目录' --name '短名'
& $PY $PIPE check --paper '论文目录' --name '短名'
# 修改顶层译文后单独刷新 HTML；之后还须检查块与译文是否同步
& $PY $PIPE render --source '论文目录/短名.zh.md'
```

切块保留完整段落、公式、HTML 表格和代码围栏，不在大表内部强切；超长单块允许超过目标长度。重新切块若发现旧译文或清单不符会拒绝覆盖；确认要重翻时另建切块目录并保存旧结果。

`assemble` 对每块检查图片引用顺序、公式内容、表格结构与数值、正文数值（公式以外）、列表项数量和脚注标记；验证源文件/块哈希，阻止源更改后继续拼接旧译文。检查可能把合理语言变化标为问题，先核对来源再调整译法，不跳过校验。图片路径以论文目录为基准，不强改为 `mineru/images/`。

`check` 检查核心产物、图片存在、分块与最终译文一致、结构一致及 HTML 内嵌图片。它不判定译文语义、章节范围是否正确，也不替代来源图表清单与浏览器视觉检查。缺原件时仍输出失败，交付按部分完成报告，不造空原件通过检查。
