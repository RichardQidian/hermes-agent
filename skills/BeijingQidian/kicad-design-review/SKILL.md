---
name: kicad-design-review
description: "Use when 审图/设计评审/review my board/投板前检查. KiCad 语义评审。"
license: MIT
metadata:
  upstream: "https://github.com/aklofas/kicad-happy"
  upstream_commit: "0fc045af790ae35c475697813c3a8d76259a8811 (2026-08-31)"
  vendored: "2026-09-01"
  python: "3.10+ (核心分析纯 stdlib；datasheets 层需 jsonschema/referencing/pyyaml)"
---

# KiCad 设计评审（kicad-happy vendored）

把 KiCad 工程解析成结构化 JSON，AI 基于数据推理出评审报告。**脚本是确定性数据抽取工具（无 AI），推理才是 AI 的活**——数据可审计、推理可追溯。

## 适用触发

- "审图" / "设计评审" / "review my board" / "投板前检查" / "is this ready to order"
- "check my power supply" / "verify this circuit" / "查电源树" / "这个原理图有什么问题"
- 本项目的固定工作流：`tools/sch_p01~06_gen.py` 生成新板 → 本技能评审 → KiCad ERC/DRC 对照去伪

## 目录结构（vendored，勿随意改）

```
scripts/            # 核心分析器（纯 stdlib，无第三方依赖）
  analyze_schematic.py   # 原理图→JSON：组件/网络图/60+检测器
  analyze_pcb.py         # PCB→JSON：布局/DFM/热
  analyze_gerbers.py     # Gerber→JSON：fab 文件检查
  analyze_thermal.py     # 热分析
  analyze_emc.py         # EMC 预合规风险（消费 schematic.json+pcb.json）
  emc_rules.py emc_formulas.py emc_spice.py   # EMC 规则引擎
  ...（kicad_utils/sexp_parser/detector_helpers/domain_detectors/等支撑模块）
  envelopes/             # 各域检测器包
  methodology_*.md       # 检测器方法论
scripts/datasheets/ # datasheets 层（可选）：PDF→结构化规格提取（已打 REPO_ROOT 路径补丁）
  scripts/ schemas/ datasheet_types/ prompts/
references/         # 评审方法论（report-generation/net-tracing/deep-review/standards-compliance/oshwa…）
```

## 标准评审流程（Design Review Contract）

1. **定位工程**：读 `.kicad_pro` 找根 sheet；多页工程（如本项目 p00~p06）从根 sheet 入口，analyzer 自动遍历层级子页。
2. **跑分析器**（全部在 `scripts/` 目录下执行）：
   ```bash
   cd <skill>/scripts
   python3 analyze_schematic.py --input <proj>.kicad_sch --output /tmp/analysis/schematic.json
   python3 analyze_pcb.py      --input <proj>.kicad_pcb --output /tmp/analysis/pcb.json
   python3 analyze_gerbers.py  --input <gerber_dir>     --output /tmp/analysis/gerbers.json   # 如有
   python3 analyze_thermal.py  --input /tmp/analysis/pcb.json --output /tmp/analysis/thermal.json
   python3 analyze_emc.py --schematic /tmp/analysis/schematic.json --pcb /tmp/analysis/pcb.json \
     --output /tmp/analysis/emc.json
   ```
   报告里**明确列出跑了哪些、没跑哪些**。
3. **datasheets 交叉验证（可选但推荐）**：先查工程下 `datasheets/extracted/` 是否有缓存；无则用 `scripts/datasheets/scripts/datasheet_lookup.py` 按 MPN 提取本地 PDF。没有 datasheet 支撑时，所有电气结论降级为 **consistency-only**，报告禁用 "verified/confirmed/按数据手册" 字样（对应 DS-001/002/003 finding）。
4. **交叉核对**：原始文件抽查（组件数、关键网络逐脚跟踪）、schematic↔PCB 对照、datasheet 核对反馈分压 Vout、EMC 报告并入。
5. **写报告**：按 severity（error/warning/info）+ confidence（deterministic/heuristic/datasheet-backed）分级；电源树可视化；每个 finding 带可验证上下文。参考 `references/report-generation.md`。

## 与 ERC/DRC 的分工

- KiCad ERC/DRC：语法/连接完整性（悬空脚、未连接网络、规则冲突）
- 本技能：**语义层**——电源树推算、反馈网络 Vout、RC 截止频率、跨域电压错配、ESD 覆盖审计、上拉/下拉缺失、晶体负载电容、DFM 风险、EMC 预合规、OSHWA 认证就绪度
- 两者结果对照：ERC 报错先修，再跑本技能找语义问题；检测器误报（如引脚名启发式匹配失败）要在报告里 triage 掉，不直接升级为 blocker。

## 已知坑（Pitfalls）

- **多页工程必须从根 sheet 入口**，只传子页会漏层级引用。
- datasheets 层脚本已 patch `REPO_ROOT`（vendored 布局适配）；若重新从上游拷贝需重打（`parents[3]`→`parents[1]`，`"skills/datasheets/schemas"`→`"schemas"`）。
- datasheet PDF 提取需要 `pdftotext`（poppler-utils）：`sudo apt-get install -y poppler-utils`。
- SPICE 子电路仿真需要 `ngspice`，未装则跳过并注明 review gap。
- `analyze_emc.py` 必须同时给 schematic.json + pcb.json（缺 PCB 时只跑几何规则子集）。
- 分析器 JSON 是**数据**不是**结论**：report 必须含人工核对步骤，不能只 dump JSON。
- 上游更新：`git -C /tmp/kicad-happy pull` 后按目录结构重新 vendor，更新本 SKILL.md 的 upstream_commit。

## 验证

评审完成前自查：datasheets 状态已声明 ✓、分析器清单已列出 ✓、原始文件抽查过 ✓、误报已 triage ✓、缺失步骤作为 review gap 写明 ✓。
