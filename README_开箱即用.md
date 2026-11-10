# 开箱即用 · 个人知识库

解压后按下面三步走，五分钟能用。

---

## 第一步：确认环境

需要 **Python 3.10+**。检查：

```bash
python --version
```

不需要安装任何第三方库——这套工具链是零依赖设计的，换机器直接跑。

---

## 第二步：跑一次体检

```bash
cd /d <你解压到的路径>
python _tools/weekly_audit.py
```

看到类似这样的输出就说明环境通了：

```
[黄] 周检完成
  本体 error 0 / warn 0 · 断言 841 通过 0 不匹配 · 断链 0 · 图片缺失 0
  覆盖 95.7%（311/322） · 原文变更 0 · 沉淀 8 篇
```

四项核心读数应该是：

| 项 | 期望值 |
|---|---|
| 断言逐字通过 | 841 通过 / 0 不匹配 |
| 本体约束 | error 0 / warn 0 |
| 断链 | 0 |
| 图片缺失 | 0 |

如果对不上，先看 `logs/weekly/` 下最新周报，再翻 `kb-ops` 技能里的「读数异常先怀疑脚本」那一节。

---

## 第三步：装六个技能（可选，但强烈建议）

技能在 `.workbuddy/skills/` 下，共六个：

| 技能 | 干什么 |
|---|---|
| `wiki-build` | 从零搭一套新库 |
| `ingest` | 把资料编译进库 |
| `wiki-query` | 从库里检索回答 |
| `knowledge-capture` | 把结论沉淀下来 |
| `knowledge-recall` | 查某个问题是否答过 |
| `kb-ops` | 体检、校验、同步、排障 |

**安装位置**（必须是用户级，装到项目目录永远读不到）：

```
C:\Users\<你的用户名>\.workbuddy\skills\
```

把六个目录整体复制过去。**装完要新开一个会话**，技能清单是会话启动时的快照，老会话看不见新装的。

验证：新会话里问「你有哪些技能」，能看到 `kb-ops` 就成。

---

## 目录结构

```
知识库根目录/
├── second-brain/          库本体
│   ├── raw/               ① 原文快照，只读，319 篇
│   ├── wiki/              ② 编译产物
│   │   ├── summaries/     文档页，每个原文一页（311 篇）
│   │   ├── concepts/      概念页（103 个知识节点）
│   │   ├── entities/      实体页
│   │   ├── methods/       方法页
│   │   ├── metrics/       指标页
│   │   ├── analysis/      问答沉淀
│   │   └── topic-map.md   分类入口
│   ├── index.md           全量目录（脚本生成，别手改）
│   ├── ontology.json      本体：4 类 / 16 关系 / 12 约束
│   └── agent.md           规则全本（697 行）
├── _tools/                122+ 个脚本
├── logs/                  处理日志 + 每周周报
├── attachments/           图片，按 md5 去重命名
├── PROMPTS.md             日常指令速查
└── 知识库搭建与运维教程.md  从零到有的完整记录
```

---

## 四个最常用的命令

```bash
# 体检
python _tools/weekly_audit.py

# 断言校验（每条结论能不能追回原文）
python _tools/check_claims.py --all

# 断链与图片
python _tools/verify_kb.py

# 重建索引
python _tools/rebuild_index_full.py
```

---

## 重新接上 GitHub（可选）

这个包**不含 `.git`**，是干净的可分发版本。要接远程：

```bash
git init -b main
git config user.name "你的名字"
git config user.email "你的邮箱"
git config core.autocrlf false      # ← 必须，否则换行会被转换
git add -A
git commit -m "初始提交"
git remote add origin <你的仓库地址>
git push -u origin main
```

`.gitattributes` 已经设了 `* -text`，别改——本库的断言是逐字比对，换行一变就可能误判。

**推送前先跑安全扫描**：

```bash
python _tools/scan_sensitive.py
```

返回 1 就停下，说明有凭据没清干净。

---

## 一件需要注意的事：有 14 篇原文不在包里

含密码、密钥、服务端 UUID 的原文**按安全原则排除**了（清单见 `.gitignore`）。

具体是：

- 4 篇账号密码笔记（steemit / 自媒体 / google / 个人账号密码）
- 8 篇技术教程，正文夹带真实数据库密码或连接串
- 2 篇含 v2ray 服务端配置与凭据

**如果你需要它们**，从原机器的 `second-brain/raw/docs/personal-assets/` 下单独拷。缺了它们不影响库能跑，只影响那 14 篇的原文检索。

---

## 想从零搭一套新的？

不要改这个包，看 `知识库搭建与运维教程.md`，或者直接用 `wiki-build` 技能。

这个包是**已经建好的库**，不是模板。拿它当模板会把别人的分类体系一起带走。

---

## 出问题看哪里

| 症状 | 先查 |
|---|---|
| 体检读数异常 | `logs/weekly/` 最新周报 |
| 断链不为 0 | 先分示例还是真断链，别手补 |
| 页面变成 CRLF | `check_spec.py` 会报，批量转 LF |
| 有空白页面 | 查 `raw/` 是不是空壳，空壳不建页 |
| 脚本报错 | 先怀疑脚本，再怀疑数据 |

规则细节以 `second-brain/agent.md` 为准。这份 README 只讲怎么起步。
