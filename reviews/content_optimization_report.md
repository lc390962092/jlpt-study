# JLPT 内容优化报告

生成时间：2026-08-03T16:15:14.655598+00:00

## 1. 数据规模

| 等级 | 词汇 | 语法 | 同形异义（词汇） | 同形异义（语法） |
|---|---:|---:|---:|---:|
| N5 | 807 | 100 | 4 | 12|
| N4 | 757 | 100 | 0 | 12|
| N3 | 1818 | 100 | 4 | 14|
| N2 | 3208 | 99 | 2 | 6|
| N1 | 4044 | 99 | 2 | 22|

## 2. 真题数据

| 文件 | 级别 | 题目数 |
|---|---|---:|
| `content/exams/N1_bunpou_1800.json` | N1 | 1836 |
| `content/exams/N1_bunpou_90.json` | N1 | 90 |
| `content/exams/N2_bunpou_90.json` | N2 | 90 |
| `content/exams/N3_bunpou_200.json` | N3 | 247 |
| `content/exams/N4_bunpou_90.json` | N4 | 90 |
| `content/exams/N5_bunpou_266.json` | N5 | 266 |
| `content/exams/sample_N5.json` | N5 | 8 |

## 3. 本次优化内容

1. **清理空字段**：所有 JSON 中的空字符串已统一处理为 `null`。
2. **合并真重复**：N2 语法、N1 语法各合并 1 条完全重复条目。
3. **同形异义标记**：为同一写法但不同读音/含义的条目添加 `homonym: true` 和 `homonym_count`。
4. **建立数据清单**：新增 `content/manifest.json`，记录文件路径、条目数、sha256 和质量指标。
5. **仓库清理**：新增 `.gitignore`，排除 `.bak*`、临时文件、Python 缓存和 `notes.csv`。

## 4. 下一步建议

- 前端读取 `manifest.json` 替代 `summary.json`，可感知缓存失效。
- 对 `homonym: true` 的条目，UI 显示时追加读音提示，避免混淆。
- 考虑将真题大文件（N1 1800题，1.8MB+）按 level/section 拆分为 chunk 懒加载。
- 对词汇/语法数据增加 `difficulty` 字段，便于测试时按难度出题。
