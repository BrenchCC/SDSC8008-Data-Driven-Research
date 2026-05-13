# SDSC8008 Dynamic Pricing Replication Project

本仓库是 SDSC8008 Data-driven Operations Research 期末个人项目，复现并扩展论文 *Dynamic Pricing with Demand Learning and Reference Effects* 的数值实验。项目包含 Python 复现实验、Published Study Benchmark (PSB) 与 Independent Replication Experiment (IRE) 对比图、Reference-Aware Robust Calibration (RARC) 扩展实验、英中双语 LaTeX 报告，以及后续制作 PPT 的设计材料。

## 项目交付物

| 交付物 | 位置 | 说明 |
|---|---|---|
| Python 代码复现 | `main.py` 与各模块目录 | 通过统一 CLI 转储 PSB、运行 IRE、绘图和测试 |
| 代码运行指导 | `docs/code_guidance/README.md` | 中文运行说明、命令示例、输出解释 |
| 英文报告 | `reports/8008-final-report/english/report_en.pdf` | 英文最终报告 |
| 中文报告 | `reports/8008-final-report/chinese/report_zh.pdf` | 中文阅读版报告 |
| 报告图像 | `reports/8008-final-report/figures/` 与 `results/figures/` | 流程图、架构图、实验图和扩展图 |
| PPT 设计材料 | `ppt-design/` | 18 页中文 PPT 设计、中英演讲稿模板和打包图片素材 |

## 快速开始

安装依赖：

```bash
pip install -r requirements.txt
```

转储 PSB 数据：

```bash
python main.py convert-data
```

运行全部 IRE 复现实验和 RARC 扩展实验：

```bash
python main.py run --experiment all
```

生成全部图表：

```bash
python main.py plot --figure all
```

运行单元测试：

```bash
pytest -q
```

更完整的运行说明见 `docs/code_guidance/README.md`。

## CLI 入口

`main.py` 是唯一命令行入口，只负责解析参数和分发任务，不直接写实验流程。

| 子命令 | 示例 | 作用 |
|---|---|---|
| `convert-data` | `python main.py convert-data` | 将公开 PSB 数据转储为 `.npz` 和 CSV |
| `run` | `python main.py run --experiment all` | 运行 IRE 复现实验和扩展实验 |
| `plot` | `python main.py plot --figure all` | 生成 Figure 2--5 对比图和 RARC 图 |

可选实验名：

- `figure2_3`：deterministic testing，对应 Figure 2 和 Figure 3。
- `figure4_5`：slow-moving pricing，对应 Figure 4 和 Figure 5。
- `robust_calibration`：RARC 扩展实验。
- `all`：运行全部实验。

## 仓库结构

```text
.
├── main.py
├── requirements.txt
├── configs/
├── data/
├── docs/
├── estimators/
├── metrics/
├── model/
├── plotting/
├── ppt-design/
├── reports/
├── results/
├── strategies/
├── tests/
└── utils/
```

## 顶层文件说明

| 文件 | 作用 |
|---|---|
| `README.md` | 项目级总览、目录说明和打包指导 |
| `main.py` | 统一 CLI 入口，包含 `convert-data`、`run`、`plot` 三类子命令 |
| `requirements.txt` | 复现实验和测试所需 Python 依赖 |
| `.gitignore` | 忽略缓存、环境、构建产物和临时文件 |

## 代码目录说明

| 目录/文件 | 作用 |
|---|---|
| `configs/replication.yaml` | 默认复现实验参数和路径配置 |
| `model/demand.py` | 需求函数、静态最优价格、期望收入计算 |
| `model/reference.py` | 参考价格指数平滑更新过程 |
| `estimators/least_squares.py` | 最小二乘估计器和 plug-in 价格估计 |
| `metrics/regret.py` | 基于期望收入的 regret 度量 |
| `strategies/deterministic_testing.py` | deterministic testing 策略复现 |
| `strategies/slow_moving.py` | slow-moving pricing 策略复现 |
| `strategies/robust_calibration.py` | RARC 扩展实验与候选策略排序 |
| `data/conversion.py` | 将 PSB 数据转储为结构化 `.npz` 和 CSV |
| `plotting/figures.py` | Figure 2--5、RARC 图和汇总表生成 |
| `utils/result_io.py` | 实验结果、CSV、NPZ、metadata 的读写工具 |
| `tests/test_core.py` | 核心公式、估计器、策略和 RARC 排序测试 |

各 Python 包中的 `__init__.py` 用于维持模块导入结构。

## 数据目录说明

| 目录/文件 | 作用 |
|---|---|
| `data/replication_package_MS-RMA-19-01931.R2/` | 已发表研究释放的原始数值包，仅用于转储生成 PSB |
| `data/processed/` | 转储后的 PSB 结构化数据，供绘图和对比使用 |
| `data/processed/deterministic_testing/no_reference/` | deterministic testing 无参考效应 PSB |
| `data/processed/deterministic_testing/reference_effect/` | deterministic testing 有参考效应 PSB |
| `data/processed/slow_moving/no_reference/` | slow-moving 无参考效应 PSB |
| `data/processed/slow_moving/reference_effect/` | slow-moving 有参考效应 PSB |

每个 `data/processed/...` 子目录通常包含：

- `psb_result.npz`：结构化数组。
- `psb_metadata.json`：参数和转储说明。
- `psb_mean_regret.csv`：平均 regret 曲线。
- `psb_regret_paths.csv`：逐路径 regret。
- `psb_price_estimates.csv`：估计价格路径。
- `psb_reference_paths.csv`：参考价格路径。

## 实验输出目录说明

| 目录/文件 | 作用 |
|---|---|
| `results/deterministic_testing/no_reference/` | IRE deterministic testing 无参考效应输出 |
| `results/deterministic_testing/reference_effect/` | IRE deterministic testing 有参考效应输出 |
| `results/slow_moving/no_reference/` | IRE slow-moving 无参考效应输出 |
| `results/slow_moving/reference_effect/` | IRE slow-moving 有参考效应输出 |
| `results/robust_calibration/` | RARC 扩展实验输出 |
| `results/figures/` | 复现实验图、扩展图、汇总 CSV |

每个主实验策略目录通常包含：

- `simulation_result.npz`：仿真数组。
- `regret_summary.csv`：平均 regret、标准差、标准误和置信区间。
- `regret_paths.csv`：逐路径 regret。
- `prices.csv`：价格路径。
- `reference_paths.csv`：参考价格路径。
- `price_estimates.csv`：估计最优价格路径。
- `metadata.json`：实验参数和运行说明。

RARC 输出包含：

- `summary.csv`：所有环境与候选策略组合的结果。
- `candidate_summary.csv`：按候选策略聚合的平均和最坏情形 regret。
- `environment_summary.csv`：按不确定环境聚合的压力测试结果。
- `metadata.json`：不确定集、候选集和选择规则。

## 文档目录说明

| 目录/文件 | 作用 |
|---|---|
| `docs/code_guidance/README.md` | 中文代码运行指导 |
| `docs/course/` | 课程项目说明与中英文转换文档 |
| `docs/limitation/limitation.md` | 项目约束和写作要求 |
| `docs/paper/paper.pdf` | 目标论文 PDF |
| `docs/paper/reference01/reference01.md` | 论文解读材料 1 |
| `docs/paper/reference02/reference02.md` | 论文解读材料 2 |
| `docs/personal_info/personal_info.md` | 报告署名信息来源 |
| `docs/diagram_sources/` | 可编辑流程图源文件和导出说明 |

## 报告目录说明

| 目录/文件 | 作用 |
|---|---|
| `reports/LaTex_Template/` | 课程提供的 LaTeX 模板 |
| `reports/8008-final-report/english/report_en.tex` | 英文报告源码 |
| `reports/8008-final-report/english/report_en.pdf` | 英文最终报告 |
| `reports/8008-final-report/chinese/report_zh.tex` | 中文报告源码 |
| `reports/8008-final-report/chinese/report_zh.pdf` | 中文最终报告 |
| `reports/8008-final-report/bib/references.bib` | 报告参考文献 |
| `reports/8008-final-report/figures/` | 报告新增流程图和架构图 |
| `reports/8008-final-report/build/` | LaTeX 编译中间文件和构建 PDF |

报告源码使用 `results/figures/` 中的实验图，以及 `reports/8008-final-report/figures/` 中的流程图和架构图。

## PPT 设计目录说明

| 目录/文件 | 作用 |
|---|---|
| `ppt-design/ppt_design_zh.md` | 18 页中文 PPT 设计思路、节奏、图片链接和素材预览 |
| `ppt-design/speech_template_zh.md` | 18 页中文演讲稿模板 |
| `ppt-design/speech_template_en.md` | 18 页英文演讲稿模板 |
| `ppt-design/figure/` | 后续用 ppt-agent 制作 PPT 的图片素材包 |

`ppt-design/figure/` 已包含：

- `reference_feedback.png`
- `replication_pipeline.png`
- `exploration_mechanisms.png`
- `rarc.png`
- `figure2_comparison.png`
- `figure3_comparison.png`
- `figure4_comparison.png`
- `figure5_comparison.png`
- `robust_calibration.png`

## 关键图表

| 文件 | 说明 |
|---|---|
| `results/figures/figure2_comparison.png` | deterministic testing regret 对比 |
| `results/figures/figure3_comparison.png` | deterministic testing 估计价格对比 |
| `results/figures/figure4_comparison.png` | slow-moving 参考价格与估计价格路径对比 |
| `results/figures/figure5_comparison.png` | slow-moving regret 对比 |
| `results/figures/robust_calibration.png` | RARC 热力图与稳健性前沿 |
| `results/figures/comparison_summary.csv` | PSB/IRE 最终指标汇总 |

## 报告编译

英文报告：

```bash
cd reports/8008-final-report/english
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=../build/english report_en.tex
cp ../build/english/report_en.pdf report_en.pdf
```

中文报告：

```bash
cd reports/8008-final-report/chinese
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=../build/chinese report_zh.tex
cp ../build/chinese/report_zh.pdf report_zh.pdf
```

如果重新清理了 `reports/8008-final-report/build/`，请确保 `reports/8008-final-report/build/bib/references.bib` 与 `reports/8008-final-report/bib/references.bib` 保持一致，或直接从报告目录使用默认输出目录编译。

## 打包指导

建议先创建打包输出目录：

```bash
mkdir -p dist
```

### 代码复现包

该包用于提交可运行代码、测试、配置、运行指导和必要 PSB 转储数据：

```bash
zip -r dist/SDSC8008-code-replication.zip \
  README.md \
  requirements.txt \
  main.py \
  configs \
  model \
  estimators \
  metrics \
  strategies \
  data/__init__.py \
  data/conversion.py \
  data/processed \
  plotting \
  utils \
  tests \
  docs/code_guidance \
  -x "*/__pycache__/*" "*/.DS_Store" "*/.pytest_cache/*"
```

如需让接收方从原始释放数据重新转储 PSB，可额外加入：

```bash
zip -r dist/SDSC8008-code-replication-with-source-data.zip \
  README.md \
  requirements.txt \
  main.py \
  configs \
  model \
  estimators \
  metrics \
  strategies \
  data \
  plotting \
  utils \
  tests \
  docs/code_guidance \
  -x "*/__pycache__/*" "*/.DS_Store" "*/.pytest_cache/*"
```

### 报告提交包

该包用于提交最终报告源码、PDF、图片和参考文献：

```bash
zip -r dist/SDSC8008-final-report.zip \
  reports/LaTex_Template \
  reports/8008-final-report/english \
  reports/8008-final-report/chinese \
  reports/8008-final-report/bib \
  reports/8008-final-report/figures \
  results/figures \
  -x "reports/8008-final-report/build/*" "*/.DS_Store"
```

### PPT 设计包

该包用于后续制作 PPT，不包含视频或正式幻灯片文件：

```bash
zip -r dist/SDSC8008-ppt-design.zip \
  ppt-design \
  -x "*/.DS_Store"
```

### 最终完整提交包

该包包含代码、报告、结果图、PPT 设计和课程相关说明，适合作为最终归档：

```bash
zip -r dist/SDSC8008-final-deliverable.zip \
  README.md \
  requirements.txt \
  main.py \
  configs \
  model \
  estimators \
  metrics \
  strategies \
  data/__init__.py \
  data/conversion.py \
  data/processed \
  plotting \
  utils \
  tests \
  docs/code_guidance \
  docs/course \
  docs/limitation \
  docs/paper/reference01 \
  docs/paper/reference02 \
  reports/LaTex_Template \
  reports/8008-final-report/english \
  reports/8008-final-report/chinese \
  reports/8008-final-report/bib \
  reports/8008-final-report/figures \
  results/figures \
  ppt-design \
  -x "*/__pycache__/*" "*/.DS_Store" "*/.pytest_cache/*" "reports/8008-final-report/build/*"
```

## 不建议打包的内容

| 类型 | 原因 |
|---|---|
| `__pycache__/` | Python 缓存文件，可自动生成 |
| `.pytest_cache/` | 测试缓存文件 |
| `.git/` | 版本控制元数据，不属于提交材料 |
| `.omc/`、`.omx/` | 本地工具状态文件 |
| `reports/8008-final-report/build/` | LaTeX 中间构建目录，最终 PDF 已复制到报告目录 |
| 临时 smoke test 输出 | 仅用于本地快速检查，不属于正式结果 |

## 复现命名约定

- PSB：Published Study Benchmark，指已发表研究释放数值结果转储后的基准数据。
- IRE：Independent Replication Experiment，指本项目独立实现并重新运行的仿真实验。
- RARC：Reference-Aware Robust Calibration，指本项目新增的参考价格感知稳健校准扩展实验。

## 验收检查表

提交前建议确认：

- `pytest -q` 能通过。
- `python main.py run --experiment all` 能完成默认实验。
- `python main.py plot --figure all` 能生成 `results/figures/` 下全部图表。
- `reports/8008-final-report/english/report_en.pdf` 和 `reports/8008-final-report/chinese/report_zh.pdf` 已更新。
- `ppt-design/ppt_design_zh.md` 中的图片链接能在本地打开。
- 打包文件位于 `dist/`，且不包含缓存、临时文件或本地工具状态。
