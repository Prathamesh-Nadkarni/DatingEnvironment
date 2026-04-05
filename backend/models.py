from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    profile = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    target_relationship_stage = Column(String) # Short-Term, Long-Term, Marriage
    persona_prompt = Column(String) # Generated LLM Prompt
    
    user = relationship("User", back_populates="profile")
    answers = relationship("SJTAnswer", back_populates="profile")

class SJTQuestion(Base):
    __tablename__ = "sjt_questions"
    id = Column(Integer, primary_key=True, index=True)
    scenario_text = Column(String)
    options = Column(JSON) # e.g., [{"id":"A", "text":"..."}, {"id":"B", "text":"..."}]
    context_type = Column(String) # e.g., "Financial", "Family", "Ethical"

class SJTAnswer(Base):
    __tablename__ = "sjt_answers"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    question_id = Column(Integer, ForeignKey("sjt_questions.id"))
    selected_option_id = Column(String)
    
    profile = relationship("Profile", back_populates="answers")
    question = relationship("SJTQuestion")

class SimulationSession(Base):
    __tablename__ = "simulation_sessions"
    id = Column(String, primary_key=True, index=True) # UUID
    agent_a_id = Column(Integer, ForeignKey("profiles.id"))
    agent_b_id = Column(Integer, ForeignKey("profiles.id"))
    scenario_name = Column(String)
    status = Column(String) # "completed", "in-progress"
    harmony_score = Column(Integer, nullable=True)
    transcript = Column(JSON) # Conversation logs
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
