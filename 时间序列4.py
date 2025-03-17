import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.ticker import FormatStrFormatter

# 设置支持中文的字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 上传 Excel 文件
uploaded_file = st.file_uploader("上传你的 Excel 文件", type=["xlsx", "xls"])

def load_data(uploaded_file):
    """ 加载用户上传的数据或使用默认数据 """
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file)
        st.write("数据预览：")
        st.write(data.head())
        # 自动检测第一列是否为索引列
        if data.iloc[:, 0].dtype in [np.int64, np.float64]:
            data.set_index(data.columns[0], inplace=True)
    else:
        data = pd.DataFrame({
            "标测电极": range(1, 61),
            **{i: [0] * 60 for i in range(-2, 14)}
        })
        data.set_index("标测电极", inplace=True)
    return data

# 加载数据
data = load_data(uploaded_file)

# 侧边栏
with st.sidebar:
    st.header("标测电极")
    electrode_a = st.selectbox("标测电极A", data.index, index=min(29, len(data.index)-1))
    electrode_b = st.selectbox("标测电极B", data.index, index=min(29, len(data.index)-1))
    fixed_y_min_str = st.text_input("固定 Y 轴最小值", value=str(data.min().min()))
    fixed_y_max_str = st.text_input("固定 Y 轴最大值", value=str(data.max().max()))
    try:
        fixed_y_min = float(fixed_y_min_str)
        fixed_y_max = float(fixed_y_max_str)
    except ValueError:
        st.error("请输入有效的数字！")
        fixed_y_min = data.min().min()
        fixed_y_max = data.max().max()
    st.write(f"当前 Y 轴范围：{fixed_y_min} 到 {fixed_y_max}")
    x_spacing = st.slider("X 轴紧凑度", 0.1, 1.0, 0.5, 0.1, key="x_spacing")
    show_values = st.button("显示具体数值")

# 计算差值
diff_a = data.loc[electrode_a]
diff_b = data.loc[electrode_b]
diff_ab = diff_a - diff_b

# 时间序列图
st.header("时间序列图")
fig_width = 10 * x_spacing
fig, axes = plt.subplots(3, 1, figsize=(fig_width, 10))
x_values = np.arange(len(data.columns)) * x_spacing
titles = [f"{electrode_a}", f"{electrode_b}", f"{electrode_a} - {electrode_b}"]
data_series = [diff_a, diff_b, diff_ab]

for ax, title, series in zip(axes, titles, data_series):
    ax.plot(x_values, series, marker="o", markersize=4, linewidth=1.5)
    ax.set_title(title, fontsize=10)
    ax.set_ylabel("")
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.8f'))
    ax.set_xticks(x_values)
    ax.set_xticklabels(data.columns, rotation=90, fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.set_ylim(fixed_y_min, fixed_y_max)

plt.tight_layout()
st.pyplot(fig)

if show_values:
    st.subheader("具体数值")
    df_a = pd.DataFrame({f"时间点 {col}": [diff_a[col]] for col in data.columns}).T.round(8)
    df_b = pd.DataFrame({f"时间点 {col}": [diff_b[col]] for col in data.columns}).T.round(8)
    df_ab = pd.DataFrame({f"时间点 {col}": [diff_ab[col]] for col in data.columns}).T.round(8)
    st.write("电极 A ：")
    st.dataframe(df_a.style.format("{:.20f}"))
    st.write("电极 B ：")
    st.dataframe(df_b.style.format("{:.20f}"))
    st.write("电极 A-B 差值：")
    st.dataframe(df_ab.style.format("{:.20f}"))
