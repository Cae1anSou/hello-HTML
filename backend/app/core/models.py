from sqlalchemy import Column, Integer, String, Enum, Text, ForeignKey,UniqueConstraint
from .config import Base

class UserKnowledge(Base):
    __tablename__ = "user_knowledge"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), index=True)
    knowledge_id = Column(String(64), index=True)
    __table_args__ = (UniqueConstraint('user_id', 'knowledge_id', name='_user_knowledge_uc'),)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(String(64), index=True, nullable=False)
    level = Column(Enum('basic', 'intermediate', 'advanced', 'expert'), nullable=False)
    description = Column(Text, nullable=False)
    __table_args__ = (UniqueConstraint('tag_name', 'level', name='_tag_level_uc'),)

class UserTime(Base):
    __tablename__ = "user_time"
    id = Column(Integer, primary_key=True, autoincrement=True)
    base_time = Column(Integer, default=0)
    advanced_time = Column(Integer, default=0) 

class Node(Base):
    __tablename__ = "nodes"

    id = Column(String(50), primary_key=True, index=True)
    label = Column(String(255), index=True)

class Edge(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, index=True)
    source_node = Column(String(50), ForeignKey("nodes.id"), primary_key=True)
    target_node = Column(String(50), ForeignKey("nodes.id"), primary_key=True)

class UserProgress(Base):
    __tablename__ = "user_progress"

    user_id = Column(String(50), index=True)
    node_id = Column(String(50), ForeignKey("nodes.id"), primary_key=True)