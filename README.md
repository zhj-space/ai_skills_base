# ai_skills_base

**Skill 合集仓库。** 这里存放的是可以直接装进 AI 客户端使用的技能包（Skill），每个技能对应一类可复用的工作流，而不是示例代码或演示项目。

当前收录：**个人知识库技能组**（llm-wiki-skills）。

---

## 本次更新内容

本次提交为个人知识库（Personal Knowledge Base / llm-wiki）技能组，共 6 个技能 + 1 套零依赖工具链。

### 六个技能

| 技能 | 职责 | 典型触发语 |
|---|---|---|
| `wiki-build` | 从零搭建或迁移一套知识库（施工期） | 搭个知识库 / 把笔记迁过来建库 |
| `ingest` | 把原始资料编译成 wiki 页面（写入期） | 把这篇入库 / 更新知识库 |
| `wiki-query` | 只读检索并回答问题（运行期） | 库里关于 X 怎么说 |
| `knowledge-capture` | 把有推理链的结论沉淀成分析页 | 沉淀一下 / 以后别再重算 |
| `knowledge-recall` | 回答前先查是否已分析过 | 我之前问过这个吗 |
| `kb-ops` | 体检、校验、同步、排障 | 跑一遍体检 / 同步到 GitHub |

设计上按生命周期拆分职责：**搭库 → 入库 → 查询 → 沉淀 → 回查 → 运维**。每个技能只做一件事，互相之间靠"先查再算"的顺序衔接，避免同一个问题被反复重推、同一份资料被重复编译。

### 工具链 `_tools/`

约 150 个 Python 脚本，**零第三方依赖**，Python 3.10+ 直接运行。主要分四类：

- **体检类**：`weekly_audit.py`（周检总入口）、`health_check.py`、`verify_kb.py`、`check_spec.py`
- **编译类**：`note2md.py`、`compile_short_notes.py`、`html2md_generic.py`、`build_concepts*.py`
- **校验类**：`verify_ev.py`（逐字证据比对）、`verify_bilink.py`（双链）、`check_coverage.py`
- **安全类**：`scan_sensitive.py`（推送前凭据扫描）

### 文档

- `README_开箱即用.md` —— 三步上手：确认环境、跑体检、装技能
- `PROMPTS.md` —— 提示语速查表，每条标注触发哪个技能、产出什么

---

## 目录结构

```
ai_skills_base/
├── README.md                  # 本文件，仓库总览
├── PROMPTS.md                 # 提示语速查
├── README_开箱即用.md          # 快速上手指引
├── llm-wiki-skills/           # 本次更新：个人知识库技能组
│   ├── wiki-build/SKILL.md
│   ├── ingest/SKILL.md
│   ├── wiki-query/SKILL.md
│   ├── knowledge-capture/SKILL.md
│   ├── knowledge-recall/SKILL.md
│   └── kb-ops/SKILL.md
└── _tools/                    # 零依赖工具链（体检 / 编译 / 校验 / 安全扫描）
```

---

## 快速开始

**1. 跑一次体检，确认环境可用**

```bash
python _tools/weekly_audit.py
```

期望读数：断言逐字通过 841 / 0 不匹配，本体约束 error 0 / warn 0，断链 0，图片缺失 0。

**2. 安装技能**

技能必须装到**用户级**目录，装进项目目录通常读不到：

```
~/.workbuddy/skills/<skill-name>/SKILL.md
```

本项目内即 `llm-wiki-skills/` 下的六个子目录，逐个复制过去即可。

**3. 开始用**

按 `PROMPTS.md` 里的短句直接说，例如「把这篇入库：<路径>」「库里关于 X 怎么说」。

---

## 使用约定

- **技能 = 单一职责**。每个 SKILL.md 对应一个阶段，不要在一个技能里混写入与查询。
- **规则集中**。详细规则写在知识库的 `agent.md`，SKILL.md 只讲调度顺序和落地步骤，避免两份规则打架。
- **逐字比对**。校验脚本做的是原文与页面的逐字断言比对，因此 `.gitattributes` 设为 `* -text`，换行符变化会导致误判，请勿修改。
- **推送前先扫描**。`python _tools/scan_sensitive.py` 返回 1 即停止，说明有凭据未清理。

---

## 安全说明

含密码、密钥、服务端配置的原始资料按安全原则**未纳入本仓库**。若你在复用时发现凭据残留，请直接以 Issue 或 PR 提示，不要在本仓库中提交真实凭据。

---

## 更新日志

| 日期 | 内容 |
|---|---|
| 2026-11-11 | 首次提交：新增个人知识库技能组（6 个技能）+ `_tools` 工具链 + 使用文档 |

---

## License

未声明许可证。如需二次分发或商用，请先联系仓库所有者。
