"""
知识图谱数据加载器

此文件用于获取知识点和用户已学习知识点数据
"""
from typing import Dict, Any
from fastapi import Request, Depends
from sqlalchemy.orm import Session
import logging
from app.core.config import get_db
from app.core.models import Node, Edge, UserProgress

# 配置日志
logger = logging.getLogger(__name__)

# 导入模块加载器
from app.modules.module_loader import register_module

# GET 请求处理器
async def get_handler(db: Session = Depends(get_db), user_id: str = "") -> Dict[str, Any]:
    """
    处理对模块API端点的GET请求。
    
    返回:
        包含模块数据的字典
    """
    try:
        logger.info("group_loader 模块 GET 请求开始")
        # 获取数据库会话
        nodes = db.query(Node).all() # 获取所有知识点
        edges = db.query(Edge).all() # 获取所有依赖关系
        
        learned_nodes = db.query(UserProgress.node_id).filter(UserProgress.user_id == user_id).all()

        if nodes is None or edges is None or learned_nodes is None:
            return {
                "module": "group_loader",
                "status": "error",
                "error": "知识图谱数据或已学习节点数据未找到"
            }

        return {
            "module": "group_loader",
            "status": "success",
            "data": {
                "nodes": [{"data": {"id": node.id, "label": node.label}} for node in nodes],
                "edges": [{"data": {"source": edge.source_node, "target": edge.target_node}} for edge in edges],
                "learnedNodes": learned_nodes
            }
        }
    except Exception as e:
        logger.exception("group_loader GET 处理出错")
        return {
            "module": "group_loader",
            "status": "error",
            "error": str(e)
        }
    
async def post_handler(request: Request) -> Dict[str, Any]:
    """
    处理对模块API端点的POST请求。
    
    参数:
        request: 包含客户端数据的FastAPI请求对象
        
    返回:
        包含响应数据的字典
    """
    logger.info("我的功能模块POST处理程序被调用")
    
    # 从请求获取JSON数据
    data = await request.json()
    
    # 在此实现您模块的POST功能
    # 处理数据并返回响应
    
    return {
        "module": "group_loader",
        "status": "error",
        "error": "该模块不支持 POST 操作"
    }

# 向应用程序注册此模块
register_module("group_loader", get_handler, post_handler)