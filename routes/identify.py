from flask import Blueprint, request, jsonify
from services.contact_service import ContactService
from sqlalchemy.exc import SQLAlchemyError
from database import db_session
import logging

logger = logging.getLogger(__name__)

identify_bp = Blueprint('identify', __name__)

@identify_bp.route('/identify', methods=['POST'])
def identify():
    """Endpoint for contact identification"""
    try:
        # Get request data
        request_data = request.json
        
        # Validate request data
        if not request_data:
            return jsonify({'error': 'Request body is required'}), 400
        
        email = request_data.get('email')
        phone_number = request_data.get('phoneNumber')
        
        if email is None and phone_number is None:
            return jsonify({'error': 'At least one of email or phoneNumber must be provided'}), 400
        
        # Process the request
        service = ContactService()
        result = service.identify_contact(request_data)
        
        return jsonify(result), 200
    
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db_session.rollback()
        return jsonify({'error': 'A database error occurred'}), 500
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    
    finally:
        # Ensure the session is removed after each request
        db_session.remove()