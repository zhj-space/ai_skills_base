---
name: kb-ops
description: 知识库运维与质量保障。当用户说「体检」「查一下库有没有问题」「跑一遍校验」「同步到 GitHub」「周检」「规范检查」「断链了」「清理空壳」「库坏了」时使用。只管库健不健康、改动能不能推出去，不写知识内容。适用于 D:\workspace\ai_kb_base 这个库。
---

# kb-ops — 运维与质量保障

**只回答两个问题：库健康吗？改动能推出去吗？**

不写知识内容（那是 `ingest` 和 `knowledge-capture` 的事），不搭库（那是 `wiki-build`）。

## 开工前必读

1. `D:\workspace\ai_kb_base\second-brain\agent.md` —— 规则全本
2. 本 skill 只讲**调度顺序和判定标准**，不重复规则

## 七个校验器，各管一段

| 脚本 | 管什么 | 什么时候跑 | 判定 |
|---|---|---|---|
| `check_claims.py --all` | 断言有没有抄对原文 | 每次入库后 | 不匹配必须 0 |
| `check_ontology.py` | 类型与关系合不合法 | 改类型/关系后 | error 必须 0 |
| `check_spec.py` | 格式与骨架符不符合规范 | 改模板/批量生成后 | ERROR 必须 0 |
| `verify_kb.py` | 断链、孤岛、图片缺失 | 每次入库后 | 断链 0、图片缺失 0 |
| `weekly_audit.py` | 七项汇总，出周报 | 每周一 | 看趋势不看单点 |
| `recompile.py` | 原文变了但没重编译 | 改过 `raw/` 后 | 已变必须 0 |
| `scan_sensitive.py` | 推送前敏感扫描 | **每次 push 前** | BLOCK 必须 0 |

一条命令跑全套：

```bash
cd /d D:\workspace\ai_kb_base && \
python _tools/check_claims.py --all && \
python _tools/check_ontology.py && \
python _tools/check_spec.py && \
python _tools/verify_kb.py
```

## 三个常见故障

### ① 断链不为 0

先分清是示例还是真断链。`verify_kb.py` **已经跳过代码块和反引号内的 `[[xx]]`**，所以它能报出来的基本是真的。

排查顺序：

1. 是不是凭据屏蔽页被谁加了链接（那些页**保持孤岛是对的**）
2. 是不是模板占位（模板目录已排除，但可能有人复制到别处）
3. 真断链 → 改目标页命名，或去掉双括号

**不许手工补链接**。手补会被下次重跑覆盖，而且掩盖了命名错误。

### ② CRLF 污染

现象：`check_spec.py` 报「换行符是 CRLF，本库约定 LF」。

成因几乎都是**非本工具链生成的页面**——别的 AI 会话写入、Windows 编辑器保存、复制粘贴。

处理：

```bash
python -c "
from pathlib import Path
for p in Path('second-brain/wiki').rglob('*.md'):
    b = p.read_bytes()
    if b'\r\n' in b: p.write_bytes(b.replace(b'\r\n', b'\n'))
"
```

**不要指望 git 修**：`.gitattributes` 设了 `* -text`，这是刻意的——本库断言逐字比对，换行一变就可能误判。

### ③ 空壳原文

现象：`raw/` 里某篇只有 frontmatter + 标题，`word_count: 0`。

处理：`_tools/fix_empty_sources.py` 把 `content_status` 改成 `empty` 并留 note。

**禁止为它生成文档页。** 空壳页会把 `wiki/` 淹成一片空白，真内容反被埋掉。

## Git 同步：安全闸在前

顺序**不可颠倒**：

```bash
python _tools/scan_sensitive.py    # 退出码 1 就停，什么都别做
git add -A
git commit -m "入库：xxx"
git push
```

### 凭据处理三条原则

| 情况 | 处理 |
|---|---|
| `raw/` 原文含密码/密钥/UUID | **排除出版本库**，本地保留（`.gitignore`） |
| wiki 文档页必须含示例 | **遮蔽**后上传（`build_redacted_doc.py` 的做法） |
| 凭据已经被推上去过 | 重建仓库 + 强推（仅当历史只在本地时） |

**最容易漏的三种写法**（都真踩过）：

- `pwd` 后跟中文冒号再加明文（旧规则只认 ASCII 冒号，静默漏报）
- 账号字段里塞邮箱（「账号」加全角冒号，值是邮箱地址）
- 配置里 `id` 字段放 UUID（v2ray/vmess 服务端凭据，原文注明「也是密码」）

**文件名干净 ≠ 内容干净。** 路径规则挡不住内容泄露，内容扫描也必须过。

## 本体维护

改 `ontology.json` 之后必须做三件事：

1. `python _tools/check_ontology.py` —— 12 条约束要全过
2. `python _tools/selftest_ontology.py` —— 注入了 12 类错误，必须 12/12 触发
3. 同步改 `agent.md` 第四·五节 —— 否则两份文档漂移，而**错的永远是散文那份**（JSON 每次都在被读，散文没人验证）

## 严格不做的事

| 禁止 | 原因 |
|---|---|
| 手工补断链 | 会被下次重跑覆盖，且掩盖命名错误 |
| 跳过 `scan_sensitive` 直接 push | 凭据上云，收不回来 |
| 在 `wiki/` 下跑正则批量替换 | 会误伤 frontmatter 和证据引文 |
| 为读不出内容的原文建空壳页 | 淹没真实内容 |
| 自己猜校验器的口径 | 读数异常时先查脚本，别先改数据 |

## 交付时说什么

不要只说「体检完了」。要说：

- **五项读数**：断言 X 通过 Y 不匹配 · 本体 error/warn · 断链 · 规范 ERROR · 覆盖率
- **修了什么**：具体文件 + 原因（没修就说没修）
- **有没有噪音**：WARN 多少条、是什么性质、为什么不阻断
- **同步结果**：推送成功与否，安全闸是否触发
- **剩下的缺口**：还没解决的问题，写清不做的后果

## 一个判断原则

**读数异常时，先怀疑脚本，再怀疑数据。**

这个库踩过的坑里，有一半是「校验器自己的 bug」：正则被 shell 吃掉、中文路径被转义、CRLF 让正则失效、规则太严把历史遗留全报成 error。

一个一上来报 348 个 error 的检查等于没检查。**能区分噪音和信号的检查器才有用。**
