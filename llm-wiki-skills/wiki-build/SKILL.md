---
name: wiki-build
description: "从零搭建或迁移一套 llm-wiki 式个人知识库（sources 原文 + wiki 编译层 + 逐字证据校验）。当用户说「搭个知识库」「把笔记迁过来建库」「换个库重做」「这套流程用到新库」时使用。运行期入库/查询用 ingest / wiki-query，本 skill 只管从无到有。"
---

# wiki-build — 从零搭一座知识库

这个 skill 记录的是**施工过程**，不是日常使用。库搭好后的入库、查询、沉淀分别由 `ingest` / `wiki-query` / `knowledge-capture` 负责。

## 先看目标，再动手

建成后长这样：

```
raw/docs/<笔记本>/      原文快照（一字不改，改动要留 amended）
wiki/concepts/                  N 个概念页（定义+性质+边界+出处）
wiki/summaries/                  每篇 source 一个页（摘要+断言+证据）
wiki/analysis/                  问答沉淀
wiki/_templates/                 7 个模板（concept/entity/method/metric + doc/digest/topic）
wiki/topic-map.md            分类入口
index.md                   自动生成
agent.md                   编译规则全本
_tools/                    工具脚本（放在库外）
```

**核心不是"整理好"，而是"每条断言都能追回原文逐字片段"**。没有这条，库就只是个二手摘要集。

## 六个阶段

### 阶段 1 摸底——先量，别急动手

```bash
# 每个来源目录多少篇、多少字、多少图
python queue.py            # 未编译清单，按分类分组
python coverage.py         # 覆盖率
```

**要看三个数**：总篇数、`content_status` 非 ok 的数量、图片引用总数。这三个数决定后面工作量。

**这一步最容易犯的错**：看到「233 篇读不出」就开始逐篇手修。正确做法是先查**为什么读不出**——多半是同一个根因。

### 阶段 2 补字——修复旧库残缺

对着新旧两份导出逐字比对，只补真正丢的：

```bash
python reconcile.py        # 对账：哪些库内有、新导出没有
python patch_3places.py    # 补指定几处
```

**判据**：只有「新导出里确实有这段、旧库缺这段」才补。不要凭印象补。

### 阶段 3 换库——重新导出，而不是修补

旧库残缺过半时，**重新导出比逐篇修省力得多**。

```bash
python note2md.py          # .note（HTML 富文本）→ md
python mindmap2md.py       # .mindmap（JSON 树）→ md
python build_sources.py    # 合并新导出正文 + 旧 front-matter
python finalize_names.py   # 文件名规范化
```

`build_sources.py` 是关键：新导出有正文但缺元信息，旧库有元信息但正文残缺，**合并两者**。

### 阶段 4 图片统一

```bash
python migrate_images.py   # 收到 attachments/docs/，md5 去重改名
python fetch_remote_imgs.py # 远程图下载落地
python verify_img_md5.py   # 校验：引用集合 vs 文件集合
```

**验收**：`图片引用缺失 0 处`。这一条不能松，否则后面所有图片都是死链。

### 阶段 5 编译

先做**金标准**：挑 1 篇最典型的，走完整八步（见 `ingest`），人工过一遍。调准了再批量。

```bash
python batch_doc.py batch_1.json    # 批量生成，一次几十篇
python compile_image_notes.py       # 特例：纯图笔记
python compile_short_notes.py       # 特例：极短文本
```

**批量必须落盘**：算完一批就写文件，别攒到最后。中断会全丢。

### 阶段 6 校验与收口

```bash
python check_claims.py --all      # 全库断言逐字校验
python rebuild_index_full.py      # 从头重建 index
python verify_kb.py               # 断链/孤岛/图片
python gen_pending_log.py         # 四数量待办日志
```

**必须全绿才算完**：断言 0 不匹配、断链 0、图片缺失 0、孤岛只剩凭据页。

## 八类问题与解法

| 问题 | 根因 | 解法 |
|---|---|---|
| 大批笔记正文空白 | 正文是图片或 HTML 富文本，API 只返回标题 | 换导出方式；HTML 转 md；纯图的走图片页 |
| `.note` 文件没转 | 导出工具只认 XML，遇到 HTML 原样留存 | 自写 HTML→md 转换器 |
| `.mindmap` 没转 | 是 JSON 树结构，不是文本 | 按 `parentid` 建树，输出层级大纲 |
| 表格单元格文字截断 | 单元格内有换行，导出只留第一行 | 与另一份导出逐字比对后补回 |
| 图片路径两套并存 | 新旧导出路径规则不同 | 统一进 `attachments/docs/`，md5 去重改名 |
| 部分图片是第三方图床 | 原站已失效 | 能下的下载落地；下不来的保留链接并标注失效，**不要删** |
| index 列表越跑越长 | 正则替换列表被空行打断，只替换前半段 | 改从头生成，不基于旧文件 |
| 个别页正文真空 | 导出阶段就没取到，源是 0 字节 | 先排查（库内/导出源/`.note` 三层），确证后登记待办，**不要建空壳页** |

## 工具地图

| 阶段 | 脚本 |
|---|---|
| 摸底 | `queue.py` `coverage.py` `classify_pending.py` `scan_pending.py` |
| 补字 | `reconcile.py` `patch_3places.py` `build_sources.py` |
| 换库 | `note2md.py` `mindmap2md.py` `finalize_names.py` |
| 图片 | `migrate_images.py` `fetch_remote_imgs.py` `verify_img_md5.py` `fix_img_paths.py` |
| 编译 | `batch_doc.py` `compile_image_notes.py` `compile_short_notes.py` |
| 校验 | `check_claims.py` `rebuild_index_full.py` `verify_kb.py` `gen_pending_log.py` `health_check.py` |

诊断类脚本（`analyze_*` `diag_*` `test_*` `list_*` `stats_*`）是一次性的，迁移时不必带。

## 迁移到新库要改什么

1. **路径**：所有脚本顶头的 `KB = r"D:/workspace/ai_kb_base/second-brain"`，改成新库绝对路径
2. **来源结构**：`raw/docs/<笔记本名>/` 的层级按新来源调整，但**保持一层笔记本名**，别拍平
3. **模板**：`wiki/_templates/` 七个模板里的字段可保留，正文措辞按新领域调；四类知识节点的段名不同是刻意的（各自被追问的问题不同），不要合并回一个通用模板
4. **概念门槛**：本库用的是「≥2 篇涉及 或 作前置」，新库可按密度调整
5. **`agent.md`**：编译规则全本，是给人和 agent 共同看的规范，必须随库走

## 验收标准

| 项 | 标准 |
|---|---|
| 断言校验 | 0 不匹配（`high` 必须逐字命中原文） |
| 断链 | 0（模板占位符除外） |
| 图片引用缺失 | 0 |
| 孤岛 | 只剩凭据屏蔽页（设计如此） |
| 概念页 | 每张都有「关系」段 ≥2 条出链、有「出处」段 |
| 待办日志 | 能用脚本重跑刷新，数字不手改 |

## 三条最重要的经验

1. **先量再动**。233 篇「读不出」看着要逐篇修，实际是一个根因。量完再决定，能省掉一半工作量。
2. **批量必须用生成器 + 落盘**。靠手工一篇篇写，几十篇就断了；靠脚本批量，几百篇也能一轮完成。但算完一批立刻写文件。
3. **校验不通过就不要交付**。「差不多对上」的断言等于没有证据，比不写还糟——它让人以为有依据。

## 这套 skill 放在哪、怎么改

两个路径是**同一个目录**——`llm-wiki-skills` 是一个 junction（目录联接），指向 `.workbuddy\skills`：

| 路径 | 本质 | 谁在用 |
|---|---|---|
| `D:\workspace\ai_kb_base\.workbuddy\skills\` | 真实目录 | 系统从这里加载 |
| `D:\workspace\ai_kb_base\llm-wiki-skills\` | Junction → 上面这个 | 人从这里找和编辑 |

**改哪边都一样**，因为是同一个物理文件。不存在同步问题，也不需要维护两份。

### 改完怎么算生效

**改完要新开会话**。skill 清单是会话启动那一刻的快照，同一会话里改完立刻问「为什么没生效」，答案是必然的。工作区要选 `D:\workspace\ai_kb_base`。

### 什么时候需要体检

只有一种情况会出事：**链接被某个工具展开成了真实目录**。备份还原、资源管理器拖拽、整个项目复制，都会干这事。一旦发生，两个路径变成两份独立文件，改一边另一边永远不变，**而且不报任何错**。

怀疑的时候跑一条：

```bash
python _tools/sync_skills.py --check
```

- 输出 `[OK] 链接模式生效` → 正常，继续干活
- 输出 `[WARN] 链接已断` → 别急着同步文件，先把不一致的内容人工合并，再重建链接：

```powershell
Remove-Item D:\workspace\ai_kb_base\llm-wiki-skills -Recurse -Force
New-Item -ItemType Junction -Path D:\workspace\ai_kb_base\llm-wiki-skills -Target D:\workspace\ai_kb_base\.workbuddy\skills
```

修复永远选「重建链接」，不选「同步文件」。同步只抹平当次的差异，结构本身还是断的，下次照样分裂。

脚本不进 skill 目录。所有施工脚本统一放 `_tools\`，skill 目录里只留 `SKILL.md`——skill 是给人看流程的，工具是给机器跑的，混在一起两头都不清爽。
