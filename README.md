# Behavioral Policies for LLM Agents

### Agent Cognitive Profile（ACP）：把 agent 的执行策略从 prompt 层提升为可测量、可组合、可调度的计算资源

> 研究问题：当模型、工具、任务全部固定时，agent 的**执行策略**——读多少再动手、改多大范围、失败后是否换路——仍然强烈影响成本、时延、正确率与稳定性。我们把这一维度形式化为可控变量 **π = (E, T, A)**，通过记忆文件（CLAUDE.md / AGENTS.md）注入，受控地测量它对轨迹与结果的因果效应。

研究计划见 [`Proposal/proposal_v3.md`](Proposal/proposal_v3.md)（两篇制）。本项目是其**预实验与共享基础设施**：策略空间定义、注入管线、任务集、多维评分、能力卡雏形。

---

## 核心思想：三维行为策略空间 π = (E, T, A)

每根轴是一个**可操纵、可检验**的行为选择，绑定可测的轨迹签名——轴的合法性来自可测量，而非心理学命名。

| 轴 | v3 定义 | 两极 | 操纵检验指标 |
|----|---------|------|--------------|
| **E** Edit Scope | 修改范围预算 | 最小补丁 ↔ 自由重构 | diff 行数、触碰文件数 |
| **T** Pre-edit Information Gathering | 动手前信息搜集深度 | 立即动手 ↔ 先全局侦察 | 首次编辑前读取次数、首编辑前 token |
| **A** Feedback Control | 反馈控制环 | open-loop（按计划执行、末端验证）↔ closed-loop（每步测试、随反馈调向） | 测试运行频率、方案切换次数 |

三轴各取 0/1，共 **2³ = 8 种行为策略（认知画像）**。

## 八种认知画像

| ID | 向量 (E,T,A) | 名称 | 行为风格 |
|----|------|------|----------|
| `p000` | (0,0,0) | 保守实干家 Conservative Doer | 最小改动 · 立即动手 · 坚持首诊 |
| `p001` | (0,0,1) | 敏捷修补匠 Adaptive Fixer | 最小改动 · 立即动手 · 随反馈调整 |
| `p010` | (0,1,0) | 严谨执行者 Methodical Executor | 最小改动 · 先全局分析 · 坚持计划 |
| `p011` | (0,1,1) | 审慎调试者 Careful Debugger | 最小改动 · 先全局分析 · 假设驱动 |
| `p100` | (1,0,0) | 激进黑客 Aggressive Hacker | 自由重构 · 立即动手 · 坚持己见 |
| `p101` | (1,0,1) | 灵活探索者 Flexible Explorer | 自由重构 · 立即动手 · 快速试错 |
| `p110` | (1,1,0) | 完美架构师 Perfectionist Architect | 自由重构 · 先全局设计 · 坚持蓝图 |
| `p111` | (1,1,1) | 全面创新者 Full Innovator | 自由重构 · 先全局分析 · 随反馈演化 |

每个画像是**一束具体的行为指令**，不是人格标签——这正是本项目相对早期 MBTI-label 实验的关键修正：预实验已反复确认，单纯的人格标签（"你是 INTJ"）几乎不改变轨迹，效应必须来自可执行的行为化规则。

## 注入机制

记忆文件是注入行为策略的事实标准接口，被整个 agent 生态大量使用。本项目用一个确定性编译器把策略规则写进每个 run 的 `CLAUDE.md`：

```
profiles/*.yaml            8 份画像定义（向量 + 行为规则 + 风格锚）
   │  scripts/compile_profiles.py
   ▼
variants/*.md              编译出的 CLAUDE.md 变体（长度匹配）
   │  scripts/run_experiment.py  （写入 results/runs/<run_id>/workspace/CLAUDE.md）
   ▼
claude -p <prompt>         Claude Code 无头模式，按 stream-json 执行
```

`run_experiment.py` 对每个 `(task × variant × repetition)` 单元：拷贝任务 workspace → 写入对应画像的 CLAUDE.md → 跑 `claude -p` → 对隐藏测试判分 → 抽取行为指标 → 写 `record.json`。已完成的单元自动跳过，可安全中断续跑；运行顺序固定种子打乱，避免某画像系统性地更早执行。

## 任务集

`tasks/` 下 28 个自包含 Python SWE 任务，全部本地可跑、自动判分。按难度与考察点分层：

| 区段 | 类型 | 内容 |
|------|------|------|
| t01–t10 | clear / vague | 日期区间、LRU、CSV 健壮性、slugify、限流、展平、日志摘要、配置健壮性、联系人去重、CLI 打磨 |
| t11–t15 | hard（SWE-bench 风格） | ORM filter chain、config 深合并、DAG 调度器、模板转义注入、连接池 |
| t16–t19 | 性能 | 去重算法、缓冲区、内存缓存、并发数据竞争 |
| t20–t22 | 优化 | N+1 查询、deepcopy 滥用、排序键（cmp_to_key → heapq） |
| t23–t25, t28, t29 | 陷阱任务（multi 评分） | 货币浮点精度、线程池死锁、并发不变量、树栈溢出、缓存系统、优先级队列饥饿 |

陷阱任务在 `meta.json` 中带 `"grading": "multi"`，强制走多维评分路径。

## 多维度评分

二元 pass/fail 在本项目任务集上**完全失效**：218 次二元运行全部满分，区分度 0%。解法是 `scripts/grade_multi.py`，在隐藏测试全对的前提下按四个维度给连续分：

```
overall = 正确性 × 50% + 性能 × 20% + 改动量(minimality) × 15% + 质量 × 15%
```

- **minimality**（改动量）是主要区分来源——所有画像几乎都解对，但改动量差异巨大；
- **performance** 对性能/优化任务启用（超时阈值见 `meta.json` 的 `timeout_grade`）；
- 120 次多维运行全部产生连续分数（0.65–0.96 区间），区分度 100%。

## 预实验发现（338 次真实执行，已完成）

设计：2³ 因子（8 策略，行为化指令、长度匹配）× 17 个 Python SWE 任务（10 hard + 7 perf）× ≤3 重复；Claude Code 无头模式 × DeepSeek-V4-flash；隐藏测试部分分；同任务配对差 + 任务级 bootstrap 95% CI（10 000 次）。`*` = CI 不含 0。

- **F1 策略可控**：三轴均显著改变轨迹（T：+663 字符叙述*、+0.96 次动手前阅读*；E：+399*、+0.64*）；策略间叙述量差 2.9×、成本差 49%。
- **F2 成本–质量解耦**：E、T 显著增加成本（+$0.048*、+$0.083*/任务；+1.29*、+2.09* 轮），质量零或负回报——T 在 hard 任务 **−0.7pp***。核心机制假设 **H-M：质量瓶颈是已验证反馈的频率，不是推理长度**。
- **F3 closed-loop 是免费保险**：A 平均成本不变（−$0.005，ns），但截断失败尾部——t29 上 p010→p011 一个 bit +13pp（0.753→0.884）。**A 买的是最坏情况，不是均值**。
- **F4 任务–策略匹配（suggestive）**：区分任务的最优策略各不相同（t23/t24→p000、t25→p101、t29→p011/p001）；oracle 按任务选择：成本 −12%、质量 +0.3pp。证据强度警示：仅 4–5 个区分任务 × n=3，策略级 CI 大量重叠——这正是 Step 0 要解决的。
- **F5 测量天花板**：13/17 任务对策略零区分（12 个满分）。评测饱和是当前最大瓶颈，决定 Paper 1 基准的第一设计目标。

完整结果见 [`results/EXPERIMENT_RESULTS.md`](results/EXPERIMENT_RESULTS.md)；交互式可视化见 `results/profile_viz.html`（3D）与 `results/analysis_report.html`（按任务明细 + 性价比）。

## 快速开始

前置：已安装并登录 [Claude Code](https://docs.claude.com/en/docs/claude-code)（`claude` 命令可用），Python 3.10+。

```bash
pip install -r requirements.txt          # 只有 pytest

# 1) 编译画像：profiles/*.yaml → variants/*.md
python scripts/compile_profiles.py

# 2) 自检：验证任务集本身有效（不调用模型，不花钱）
python scripts/selftest.py

# 3) 冒烟测试：1 任务 × 2 画像 × 1 次 = 2 个 run
python scripts/run_experiment.py \
  --tasks t23_currency_precision \
  --variants p000_conservative_doer,p111_full_innovator --reps 1

# 4) 正式：4 个区分任务 × 8 画像 × 3 次（可中断，自动断点续跑）
python scripts/run_experiment.py \
  --tasks t23_currency_precision,t24_threadpool_deadlock,t25_tree_overflow,t29_priority_queue \
  --reps 3 --parallel 2

# 5) 分析：生成 results/report.md
python scripts/analyze.py
```

**换模型 / 换后端**：`run_experiment.py` 是 harness 无关的，`--model` 直接透传给 `claude --model`。本项目预实验用 DeepSeek-V4-flash（Infini-AI 云）：

```bash
export ANTHROPIC_BASE_URL=https://cloud.infini-ai.com/maas
export ANTHROPIC_AUTH_TOKEN=<your-token>        # 切勿提交到仓库
python scripts/run_experiment.py --model deepseek-v4-flash ...
```

先用便宜模型探信号，有信号再换大模型复跑。

## 判读规则（重要，按顺序）

1. **先看行为指标**：行为列在画像间是否分离？例如 T=1 画像的叙述字数、动手前阅读应明显高于 T=0；A=1 的测试运行频率应更高。**行为都没变 ⇒ 操纵无效，结果差异都是噪声**——应回去加强指令措辞，而不是加大样本。
2. **再看同任务配对差 bootstrap 95% CI**：排除 0 才算有信号；跨 0 只说明效应小于当前检测力，不是"无效应"的证明。
3. **对照 F2 看 cost–quality 解耦**，对照 F3 看最坏情况（不是均值）。
4. **多维评分是必须的**：二元评分在本任务集上区分度为 0，任何二元结论都不可信。

## 注意事项 / 已知坑

- **全局记忆混淆**：Claude Code 还会加载 `~/.claude/CLAUDE.md`。跑实验期间请将其清空或对所有条件保持恒定（最好清空）。
- **无头模式没有交互**：agent 提问不会有人回答。行为指令一律写成"陈述假设后继续"，不要写出会阻塞的指令。
- **权限**：默认用 `--allowedTools` 白名单。`--yolo` 切换为 `--dangerously-skip-permissions`，只在容器/虚拟机里用。
- **不要把 `tests_hidden/` 或 `solution/` 拷进 workspace**，agent 会看到答案。runner 只拷贝 `workspace/`，判分在临时目录做，visible 回归测试用任务原始副本重跑，防作弊已处理。
- **API key 勿入库**：所有 token 通过环境变量注入，仓库内不应出现任何明文密钥。
- **统计功效**：338 次运行对二元结论功效仍低，所以判分用部分分、比较用同任务配对差。想收窄 CI：先加 `--reps`，再加任务数。
- 修改/新增任务后必须重跑 `python scripts/selftest.py`（保证 solution=1.0、基线<1.0，否则任务无区分度）。
- 画像变体请保持长度接近，避免"上下文更长"混淆成本。

## 目录结构

```
profiles/                8 份画像定义 (yaml) + dimensions.yaml（三轴定义）
variants/                编译出的 CLAUDE.md 变体（8 份，长度匹配）
tasks/<id>/
  workspace/             给 agent 的初始代码（含部分可见测试）
  prompt.txt             任务指令（通过 claude -p 传入）
  tests_hidden/          隐藏判分测试（agent 永远看不到）
  solution/              参考解（仅供 selftest 验证测试有效性）
  meta.json              类型、隐藏测试数、grading=multi 等
scripts/
  compile_profiles.py    yaml → CLAUDE.md 编译器
  run_experiment.py      跑实验（可断点续跑、并发、乱序）
  grade.py               二元判分（junitxml 解析，部分分）
  grade_multi.py         多维判分（正确性+性能+改动量+质量）
  behavior_metrics.py    轨迹行为指标（操纵检验用）
  analyze.py             配对差 + bootstrap CI + 行为表 → results/report.md
  selftest.py            任务集自检（不花钱）
results/
  runs/<run_id>/         每个 run 的 workspace、transcript.jsonl、record.json
  EXPERIMENT_RESULTS.md  完整结果文档
  profile_viz.html       3D 交互式可视化（性能 / 成本 / 加权）
  analysis_report.html   按任务明细 + 性价比分析
Proposal/
  proposal_v3.md         两篇制研究计划书
```

## 研究计划（两篇制，见 proposal_v3.md）

- **Paper 1 — 测量与解释**：*Behavioral Policies for LLM Agents: Measuring Execution-Strategy Diversity and Its Routing Headroom*。策略空间（三种实现层级：自然语言 / 结构化配置 / harness 强制，排除 wording effect）+ 因果测量（AgentPolicyBench-Atomic，双对照，跨 3 档模型）+ 机制干预（强制反馈纪律，验证 H-M）+ 能力卡 + 离线 oracle headroom 分析。
- **Paper 2 — 构建与调度**：*DecompBench: Capability-Aware Decomposition and Policy Routing for LLM Agent Teams*。能力卡诱导式选材拼装的可拆分任务基准 + 能力感知 manager（L0 查表 → L1 预测式路由 → L2 contextual bandit → L3 失败升级链）。依赖 Paper 1 的能力卡。
- **Step 0 门槛实验（写作前，~$150）**：把 F4 的 4 个区分任务加厚到 n=12，按预注册判据（G1/G2/G3）决定走"两篇制全速"、"重心移向解耦+机制+默认策略"还是"收缩为单篇"。这是全计划风险回报比最高的 $150。

## 与相关工作的边界

与 Mixture-of-Agents（Wang et al., 2024，多 LLM 分层聚合）划清——本项目的 expert 是**同一模型的不同行为策略**、路由基于**实测能力卡**而非学习聚合；MoE 只作类比段落。详细文献定位见 proposal §1、§7 与参考文献。

---

*统计标准全程：同任务配对、任务级 bootstrap 10 000 次、Holm 校正、均值/最坏情况/方差三列报告。所有实验预注册，基准、能力卡、全部轨迹（含 338 条预实验）与分析脚本将随论文开源。*
