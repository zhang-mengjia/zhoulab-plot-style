# Matplotlib 实现与调用

实现位于 [../scripts/matplotlib_helpers.py](../scripts/matplotlib_helpers.py)。它与 [SKILL.md](../SKILL.md) 及各图型文档共同构成完整指导，使用已安装的 NumPy、Matplotlib、Arial 字体和标准库；只有小提琴 KDE 另需 SciPy。

脚本定义物理画布、类别缩放、柱/小提琴/折线/PETH/森林图图层、动物连线、轴内比较括号及统一裁切导出。按当前执行环境读取或复用它；自包含 notebook 应将脚本正文复制到单个 code cell，注明来源，不导入 skill 或项目外部 helper。

## 调用与几何检查

1. 先调用 set_plot_style。Arial 缺失时明确报告缺少字体，不能静默换字体。
2. 普通 n 柱：positions = BAR_STEP × np.arange(n)，然后 bar_panel(positions)。相贴分组柱用 [柱状图规范](bar.md) 给出的组中心与偏移公式。
   小提琴使用相同 positions 调用 violin_panel(positions)，与对应柱图共用 x 范围和物理比例；draw_violin 接收真实个体值、颜色、可选的已有均值 mean 和区间端点 ci=(lower, upper)，不计算或选择统计模型。配对分组与密度说明见 [小提琴图规范](violin.md)。
3. 普通有序折线调用line_panel(真实完整x坐标)，每单位9.0311 mm、两端各0.25单位；普通PETH使用physical_panel(PETH_AX_WIDTH_IN)。PSTH按[统一时间尺度](peth.md)计算各轴宽，默认宽度为 `(t_max-t_min)×10.16/25.4` inch，轴高保持AX_H_IN。多面板横向位置按这些实际轴宽及面板间距累计。二维规则图使用physical_panel(AX_H_IN)并设等比例坐标。给出真实坐标、单位和轴内图例。
4. draw_bar 的 animal_values 各列须保留相同动物行序和 NaN 槽位，才可与 draw_animal_paths 对齐。
5. draw_error_line 的 error 可为长度 n 的对称误差或 2×n 的非对称误差幅度；CI 用上下两行 mean−lower、upper−mean。
6. draw_event_profile 可传对称 error，或用 bounds=(lower, upper) 提供非对称带；未平滑的输入不会自动平滑。
7. 常规检验使用format_test_label(p)生成三位有效数字的“星号/ns, 斜体P=数值”，multiline=True可在逗号后换行；模型消融图仅使用原P对应星号/ns。add_comparison_brackets的envelope_by_x为“柱位 → 所有动物值及均值+误差上缘”，比较按既定顺序传入。逐系数检验可用place_point_test_labels按真实x错层；check_test_labels检查边界及标签/图例碰撞。空间不足撤除本次标注后调整统一范围，不缩字号。
8. 图层完成后，普通轴高应为 ax.get_position().height × fig.get_figheight() = 1.6 inch。柱的物理宽度为 BAR_WIDTH × 数据轴物理宽度 / x跨度，普通净距同理使用 BAR_GAP。小提琴最大完整宽度按 VIOLIN_WIDTH 使用同一公式；对应柱图与小提琴的数据轴尺寸和类别中心应一致。
9. 不在固定物理轴之后调用 tight_layout/constrained_layout 自动重排。更改 x 范围时按新跨度重算轴宽；单纯扩展外边距不改变数据轴。
10. export_plot的outputs只传用户要求或既有流程必需路径；三格式共用同一内容边界，PDF Keywords保存主数据轴原始坐标供A4按轴对齐。A4以1:1复用PDF，保留轴高/字号，无标题；空间不足拆行或分页。
