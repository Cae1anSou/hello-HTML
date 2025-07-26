"""
heatmap_main 模块
此模块处理用户交互数据的上传、统计与热力图生成。
"""
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from fastapi.middleware.cors import CORSMiddleware
from heatmap_util import generate_heatmap, get_heatmap

# 初始化 FastAPI 应用
app = FastAPI()
# 数据文件路径常量
DATA_FILE = "events.json"

# 配置跨域中间件，允许所有来源访问（可根据需求指定前端地址）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Event(BaseModel):
    """
    事件模型，包含交互类型、坐标以及可选的时间戳和持续时间。
    """
    type: str           # 事件类型，如 'click' 或 'hover'
    x: float            # 事件发生的 x 坐标
    y: float            # 事件发生的 y 坐标
    timestamp: float = None  # 可选事件时间戳
    duration: float = None   # 可选事件持续时间

class EventUpload(BaseModel):
    """
    上传数据模型，包含会话 ID、页面 ID、页面尺寸以及一组事件。
    """
    session_id: str     # 会话标识
    page_id: str        # 页面标识
    width: int          # 页面宽度
    height: int         # 页面高度
    events: list[Event] # 事件列表

@app.post("/upload_events")
async def upload_events(data: EventUpload):
    """
    上传事件接口。
    将上传的会话交互数据追加存储到本地 JSON 文件中。
    Args:
        data (EventUpload): 上传的事件数据
    Returns:
        dict: 操作状态
    """
    # 读取已有数据或初始化空列表
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    else:
        all_data = []
    # 追加当前上传数据
    all_data.append(data.dict())
    # 写入文件
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False)
    return {"status": "ok"}

@app.get("/heatmap")
def heatmap_route(session_id: str = None, page_id: str = None):
    """
    热力图生成接口。
    根据可选的 session_id 和 page_id 过滤数据，调用 util 中的函数生成热力图。
    Args:
        session_id (str, optional): 会话标识，默认为 None
        page_id (str, optional): 页面标识，默认为 None
    Returns:
        FileResponse: 生成的热力图图片文件
    """
    return get_heatmap(DATA_FILE, session_id, page_id)

@app.get("/stats")
def get_stats():
    """
    统计接口。
    统计所有会话中 click 和 hover 事件的总次数。
    Returns:
        dict: 包含 click 和 hover 事件计数
    """
    click_count = 0
    hover_count = 0
    # 如果数据文件不存在，返回默认计数
    if not os.path.exists(DATA_FILE):
        return {"click": 0, "hover": 0}
    # 读取并统计
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    for session in all_data:
        for e in session["events"]:
            if e["type"] == "click":
                click_count += 1
            elif e["type"] == "hover":
                hover_count += 1
    return {"click": click_count, "hover": hover_count}

@app.get("/stats_file")
def get_stats_file():
    """
    统计接口（文件格式）。
    与 /stats 功能相同，可根据需求返回不同格式或直接读取文件。
    Returns:
        dict: 包含 click 和 hover 事件计数
    """
    click_count = 0
    hover_count = 0
    if not os.path.exists(DATA_FILE):
        return {"click": 0, "hover": 0}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    for session in all_data:
        for e in session["events"]:
            if e["type"] == "click":
                click_count += 1
            elif e["type"] == "hover":
                hover_count += 1
    return {"click": click_count, "hover": hover_count}

@app.get("/")
def root():
    """
    根路径接口。
    提示服务已启动，并告知各接口使用方法。
    Returns:
        dict: 提示消息
    """
    return {"msg": "热力图后端已启动。上传数据请用 /upload_events，查看热力图请用 /heatmap"}
