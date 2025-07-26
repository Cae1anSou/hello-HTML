import os
import json
from fastapi.responses import FileResponse, JSONResponse


def generate_heatmap(xs, ys, width, height, output_file='heatmap.png'):
    """
    生成热力图函数。
    参数:
        xs (list of float): 所有点击或悬停事件的 x 坐标列表。
        ys (list of float): 所有点击或悬停事件的 y 坐标列表。
        width (int): 页面宽度，用于设置热力图坐标范围。
        height (int): 页面高度，用于设置热力图坐标范围。
        output_file (str): 热力图输出文件路径，默认 'heatmap.png'.
    """
    # 延迟导入绘图相关库，减少模块加载时的依赖
    import matplotlib.pyplot as plt
    import numpy as np

    # 使用 numpy 计算二维直方图热力图数据
    heatmap, xedges, yedges = np.histogram2d(
        xs, ys,
        bins=(64, 64),              # 划分 64x64 网格
        range=[[0, width], [0, height]]  # x,y 坐标范围
    )
    # 设置热力图显示范围
    extent = [0, width, 0, height]

    # 创建白色背景的绘图区域
    plt.figure(figsize=(12, 9), facecolor='white')
    # 绘制热力图，使用 'hot' 配色映射，设置透明度
    plt.imshow(
        heatmap.T,     # 转置热力图数组，以对齐坐标
        extent=extent,
        origin='upper',
        cmap='hot',
        alpha=0.7
    )
    # 设置坐标轴背景色
    plt.gca().set_facecolor('white')
    # 添加颜色条
    plt.colorbar()
    # 添加标题和坐标轴标签
    plt.title("用户交互热力图")
    plt.xlabel("X 坐标")
    plt.ylabel("Y 坐标")
    # 自动调整布局，防止标签被截断
    plt.tight_layout()
    # 保存热力图到文件
    plt.savefig(output_file, facecolor='white')
    plt.close()


def get_heatmap(DATA_FILE, session_id: str = None, page_id: str = None):
    """
    获取并返回热力图接口逻辑。
    1. 读取存储的事件数据文件。  
    2. 根据可选的 session_id 和 page_id 过滤数据。  
    3. 收集点击和悬停事件坐标，悬停事件根据 duration 进行重复统计。  
    4. 调用 generate_heatmap 生成热力图并返回图片。

    参数:
        DATA_FILE (str): 保存事件数据的 JSON 文件路径。
        session_id (str, optional): 会话 ID，用于筛选数据。
        page_id (str, optional): 页面 ID，用于筛选数据。
    返回:
        FileResponse: 成功时返回生成的热力图图片。
        JSONResponse: 失败时返回错误信息和对应 HTTP 状态码。
    """
    # 如果数据文件不存在，返回 404 错误
    if not os.path.exists(DATA_FILE):
        return JSONResponse({"error": "No data"}, status_code=404)

    # 读取事件数据
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    xs, ys = [], []  # 用于存储所有事件的坐标
    # 默认页面分辨率，当数据中包含 width/height 时会被替换
    width, height = 1920, 1080

    # 遍历所有会话数据
    for session in all_data:
        # 按 session_id 筛选
        if session_id and session["session_id"] != session_id:
            continue
        # 按 page_id 筛选
        if page_id and session.get("page_id") != page_id:
            continue
        # 更新页面宽高
        width = session.get("width", width)
        height = session.get("height", height)

        # 遍历事件列表，收集坐标
        for e in session["events"]:
            if e["type"] == "click":
                xs.append(e["x"])
                ys.append(e["y"])
            elif e["type"] == "hover":
                # 悬停事件根据持续时间进行重复计数
                count = int(e.get("duration", 1))
                xs.extend([e["x"]] * count)
                ys.extend([e["y"]] * count)

    # 如果没有收集到任何事件，返回 404 错误
    if not xs or not ys:
        return JSONResponse({"error": "No event data"}, status_code=404)

    # 生成热力图并保存到默认文件
    generate_heatmap(xs, ys, width, height, output_file='heatmap.png')
    # 返回图片文件响应
    return FileResponse("heatmap.png", media_type="image/png")
