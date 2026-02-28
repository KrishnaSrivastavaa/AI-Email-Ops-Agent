from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey, Text, Boolean, func)



Base = declarative_base()


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    role = Column(String, default="member")  # admin / member

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GmailAccount(Base):
    __tablename__ = "gmail_accounts"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    gmail_email = Column(String, nullable=False)
    refresh_token = Column(Text, nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())



class EmailMessage(Base):
    __tablename__ = "email_messages"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    gmail_message_id = Column(String, index=True)
    thread_id = Column(String)

    subject = Column(String)
    sender = Column(String)

    processed = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AutomationRule(Base):
    __tablename__ = "automation_rules"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    name = Column(String)
    trigger_type = Column(String)  # unread / keyword / sender
    action_type = Column(String)   # reply / classify / notify

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
