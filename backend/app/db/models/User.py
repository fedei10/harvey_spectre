from sqlalchemy import Column, Integer, String
from base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True
                   )











    #important arguments so i dont forget about them 
"""
is_default
can_deleted

created_at
updated_at
deleted_at


get__all
get_by_id
store
restore
update
soft_deleted
hard_soft_deleted
get_all_soft_deleted



"""

