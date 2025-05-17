from typing import Dict, Any, List, Optional
from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from database import db_session
from models import Contact
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContactService:
    """Service for contact identity reconciliation using SQLAlchemy"""
    
    def find_matching_contacts(self, email: Optional[str], phone_number: Optional[str]) -> List[Contact]:
        """Find all contacts that match the given email or phone number"""
        try:
            query = Contact.query.filter(Contact.deletedAt.is_(None))
            
            # Build OR condition for email and phone
            conditions = []
            if email:
                conditions.append(Contact.email == email)
            if phone_number:
                conditions.append(Contact.phoneNumber == phone_number)
            
            if conditions:
                query = query.filter(or_(*conditions))
            
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Database error in find_matching_contacts: {str(e)}")
            db_session.rollback()
            raise
    
    def get_contact_by_id(self, contact_id: int) -> Contact:
        """Get a contact by ID"""
        try:
            contact = Contact.query.filter(Contact.id == contact_id).first()
            if not contact:
                raise ValueError(f"Contact with ID {contact_id} not found")
            return contact
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_contact_by_id: {str(e)}")
            db_session.rollback()
            raise
    
    def get_all_secondaries(self, primary_id: int) -> List[Contact]:
        """Get all secondary contacts linked to a primary contact"""
        try:
            return Contact.query.filter(
                and_(
                    Contact.linkedId == primary_id,
                    Contact.deletedAt.is_(None)
                )
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_all_secondaries: {str(e)}")
            db_session.rollback()
            raise
    
    def create_primary_contact(self, email: Optional[str], phone_number: Optional[str]) -> Contact:
        """Create a new primary contact"""
        try:
            contact = Contact(
                email=email,
                phone_number=phone_number,
                link_precedence='primary'
            )
            db_session.add(contact)
            db_session.commit()
            return contact
        except SQLAlchemyError as e:
            logger.error(f"Database error in create_primary_contact: {str(e)}")
            db_session.rollback()
            raise
    
    def create_secondary_contact(self, primary_id: int, email: Optional[str], phone_number: Optional[str]) -> Contact:
        """Create a new secondary contact linked to a primary"""
        try:
            contact = Contact(
                email=email,
                phone_number=phone_number,
                linked_id=primary_id,
                link_precedence='secondary'
            )
            db_session.add(contact)
            db_session.commit()
            return contact
        except SQLAlchemyError as e:
            logger.error(f"Database error in create_secondary_contact: {str(e)}")
            db_session.rollback()
            raise
    
    def convert_to_secondary(self, contact: Contact, new_primary_id: int) -> None:
        """Convert a primary contact to secondary and update its linked secondaries"""
        try:
            # Find all secondary contacts linked to this contact
            secondaries = self.get_all_secondaries(contact.id)
            
            # Update all secondaries to point to the new primary
            for secondary in secondaries:
                secondary.linkedId = new_primary_id
            
            # Convert this contact to secondary
            contact.linkPrecedence = 'secondary'
            contact.linkedId = new_primary_id
            
            db_session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Database error in convert_to_secondary: {str(e)}")
            db_session.rollback()
            raise
    
    def need_new_secondary(self, 
                           primary: Contact, 
                           existing_contacts: List[Contact], 
                           email: Optional[str], 
                           phone_number: Optional[str]) -> bool:
        """Check if a new secondary contact needs to be created"""
        existing_emails = [c.email for c in existing_contacts]
        existing_phones = [c.phoneNumber for c in existing_contacts]
        
        email_exists = not email or email in existing_emails
        phone_exists = not phone_number or phone_number in existing_phones
        
        return not (email_exists and phone_exists)
    
    def format_response(self, primary_contact: Contact) -> Dict[str, Any]:
        """Format response for a single primary contact with no secondaries"""
        emails = [primary_contact.email] if primary_contact.email else []
        phone_numbers = [primary_contact.phoneNumber] if primary_contact.phoneNumber else []
        
        return {
            'contact': {
                'primaryContatctId': primary_contact.id,
                'emails': emails,
                'phoneNumbers': phone_numbers,
                'secondaryContactIds': []
            }
        }
    
    def get_consolidated_contact(self, primary: Contact) -> Dict[str, Any]:
        """Get a consolidated contact (primary + all secondaries)"""
        secondaries = self.get_all_secondaries(primary.id)
        
        emails = []
        phone_numbers = []
        secondary_ids = []
        
        # Add primary contact details first
        if primary.email:
            emails.append(primary.email)
        
        if primary.phoneNumber:
            phone_numbers.append(primary.phoneNumber)
        
        # Add secondary contact details
        for secondary in secondaries:
            secondary_ids.append(secondary.id)
            
            if secondary.email and secondary.email not in emails:
                emails.append(secondary.email)
            
            if secondary.phoneNumber and secondary.phoneNumber not in phone_numbers:
                phone_numbers.append(secondary.phoneNumber)
        
        return {
            'contact': {
                'primaryContatctId': primary.id,
                'emails': emails,
                'phoneNumbers': phone_numbers,
                'secondaryContactIds': secondary_ids
            }
        }
    
    def identify_contact(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to identify and consolidate contacts"""
        email = request_data.get('email')
        phone_number = request_data.get('phoneNumber')
        
        # Validate input
        if not email and not phone_number:
            raise ValueError('At least one of email or phoneNumber must be provided')
        
        try:
            # Find all matching contacts
            matching_contacts = self.find_matching_contacts(email, phone_number)
            
            # Case 1: No matching contacts found, create a new primary contact
            if len(matching_contacts) == 0:
                new_contact = self.create_primary_contact(email, phone_number)
                return self.format_response(new_contact)
            
            # Separate primary and secondary contacts
            primary_contacts = [c for c in matching_contacts if c.linkPrecedence == 'primary']
            secondary_contacts = [c for c in matching_contacts if c.linkPrecedence == 'secondary']
            
            # Case 2: Only secondary contacts found
            if len(primary_contacts) == 0:
                # Get the primary contact for the first secondary
                primary_id = secondary_contacts[0].linkedId
                primary_contact = self.get_contact_by_id(primary_id)
                
                # Check if we need to create a new secondary contact
                if self.need_new_secondary(primary_contact, matching_contacts, email, phone_number):
                    self.create_secondary_contact(primary_id, email, phone_number)
                
                return self.get_consolidated_contact(primary_contact)
            
            # Case 3: One primary contact found
            if len(primary_contacts) == 1:
                primary_contact = primary_contacts[0]
                
                # Check if we need to create a new secondary contact
                if self.need_new_secondary(primary_contact, matching_contacts, email, phone_number):
                    self.create_secondary_contact(primary_contact.id, email, phone_number)
                
                return self.get_consolidated_contact(primary_contact)
            
            # Case 4: Multiple primary contacts found - we need to consolidate them
            # Sort by creation date (oldest first)
            primary_contacts.sort(key=lambda x: x.createdAt)
            oldest_primary = primary_contacts[0]
            other_primaries = primary_contacts[1:]
            
            # Convert other primaries to secondary linked to the oldest primary
            for contact in other_primaries:
                self.convert_to_secondary(contact, oldest_primary.id)
            
            # Check if we need to create a new secondary with the given email/phone
            all_secondaries = self.get_all_secondaries(oldest_primary.id)
            all_contacts = [oldest_primary] + all_secondaries
            
            if self.need_new_secondary(oldest_primary, all_contacts, email, phone_number):
                self.create_secondary_contact(oldest_primary.id, email, phone_number)
            
            return self.get_consolidated_contact(oldest_primary)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in identify_contact: {str(e)}")
            db_session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error in identify_contact: {str(e)}")
            raise