# AGENTS.md × MBTI：人格化记忆文件对 agent 解题效果的影响（MVP 实验脚手架）

研究问题：往 agent 的记忆文件（CLAUDE.md / AGENTS.md）里写入 MBTI 式人格内容，
会不会改变 agent 的**工作方式**（轨迹）和**任务结果**（隐藏测试通过率、成本）？

## 实验设计

**自变量**：5 个记忆文件变体（`variants/`），除人格段落外内容完全相同、长度基本匹配：

| 变体 | 内容 |
|---|---|
| `control` | 等长中性填充文本（无任何行为暗示） |
| `intj_label` | 只声明"你是 INTJ"并描述特质（弱操纵） |
| `esfp_label` | 只声明"你是 ESFP"并描述特质（弱操纵） |
| `intj_behavior` | I/N/T/J 四轴行为化指令：静默、先全局后动手、逻辑优先、先计划一次做完（强操纵） |
| `esfp_behavior` | E/S/F/P 四轴行为化指令：边做边说、直接上手小步迭代、体验优先、探索式随时调向（强操纵） |

**因变量**：
- 结果指标：隐藏测试通过比例（部分分，比二元 pass/fail 灵敏）、回归破坏（visible 测试）、步数、token 成本、超时
- 行为指标（操纵检验）：叙述字数、首次编辑前的读取次数、测试运行次数、TodoWrite 次数、工具调用数、触碰文件数

**任务集**（`tasks/`，10 个，全部自动判分，几分钟内可完成）：

| 任务 | 类型 | 内容 |
|---|---|---|
| t01_date_range | clear | 日期区间 off-by-one 修复 |
| t02_lru_cache | clear | LRU 淘汰顺序修复（get 不刷新新近度） |
| t03_csv_stats | clear | CSV 均值的脏数据健壮性（精确规格） |
| t04_slugify | clear | 按精确规则实现 slugify |
| t05_rate_limiter | clear | 滑动窗口限流 off-by-one 修复 |
| t06_flatten | clear | 按精确规则实现嵌套结构展平 |
| t07_log_summary | vague | "写个有用的日志摘要"（隐藏测试检查关键事实是否被呈现） |
| t08_config_robust | vague | "让配置加载足够健壮"（宽容判分） |
| t09_dedupe_contacts | vague | "清理联系人重复"（有同名不同人的陷阱） |
| t10_todo_cli | vague | "把 CLI 打磨得好用"（无 traceback、状态可见等） |

clear/vague 分层对应假设：**人格效应在模糊任务上应该更大**。

**预注册假设**（跑之前先想好怎么判读）：
- H1：标签版效应 ≈ 0，行为版 ≠ 0（效应来自具体指令而非人格标签）
- H2：J/T/I 侧（intj_behavior）在 clear 任务占优；P/E/S 侧在 vague 任务不差或更好
- H3：主要差异体现在过程指标（步数/成本/轨迹形态）而非成功率

## 快速开始

前置：已安装并登录 [Claude Code](https://docs.claude.com/en/docs/claude-code)
（`claude` 命令可用），Python 3.10+。

```bash
pip install -r requirements.txt        # 只有 pytest

# 0) 自检：验证任务集本身有效（不调用 Claude，不花钱）
python scripts/selftest.py

# 1) 冒烟测试：2 任务 × 2 变体 × 1 次 = 4 个 run
python scripts/run_experiment.py \
  --tasks t01_date_range,t07_log_summary \
  --variants control,intj_behavior --reps 1 --model haiku

# 2) 正式 MVP：10 × 5 × 3 = 150 runs（可中断，重跑会自动跳过已完成的）
python scripts/run_experiment.py --reps 3 --parallel 2 --model haiku

# 3) 分析：生成 results/report.md
python scripts/analyze.py
```

`--model` 直接透传给 `claude --model`，可用别名（haiku/sonnet/opus）或完整模型
ID；先用便宜模型探信号，有信号再换大模型复跑。先跑 `claude -p "hi" --model haiku`
确认别名在你的版本可用。

## 判读规则（重要，按顺序）

1. **先看 report 第 3 节（操纵检验）**：行为列在变体间是否分离？
   例如 esfp_behavior 的叙述字数应明显高于 intj_behavior，intj_behavior 的
   首次编辑前读取数、TodoWrite 应更高。**如果行为都没变，说明操纵无效，
   第 2 节的任何差异都是噪声**——应该回去加强指令措辞，而不是加大样本。
2. 再看第 2 节配对差的 bootstrap 95% CI：排除 0 才算有信号；跨 0 只说明
   效应小于当前检测力（10 任务 × 3 次的功效有限），不是"无效应"的证明。
3. 对照 clear/vague 两列看交互（H2），对照 label/behavior 看 H1。
4. "行为变了但结果没变"本身就是一个发现（人格影响成本与风格而非能力）。

## 注意事项 / 已知坑

- **全局记忆混淆**：Claude Code 还会加载 `~/.claude/CLAUDE.md`。跑实验期间
  请将其清空或保持恒定（对所有条件相同即可，但最好清空）。
- **无头模式没有交互**：agent 提问不会有人回答。因此 E 侧指令写的是
  "边做边说、陈述假设后继续"，而不是"提问并等待"；自行修改变体时别写出
  会阻塞的指令。
- **权限**：默认用 `--allowedTools` 白名单（Bash/读写/编辑等）。`--yolo` 切换为
  `--dangerously-skip-permissions`，只在容器/虚拟机里用。
- **不要把 `tests_hidden/` 或 `solution/` 拷进 workspace**，agent 会看到答案。
  runner 只拷贝 `workspace/`，判分在临时目录做，防作弊已处理（visible 回归
  测试用任务原始副本重跑，agent 改测试文件无法刷分）。
- **统计功效**：150 runs 对二元结论功效很低，所以判分用部分分、比较用同任务
  配对差。想收窄 CI：先加 `--reps`，再加任务数。
- 修改/新增任务后必须重跑 `python scripts/selftest.py`（保证解答=1.0、
  基线<1.0，否则任务没有区分度）。
- 变体文件请保持长度接近（selftest 检查 ±30%），避免"上下文更长"混淆。

## 升级路径（MVP 有信号之后）

1. **归因到轴**：做单轴消融（每次只翻转一个轴的行为指令，其余中性）。
2. **全因子**：16 型 × 行为版，或在 SWE-bench Lite 子集上复现。
3. **跨模型**：同一套变体在 haiku/sonnet/opus 上比较（人格敏感度随能力变化？）。
4. **机制检验**：用 `--memory-filename AGENTS.md` 适配其他 harness，或改用
   `claude --append-system-prompt` 注入同样文本，验证注入位置是否重要。
5. 行为指标可加：编辑撤销率、方案切换次数（需要更细的轨迹解析）。

## 目录结构

```
variants/            5 份人格变体（写入每个 run 的 CLAUDE.md）
tasks/<id>/
  workspace/         给 agent 的初始代码（含部分可见测试）
  prompt.txt         任务指令（通过 claude -p 传入）
  tests_hidden/      隐藏判分测试（agent 永远看不到）
  solution/          参考解（仅供 selftest 验证测试有效性）
  meta.json          类型 clear/vague、隐藏测试数等
scripts/
  run_experiment.py  跑实验（可断点续跑、并发、乱序）
  grade.py           判分（junitxml 解析，部分分）
  behavior_metrics.py 轨迹行为指标（操纵检验用）
  analyze.py         配对差 + bootstrap CI + 行为表 → results/report.md
  selftest.py        任务集自检（不花钱）
results/runs/<run_id>/   每个 run 的 workspace、transcript.jsonl、record.json
```
