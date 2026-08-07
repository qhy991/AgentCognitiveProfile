
---

# Agent Behavioral Policies: Measuring, Understanding, and Scheduling Execution Strategies for LLM Agents

## 认知策略即行为策略：LLM Agent 工作风格的因果建模、机制分析与动态调度

---

# 摘要

随着 LLM Agent 在软件工程、科学计算和自动化任务中的广泛应用，研究重点逐渐从“模型是否具备能力”转向“如何组织 agent 的行为过程”。现有工作主要关注模型规模、工具调用框架和多 agent 架构，而**同一个模型在面对相同任务时，不同执行策略如何影响任务结果、成本和稳定性，仍缺乏系统研究**。

本研究提出将 agent 的执行风格形式化为一个可控制的 **Behavioral Policy Space（行为策略空间）**。不同于传统 persona prompting，本研究关注影响 agent 决策过程的可观测策略变量，包括：

* **Exploration Budget (E)**：搜索空间探索程度（局部修复 ↔ 全局重构）
* **Deliberation Allocation (T)**：分析与执行资源分配（快速行动 ↔ 深度规划）
* **Feedback Adaptation (A)**：基于环境反馈调整策略的能力（固定计划 ↔ 动态修正）

三个维度构成 agent policy vector：

[
\pi=(E,T,A)
]

初步实验基于 8 类行为策略、17 个软件工程任务和 338 次 agent 执行，发现：

1. **行为策略能够稳定改变 agent 轨迹**：不同策略导致分析长度、代码探索范围、测试节奏最高产生 2.9 倍差异，证明 agent policy 可以被外部控制。
2. **更多推理并不必然带来更高质量**：增加规划深度显著提升成本（+$0.083/task，+2.1 steps），但在困难任务上降低正确率（−0.7pp）。
3. **反馈适应能力是影响稳定性的关键因素**：增加反馈调整机制能够显著降低失败尾部风险，而不增加平均成本。

基于这些发现，本研究进一步提出三个研究方向：

* **AgentPolicyBench**：建立第一个针对 agent 行为策略的系统评测平台；
* **Behavior Mechanism Study**：通过干预实验分析探索、推理和反馈机制对 agent 性能的因果影响；
* **Adaptive Policy Scheduler**：根据任务特征和运行轨迹动态选择 agent 行为策略，实现质量、成本和稳定性的联合优化。

本研究目标是建立一个新的 agent 优化范式：

> 从“提升模型能力”转向“学习和调度 agent 的行为策略”。

---

# 1. 背景与动机

## 1.1 当前 Agent 优化主要关注能力，而忽视行为策略

当前 LLM Agent 研究主要集中于：

### 模型能力

例如：

* 更大模型
* reasoning model
* test-time scaling

目标：

> 模型知道更多。

---

### Agent 架构

例如：

* ReAct
* Reflexion
* SWE-agent

目标：

> 如何组织 agent loop。

---

### 工具环境

例如：

* terminal
* browser
* code execution

目标：

> 如何扩大 agent 能力边界。

---

然而，在实际任务中，一个重要问题长期被忽略：

> 当模型、工具和任务均固定时，agent 的执行策略是否决定最终性能？

例如：

两个 agent：

Agent A:

```
阅读少量代码
快速修改
频繁测试
失败后调整
```

Agent B:

```
全面分析
设计完整方案
一次性修改
最后测试
```

即使使用同一个模型，两者可能产生完全不同的：

* 成本
* 时间
* 成功率
* 鲁棒性

因此，本研究提出：

**Agent Behavior Policy 是一种新的优化维度。**

---

# 2. 研究假设

## H1：Agent Behavior Policy 可被测量和控制

行为指令能够改变 agent：

* exploration
* reasoning allocation
* feedback loop

并形成稳定轨迹差异。

---

## H2：Agent 性能瓶颈不是推理长度，而是反馈闭环效率

传统假设：

[
more reasoning
\rightarrow
better performance
]

本研究提出：

[
better feedback loop
\rightarrow
better adaptation
]

推理增加可能只是：

* 更多 token
* 更长轨迹
* 更多成本

而非有效决策。

---

## H3：不同任务存在不同最优行为策略

例如：

简单 bug fix：

[
(E,T,A)=(low,low,high)
]

大型重构：

[
(E,T,A)=(high,high,high)
]

不存在统一最优 agent。

---

## H4：行为策略可以动态调度

agent 应根据：

* 任务属性
* 当前失败状态
* 轨迹信号

动态调整：

[
\pi_t
\rightarrow
\pi_{t+1}
]

---

# 3. Preliminary Study

## 3.1 实验设置

| 项目           | 设置                                    |
| ------------ | ------------------------------------- |
| Agent        | Claude Code                           |
| Model        | DeepSeek-V4-flash                     |
| Task         | 17 Python SWE tasks                   |
| Policy Space | 2³ = 8                                |
| Runs         | 338                                   |
| Metrics      | Quality / Cost / Latency / Trajectory |

---

## 3.2 发现

---

## Finding 1

### Behavior Policy 控制有效

不同 policy:

* reasoning tokens
* code exploration
* testing frequency

差异：

最高：

2.9×

说明：

agent 行为不是随机噪声。

---

## Finding 2

### More reasoning ≠ better agent

T 增强：

成本：

+49%

质量：

无提升甚至下降。

说明：

简单增加 reasoning budget 不是有效优化方向。

---

## Finding 3

### Feedback adaptation improves robustness

A 增强：

平均成本：

无变化

最坏情况：

+13pp

说明：

反馈机制主要改善：

tail risk。

---

# 4. Research Plan

# WP1: AgentPolicyBench

## 目标

建立 agent behavioral policy 的标准评测平台。

---

## Task Design

任务覆盖：

### Bug Fix

* concurrency
* numerical correctness
* algorithm

### Optimization

* performance tuning
* refactoring

### Ambiguous Requirement

测试 agent 判断能力。

---

## Metrics

不使用单一 score。

输出：

[
M=
(Q,C,L,R,S)
]

其中：

Quality:

* hidden tests
* regression

Cost:

* tokens
* API cost

Latency:

* execution time

Robustness:

* failure tail

Surgery:

* diff size
* touched files

---

# WP2: Behavioral Mechanism Analysis

## 核心问题

为什么不同策略有效？

---

## Experiment 1

### Feedback Intervention

Baseline:

agent 自主决定测试。

Treatment:

harness 强制：

```
edit
 ↓
test
 ↓
feedback
 ↓
edit
```

验证：

如果 T 的负效应消失：

说明：

问题不是 reasoning，

而是：

feedback frequency。

---

## Experiment 2

### Reasoning Efficiency

提出：

Useful Reasoning Ratio

[
URR=
\frac{
reasoning\ causing\ action\ change
}{
total\ reasoning
}
]

分析：

有效思考 vs 无效思考。

---

## Experiment 3

### Policy Compliance

研究：

instruction

↓

trajectory

之间关系。

---

# WP3: Adaptive Policy Scheduler

## Goal

学习：

任务 → 最优 policy

---

## Stage 1

Static Router

输入：

* task description
* repository features
* history

输出：

[
\pi
]

---

## Stage 2

Dynamic Scheduler

默认：

```
low exploration
high feedback
```

触发：

连续失败：

↓

增加：

* exploration
* planning

---

## Stage 3

Policy Portfolio

困难任务：

并行多个 policy：

[
{
\pi_1,\pi_2,...,\pi_k
}
]

选择最佳结果。

---

# 5. Evaluation

## Benchmark

* AgentPolicyBench
* SWE-bench Verified
* TerminalBench

---

## Baselines

### Fixed policy

always:

* low
* medium
* high

### Random

### Oracle

---

## Metrics

主要：

Quality-cost frontier

[
Utility
=======

Quality-\lambda Cost
]

同时报告：

* P50 latency
* P95 latency
* worst-case score

---

# 6. Expected Contributions

## Contribution 1

提出：

**Agent Behavioral Policy Space**

作为研究 LLM Agent 的新维度。

---

## Contribution 2

建立：

**AgentPolicyBench**

第一个系统研究：

policy → trajectory → outcome

的数据集。

---

## Contribution 3

发现：

**Feedback Adaptation Dominates Reasoning Depth**

揭示 agent 性能优化的新规律。

---

## Contribution 4

提出：

**Adaptive Policy Scheduler**

实现：

自动选择 agent 工作策略。

---

# 7. 论文定位

推荐标题：

## Option 1（ML/Agent）

**Behavioral Policies for LLM Agents: Measuring, Understanding, and Scheduling Agent Execution Strategies**

---

## Option 2（SE）

**From Prompts to Policies: Learning and Scheduling Behavioral Strategies for Software Engineering Agents**

---

## Option 3（MLSys）

**Optimizing LLM Agents through Behavioral Policy Scheduling**

---
