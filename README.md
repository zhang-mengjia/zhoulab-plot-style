# Zhoulab 科学绘图风格

一个可迁移的 Codex skill，用于按实验室统一风格绘制或调整科研图。支持柱状图、小提琴图、普通折线图、PETH、森林图和 raster。

默认采用 Arial 9 pt、普通数据轴高 40.64 mm、统一的物理尺寸与类别间距、条件色半透明填充，以及统一的误差、显著性标注和导出规范。只调整绘图外观，保留输入的数据、统计单位、排除规则与已有统计结果。

## 在另一台电脑安装

将下面这段提示词发给另一台电脑上的 Codex：

> 请从 https://github.com/zhang-mengjia/zhoulab-plot-style 安装 `zhoulab-plot-style` skill。仓库根目录就是完整的 skill，请将整个仓库安装到当前用户的 Codex skills 目录（优先使用已配置的 CODEX_HOME 下的 skills，否则使用用户主目录下的 .codex/skills），文件夹名称保持为 zhoulab-plot-style。保留 SKILL.md、references/ 和 scripts/ 的相对结构。若同名 skill 已存在，先检查其内容与本地修改，不要直接覆盖。安装后检查所有内部引用是否齐全，并检查当前绘图 Python 环境的 NumPy、Matplotlib、SciPy 和 Arial 字体；报告缺失项。告诉我如何重新加载 skill，并给出一个调用示例。

也可以使用 Git 手动安装。以下命令适用于 Windows PowerShell，目标文件夹须不存在：

```powershell
$skillBase = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex\skills' }
New-Item -ItemType Directory -Path $skillBase -Force | Out-Null
git clone https://github.com/zhang-mengjia/zhoulab-plot-style.git (Join-Path $skillBase 'zhoulab-plot-style')
```

安装后重新开启 Codex 会话；若技能列表仍未更新，重启 Codex。也可以从 GitHub 的 **Code → Download ZIP** 下载，将解压后的文件夹重命名为 `zhoulab-plot-style`，放入同一 skills 目录。确保目录内直接包含 `SKILL.md`，避免重复嵌套文件夹。

## 使用

在 Codex 中明确调用：

> 使用 $zhoulab-plot-style，按实验室统一风格绘制我提供的数据。保留原有统计方法和结果，输出 PDF 和 600 dpi PNG。

按实际任务补充数据文件、条件顺序、颜色映射、误差定义和统计结果。不要把示例中的输出格式当作每次都必须生成的文件。

## 文件与依赖

| 路径 | 内容 |
|---|---|
| [SKILL.md](SKILL.md) | 技能入口和共同绘图规范 |
| [references/](references/) | 各图型规范及 Matplotlib 调用说明 |
| [scripts/matplotlib_helpers.py](scripts/matplotlib_helpers.py) | 自包含的 Matplotlib 绘图辅助函数 |

迁移时复制整个文件夹。规范与辅助实现不依赖原电脑上的项目、历史代码或其他 skill。

实际使用 Python 绘图时需要 NumPy、Matplotlib 和 Arial 字体；小提琴图的 KDE 另需 SciPy。请使用目标电脑实际的 Python 环境安装依赖，不照搬原电脑的解释器路径。Arial 字体不随仓库分发；字体缺失时需要先解决字体环境，不能静默替换字体。

此仓库包含绘图规范和代码，不包含实验数据、Python 环境、字体文件或 Python 编译缓存。更新已通过 Git 安装的 skill 时，可在该目录运行 `git pull --ff-only`；存在本地修改时先处理修改。
