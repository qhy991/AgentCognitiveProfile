# 研究计划书 v3（两篇制）

# Behavioral Policies for LLM Agents

## 把 agent 的行为策略从 prompt 层提升为可测量、可组合、可调度的计算资源

**三层体系：Behavioral Policy Space → Capability Card → Capability-Aware Routing**（见 architecture_figure.svg）

---

## 0. v3 相对 v2 的变化（一页速览）

1. **由研究计划收敛为两篇论文**：Paper 1「测量与解释」（策略空间 + 因果 + 机制 + 能力卡 + 离线路由空间），Paper 2「构建与调度」（DecompBench + Manager）。Paper 1 不做任何在线系统——路由价值以**离线 oracle headroom 分析**呈现，作为 Paper 2 的动机。
2. **新增 Step 0 门槛实验（写作之前）**：F4（任务–策略匹配）目前只有 n=3 的 suggestive 证据，是两篇论文共同的地基。先花 ~$150 把 4 个区分任务加厚到 n=10–15，按预注册判据决定走"两篇制"还是收缩为"解耦+机制"单篇。
3. **术语修订**：A 轴改名 **Feedback Control（open-loop ↔ closed-loop）**；T 轴定义收窄为**动手前信息搜集深度**（去掉 "thinking" 的心理学语义）；E 轴（修改范围）不变。构念与 338 次预实验数据完全连续，仅词汇升级。
4. **合并"措辞鲁棒性"与"policy 实现层级"为同一实验**：每个策略以三种形式实现——自然语言 / 结构化配置 / harness 强制——三者效应一致则证明是 policy 而非 wording；harness 版同时就是机制干预臂。不使用 "compiler" 措辞（避免对确定性语义的过度承诺；遵从度本身是实测对象）。
5. **DecompBench 异质性改为能力卡诱导式选材**（从实测最优策略不同的原子任务反向拼装 DAG），"全部子任务同一最优"的退化情形设为对照组；任务构成 80% 组合构造 + 20% 真实项目级任务。
6. **定位边界**：与 Mixture-of-Agents（Wang et al., 2024，多 LLM 分层聚合）划清——我们的 expert 是同一模型的不同行为策略、路由基于实测能力卡而非学习聚合；MoE 只作类比段落，不作系统命名。

---

## 1. 核心主张与背景

当模型、工具、任务全部固定时，agent 的**执行策略**——读多少再动手、改多大范围、失败后是否换路——仍然强烈影响成本、时延、正确率与稳定性。这一维度被现有研究忽视：模型能力路线（test-time scaling）、框架路线（ReAct/Reflexion/SWE-agent）、自动设计路线（ADAS/AFlow）都不把"同一配置下的行为策略"作为受控变量。记忆文件（AGENTS.md/CLAUDE.md）是注入此类策略的事实标准接口，被整个生态大量使用，却几乎没有受控因果证据。

我们把行为策略形式化为 **π = (E, T, A)**：

| 轴 | 定义（v3 修订） | 两极 | 操纵检验指标 |
|---|---|---|---|
| **E** Edit Scope | 修改范围预算 | 最小补丁 ↔ 自由重构 | diff 行数、触碰文件数 |
| **T** Pre-edit Information Gathering | 动手前信息搜集深度 | 立即动手 ↔ 先全局侦察 | 首次编辑前读取次数、首编辑前 token |
| **A** Feedback Control | 反馈控制环 | open-loop（按计划执行、末端验证） ↔ closed-loop（每步测试、随反馈调向） | 测试运行频率、方案切换次数 |

每根轴绑定可测的轨迹签名——轴的合法性来自可操纵、可检验，而非命名。

**单 agent 的天花板使该维度进一步升值**：SWE-Marathon（2026）显示中位 2347 步的真实长程任务上最强单 agent 解决率 ≤30%，长上下文出现行为退化。规模化必然走向"拆分 + 分派"，而分派的前提是 worker 异质性可测量。**同一模型 + 不同策略**是最干净的异质性来源：成本一份文本文件，归因无混杂。

---

## 2. 预实验证据（338 次真实执行，已完成）

设计：2³ 因子（8 策略，行为化指令、长度匹配）× 17 个 Python SWE 任务（10 hard + 7 perf）× ≤3 重复；Claude Code 无头模式 × DeepSeek-V4-flash；隐藏测试部分分；同任务配对差 + 任务级 bootstrap 95% CI（10 000 次）。\* = CI 不含 0。

- **F1 策略可控**：三轴均显著改变轨迹（T：+663 字符叙述\*、+0.96 次动手前阅读\*；E：+399\*、+0.64\*）；策略间叙述量差 2.9×、成本差 49%。
- **F2 成本–质量解耦**：E、T 显著增加成本（+$0.048\*、+$0.083\*/任务；+1.29\*、+2.09\* 轮），质量零或负回报——T 在 hard 任务 **−0.7pp\***。机制线索：T 显著减少测试运行（−0.41 次\*）；区分任务内测试次数与质量正相关（r=+0.18）、叙述量负相关（r=−0.50）。→ 核心机制假设 **H-M：质量瓶颈是已验证反馈的频率，不是推理长度**。
- **F3 closed-loop 是免费保险**：A 平均成本不变（−$0.005，ns），但截断失败尾部——t29 上 p010→p011 一个 bit +13pp（0.753→0.884）；全局最坏单次 0.65→0.77。**A 买的是最坏情况，不是均值**。
- **F4 任务–策略匹配（suggestive）**：区分任务的最优策略各不相同（t23/t24→p000、t25→p101、t29→p011/p001）；oracle 按任务选择：成本 −12%、质量 +0.3pp。**证据强度警示：仅 4–5 个区分任务 × n=3，策略级 CI 大量重叠——这正是 Step 0 要解决的。**
- **F5 测量天花板**：13/17 任务对策略零区分（12 个满分）。评测饱和是当前最大瓶颈，决定 Paper 1 基准的第一设计目标。

局限（v3 修复对象）：单模型、无空白对照、机制观察性、多维评分仅子集覆盖。

---

## 3. Step 0 — 门槛实验：F4 加厚（写作前，~1 周，~$150）

**动机**：F4 是 Paper 2 的存在性前提（"若存在全能策略，manager 无意义"），也影响 Paper 1 的叙事重心。当前证据不足以承重。

**设计**：4 个区分任务（t23/t24/t25/t29）× 8 策略 × 加厚至 n=12（新增 ~290 runs）；同 harness 同模型；预注册判据。

**判据与分支**：
- **G1 通过**（≥2 个任务上"任务内最优策略 vs 最差策略"的配对差 CI 不含 0，且不同任务的最优策略不同）→ 两篇制全速推进。
- **G2 部分通过**（差异显著但最优策略集中于 1–2 个）→ Paper 1 重心移向"解耦 + 机制 + 默认策略推荐"，Paper 2 的 routing 降级为成本路由。
- **G3 未通过**（区分度消失，差异为噪声）→ 收缩为单篇：Cost–Quality Decoupling and the Feedback Mechanism in LLM Agents；DecompBench 线暂停。

这是全计划风险回报比最高的 $150。

---

## 4. Paper 1 — 测量与解释

**题目（工作稿）**：*Behavioral Policies for LLM Agents: Measuring Execution-Strategy Diversity and Its Routing Headroom*
**目标**：ICLR/NeurIPS 主会（备选：D&B track，以基准+数据为主贡献）

### 4.1 研究问题

RQ1 记忆文件中的行为指令是否、如何因果地改变 agent 行为与结果？RQ2 效应的机制中介是什么？RQ3 策略能力能否被量化成 manager 可消费的形态？RQ4 若按任务选择策略，理论收益空间多大（离线）？

### 4.2 内容与贡献

**C1 Behavioral Policy Space**。π=(E,T,A) 形式化；**三种实现层级**：自然语言 / 结构化配置 / harness 强制执行。三者效应一致 ⇒ 排除 wording effect（回应 persona-null 文献）；不一致的部分本身构成发现（哪些策略必须机制化才生效）。每策略配 paraphrase ×3 做措辞鲁棒性。

**C2 因果测量**。AgentPolicyBench-Atomic：30–40 个任务，难度校准至无策略基线通过率 40–80%（≥70% 任务入带）；双对照（空白 + 等长中性填充）；每单元 n≥5；跨 3 档模型（flash/中档/frontier）。全因子 + 配对 bootstrap + Holm 校正。产出三轴效应量及其"×模型能力"交互（H5：模型越强，质量效应越小、成本效应占比越大）。

**C3 机制：反馈频率 > 侦察深度**。干预实验：harness 强制 edit→test→feedback 后重估三轴效应；判据——T 的质量负效应点估计缩小 ≥50% 且 CI 含 0。辅以剂量反应（每轴 4 档强度）、遵从度衰减曲线、URR（有效推理比，探索性）。若 H-M 成立，直接落地结论：**反馈纪律应内建于 harness，而非交给策略自由裁量**。

**C4 能力卡与离线路由空间**。能力卡 = (策略 × 任务桶) 的后验：质量分布（均值/CI/最坏情况/方差）+ 成本 + 时延 + 足迹，含样本量与时间衰减；IRT 联合估计策略能力 θ 与任务难度 b 实现跨任务集可比。预测力判据：留出任务上能力卡预测的策略排序 Spearman ≥0.6。**离线 oracle headroom 分析**（不建系统）：按任务选最优/最便宜达标策略的质量与成本包络、regret 分布、以及"错配代价"矩阵——量化 Paper 2 的预期收益上限。

### 4.3 评估与成功判据（预注册）

| 项 | 判据 |
|---|---|
| 操纵有效 | 三轴轨迹签名配对差 CI 不含 0（三种实现层级分别成立） |
| 非 wording | NL/结构化/harness 三版效应方向一致；paraphrase 方差 < 策略间方差的 1/3 |
| 机制 H-M | 强制反馈后 T 负效应缩小 ≥50% 且 CI 含 0 |
| 能力卡 | 留出集排序 Spearman ≥0.6；IRT θ 跨任务集相关 ≥0.7 |
| headroom | oracle vs 最优固定策略的成本/质量包络给出区间估计（预实验点估计：−12% 成本） |

资源：≈ 35 任务 × 14 条件（8 策略 × 实现层级抽样 + 对照）× 5 重复 × 3 模型分层 ≈ 6–8k runs，$10–14k；4 个月。

---

## 5. Paper 2 — 构建与调度

**题目（工作稿）**：*DecompBench: Capability-Aware Decomposition and Policy Routing for LLM Agent Teams*
**依赖**：Paper 1 的能力卡 + Step 0 通过 G1/G2

### 5.1 DecompBench：可拆分任务基准

- **组合式构造**：以 Paper 1 校准的原子任务为积木，拼装 typed subtask DAG；3 规模（3/6/10 子任务）× 4 依赖结构（链/星/菱形/宽并行）× 异质度。**异质性由能力卡诱导**：选取实测最优策略互不相同的原子任务入同一 DAG；"同质 DAG"（所有子任务同一最优）作为退化对照组。约 50 项目任务，80% 组合构造 + 20% 真实项目级任务（从 Commit0/SWE-EVO 风格任务改造）做外部效度。
- **三层判分**：子任务隐藏测试分、端到端集成测试分、**集成税** = 两者之差；另记接口契约违约。
- **核心性质**：每个子任务对每个策略的表现有离线真值 ⇒ **任意分派方案的期望得分与 regret 可解析计算**。这是与 OrchBench（模拟 worker）、DecisionBench（原子任务整体委托）、EntCollabBench（角色=权限）的决定性差异。

### 5.2 Manager：能力感知调度

L0 规则查表 → L1 预测式路由（任务特征 → 各策略 (Q,C) 预测 → argmax Q−λC；λ 按任务价值）→ L2 contextual bandit 在线更新能力卡（影子模式先行、探索限低风险桶）→ L3 失败升级链（触发器：连续测试失败/编辑震荡/无进展轮数 ⇒ 逐级放开 E、T；A 恒 closed-loop）+ 难尾 portfolio（互补策略并行 + 测试仲裁）。分解器先用真值 DAG（上限分析），再评自动分解。Manager 自身开销入账（单次决策成本必须 ≪ 路由毛收益）。

### 5.3 评估

基线：单 agent 整做 / 最优固定策略团队 / 随机路由 / oracle。判据：异质 DAG 上能力感知路由的 Utility 提升 CI 不含 0；regret ≤ oracle 差距 50%；退化对照组上不劣于固定团队（诚实报告无收益场景）；集成税随依赖密度的变化完整报告。外部：SWE-bench Verified 子集 + TheAgentCompany 子集迁移。失败分析对齐 MAST 分类。资源：$8–12k；4 个月。

---

## 6. 共享基础设施与开放科学

统一 harness（运行、判分、轨迹指标、能力卡更新）；所有实验预注册（假设、判据、n、统计口径）；基准、能力卡、全部轨迹（含 Step 0 与预实验 338 条）、分析脚本开源。统计标准全程：同任务配对、任务级 bootstrap 10 000 次、Holm 校正、均值/最坏情况/方差三列报告。

---

## 7. 风险表（v3 更新）

| 风险 | 缓解 |
|---|---|
| Step 0 判 G3（F4 是噪声） | 预设收缩路径（§3），沉没成本 ~$150 |
| "只是 prompt engineering" | 三实现层级不变性 + 因果效应量 + 机制干预（C1/C3 联合防御） |
| 与 test-time scaling 表面冲突 | 正面写入 discussion：收益来自已验证反馈的结构化搜索，非无结构 deliberation |
| MoA/MoE 撞名与类比攻击 | 不用 MoA 命名；类比一段 + 引用划界（expert=策略非模型、路由=实测能力卡非学习聚合） |
| 组合任务不真实 | 20% 真实项目级任务 + 外部基准迁移 |
| judge 偏差（URR/代码质量） | 双 judge 异源 + 10% 人工抽检；主判据永远是隐藏测试 |
| manager 开销吞噬收益 | 决策成本入账；L1 用轻量特征器 |

---

## 8. 时间线

| 阶段 | 内容 | 产出 |
|---|---|---|
| M0（2 周） | **Step 0 门槛实验** + 预注册 | Go/No-Go 决议 |
| M1–M2 | Atomic 基准校准、三实现层级、双对照 | 基准 v1 |
| M2–M4 | 全因子 + 机制干预 + 能力卡 + headroom 分析 | **Paper 1 投稿** |
| M4–M6 | DecompBench 构造（能力卡诱导）+ 验证 | 基准 v2 |
| M6–M8 | Manager L0–L3、regret 评估、外部迁移 | **Paper 2 投稿** + 全量开源 |

---

## 参考文献（在 v2 基础上新增/强调）

Wang, J. et al. (2024). *Mixture-of-Agents Enhances Large Language Model Capabilities.* arXiv:2406.04692（划界对象）· 其余同 v2：Zheng 2024（persona-null）、Salewski 2023、Jiang 2024、ReAct、Reflexion、Self-Refine、Plan-and-Solve、Self-Consistency、SWE-bench、SWE-agent、SWE-Lancer、Commit0、PaperBench、MLE-bench、SWE-Marathon (arXiv:2606.07682)、SWE-EVO、TheAgentCompany、MultiAgentBench、MAST、OrchBench (arXiv:2607.25656)、DecisionBench (arXiv:2605.19099)、EntCollabBench (arXiv:2605.08761)、ADAS、AFlow、RouteLLM、AutoGen、AGENTS.md、Terminal-Bench。

---

*附件：三层体系架构图（architecture_figure.svg，可入稿）；预实验统计报告（analysis_report.html）；能力卡原型（capability_cards_v0.json）。*
