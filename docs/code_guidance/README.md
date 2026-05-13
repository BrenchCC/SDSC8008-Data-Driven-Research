# 代码运行指导：Dynamic Pricing with Demand Learning and Reference Effects

本文档说明如何运行本项目的 Independent Replication Experiment (IRE)、如何读取 Published Study Benchmark (PSB) 转储结果，以及如何生成报告中使用的复现图和扩展图。所有命令都从项目根目录执行。

## 1. 环境准备

安装必要依赖：

```bash
pip install -r requirements.txt
```

进入项目目录：

```bash
cd /path/to/SDSC8008-Data-Driven-Research
```

## 2. 目录结构

- `main.py`：统一命令行入口，只负责解析命令和分发任务。
- `model/`：需求函数与参考价格更新过程。
- `estimators/`：最小二乘估计器，用于估计 `alpha` 与正号记法下的 `beta`。
- `strategies/`：deterministic testing、slow-moving pricing 与 RARC 扩展实验。
- `metrics/`：期望收入与 regret 计算。
- `data/conversion.py`：将 PSB 数据转储为 `.npz` 和 `.csv`。
- `plotting/`：生成 Figure 2--5 的 PSB/IRE 对比图和 RARC 扩展图。
- `data/processed/`：转储后的 PSB 数据。
- `results/`：IRE 运行输出、RARC 扩展输出、对比图和汇总表。

## 3. 关键实现约定

- IRE 使用正号价格敏感度记法：
  `d(p, r) = alpha - beta * p + eta_plus * (r - p)^+ - eta_minus * (p - r)^+`。
- PSB 源数据中对价格斜率的存储方式与 IRE 记法不同；转储后的 metadata 会保留 `beta_positive_notation = 0.5`，便于和代码公式对齐。
- PSB 源数据只作为转储后的对比来源；IRE 仿真不直接依赖源数据文件。
- IRE 使用确定性随机种子，但不追求逐点匹配 PSB 的随机流；对比重点是策略现象、曲线形态和最终数量级。
- regret 使用期望收入计算；实现需求只用于估计器更新和路径诊断，避免把随机噪声混入理论收入比较。
- 所有数值仿真数组使用 `float64`。

## 4. 常用命令

转储 PSB 数据：

```bash
python main.py convert-data
```

运行全部 IRE 复现实验和 RARC 扩展实验：

```bash
python main.py run --experiment all
```

只运行 Figure 2 和 Figure 3 对应实验：

```bash
python main.py run --experiment figure2_3
```

只运行 Figure 4 和 Figure 5 对应实验：

```bash
python main.py run --experiment figure4_5
```

只运行 RARC 扩展实验：

```bash
python main.py run --experiment robust_calibration
```

生成全部图表：

```bash
python main.py plot --figure all
```

只生成 RARC 扩展图：

```bash
python main.py plot --figure robust_calibration
```

快速 smoke test：

```bash
python main.py run --experiment all --t-max 200 --n-sim 3 --results-dir results/_smoke
python main.py plot --figure all --results-dir results/_smoke
```

运行单元测试：

```bash
pytest -q
```

## 5. 输出说明

IRE 主输出目录：

- `results/deterministic_testing/no_reference/`
- `results/deterministic_testing/reference_effect/`
- `results/slow_moving/no_reference/`
- `results/slow_moving/reference_effect/`

每个策略目录包含：

- `simulation_result.npz`：IRE 的 regret、价格、需求、估计价格、参考价格路径和初始参考价格。
- `regret_summary.csv`：按时期汇总的平均 regret、标准差、标准误和 95% 置信区间。
- `regret_paths.csv`：逐路径累计 regret。
- `prices.csv`：逐路径价格。
- `reference_paths.csv`：逐路径参考价格。
- `price_estimates.csv`：估计最优价格路径。
- `metadata.json`：实验参数与复现实验说明。

PSB 转储输出目录：

- `data/processed/deterministic_testing/no_reference/`
- `data/processed/deterministic_testing/reference_effect/`
- `data/processed/slow_moving/no_reference/`
- `data/processed/slow_moving/reference_effect/`

每个目录包含 `psb_result.npz`、路径 CSV 和 metadata。

RARC 扩展输出目录：

- `results/robust_calibration/summary.csv`：每个环境和候选策略的最终 regret。
- `results/robust_calibration/candidate_summary.csv`：按候选策略聚合后的平均 regret、最坏情形 regret 和角色标记。
- `results/robust_calibration/environment_summary.csv`：按环境聚合的稳健性结果。
- `results/robust_calibration/metadata.json`：不确定集、候选集和选择规则。

## 6. 图表说明

复现图、扩展图和汇总表位于：

- `results/figures/figure2_comparison.png`
- `results/figures/figure3_comparison.png`
- `results/figures/figure4_comparison.png`
- `results/figures/figure5_comparison.png`
- `results/figures/robust_calibration.png`
- `results/figures/comparison_summary.csv`

Figure 2--5 采用三视图布局：

1. 左列：PSB 曲线。
2. 中列：IRE 曲线。
3. 右列：两者在同一坐标系下叠加，便于比较形态和数量级。

RARC 图包含三部分：

1. 平均最终 regret 热力图。
2. 最坏情形最终 regret 热力图。
3. 平均 regret 与最坏情形 regret 的稳健性前沿图。

图中的 `D` 表示复现默认候选，`M` 表示平均表现最优候选，`R` 表示 minimax 稳健候选。

## 7. 结果解读检查表

- Figure 2：deterministic testing 在 reference-effect 场景下 regret 明显大于 no-reference 场景，说明忽略参考价格状态会导致模型失配。
- Figure 3：reference-effect 场景下 estimated price 长期低于静态最优价格附近，说明参考效应污染了普通线性回归估计。
- Figure 4：slow-moving pricing 下参考价格和估计价格逐渐靠近静态 benchmark 附近，体现“慢变化”对状态扰动的控制。
- Figure 5：slow-moving pricing 在两种场景下都保持较低 regret，说明显式管理参考价格状态能够缓解 Figure 2 中的性能恶化。
- RARC：比较不同 `c_0` 和 `delta_decay_power` 在参考记忆强度与损失侧参考效应不确定时的稳健表现。

## 8. 常见问题

- 为什么 IRE 不逐点匹配 PSB 曲线？
  IRE 使用确定性随机种子，但不复刻 PSB 随机流。复现目标是验证机制、趋势和数量级。
- 为什么 regret 使用期望收入？
  论文的理论 regret 比较的是期望收益损失；随机需求冲击只应用于估计器更新。
- 为什么要先转储 PSB 数据？
  项目要求不直接使用源数据运行 IRE。转储为 `.npz` 和 `.csv` 后，PSB 结果只作为可视化和数值比较来源。
- RARC 是什么？
  RARC 全称为 Reference-Aware Robust Calibration，用于研究 slow-moving pricing 的扰动参数在不同参考记忆强度和损失侧参考效应下是否稳健。
