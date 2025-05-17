from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, func
from sqlalchemy.sql import expression
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Contact(Base):
    """Contact model for SQLAlchemy"""
    __tablename__ = 'contact'
    
    id = Column(Integer, primary_key=True)
    phoneNumber = Column(String(255))
    email = Column(String(255))
    linkedId = Column(Integer, ForeignKey('contact.id'), nullable=True)
    linkPrecedence = Column(Enum('primary', 'secondary', name='link_precedence_enum'), nullable=False)
    
    # Use TIMESTAMP for PostgreSQL with timezone
    createdAt = Column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updatedAt = Column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    deletedAt = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Simple relationship without cascade issues
    secondary_contacts = relationship(
        'Contact', 
        backref='primary_contact',
        remote_side=[id]
    )
    
    def __init__(self, email=None, phone_number=None, linked_id=None, link_precedence='primary'):
        """Initialize a new Contact"""
        self.email = email
        self.phoneNumber = phone_number
        self.linkedId = linked_id
        self.linkPrecedence = link_precedence
    
    def to_dict(self):
        """Convert Contact to dictionary"""
        return {
            'id': self.id,
            'phoneNumber': self.phoneNumber,
            'email': self.email,
            'linkedId': self.linkedId,
            'linkPrecedence': self.linkPrecedence,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None,
            'deletedAt': self.deletedAt.isoformat() if self.deletedAt else None
        }