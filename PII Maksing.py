#!/usr/bin/env python3
"""
Kore.ai Chat History Extractor with PII Masking
This script extracts chat history from Kore.ai API v2, saves it to CSV,
and applies PII masking to protect sensitive information.
"""

import csv
import json
import requests
import sys
from datetime import datetime
from typing import List, Dict, Any
import os
import re
import time

# Import the PIIMasker class from your existing file
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from PII_Masking import PIIMasker  # Note: renamed from "PII Maksing.py" 
except ImportError:
    # If import fails, include the PIIMasker class directly
    class PIIMasker:
        def __init__(self):
            # Define regex patterns for various PII types
            self.patterns = {
                # Email addresses
                'email': (
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    '[EMAIL]'
                ),
                
                # Phone numbers (various formats)
                'phone': (
                    r'(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
                    '[PHONE]'
                ),
                
                # Social Security Numbers
                'ssn': (
                    r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b',
                    '[SSN]'
                ),
                
                # Credit card numbers (basic pattern)
                'credit_card': (
                    r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
                    '[CREDIT_CARD]'
                ),
                
                # Date of Birth patterns (various formats)
                'dob': (
                    r'\b(?:0?[1-9]|1[0-2])[-/.](?:0?[1-9]|[12]\d|3[01])[-/.](?:19|20)?\d{2}\b|'
                    r'\b(?:0?[1-9]|[12]\d|3[01])[-/.](?:0?[1-9]|1[0-2])[-/.](?:19|20)?\d{2}\b|'
                    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b|'
                    r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
                    '[DOB]'
                ),
                
                # IP addresses
                'ip_address': (
                    r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                    '[IP_ADDRESS]'
                ),
                
                # Driver's license (general pattern)
                'drivers_license': (
                    r'\b[A-Z]{1,2}\d{6,8}\b',
                    '[DRIVERS_LICENSE]'
                ),
                
                # Passport numbers (general pattern)
                'passport': (
                    r'\b[A-Z]{1,2}\d{6,9}\b',
                    '[PASSPORT]'
                ),
                
                # Bank account numbers (general pattern)
                'bank_account': (
                    r'\b\d{8,17}\b',
                    '[BANK_ACCOUNT]'
                ),
                
                # Address patterns (simplified)
                'address': (
                    r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Plaza|Pl)\b[,\s]*(?:[A-Za-z\s]+,\s*)?(?:[A-Z]{2}\s+)?\d{5}(?:-\d{4})?\b',
                    '[ADDRESS]'
                ),
                
                # ZIP codes
                'zip_code': (
                    r'\b\d{5}(?:-\d{4})?\b',
                    '[ZIP]'
                )
            }
            
            # Additional context-based patterns
            self.context_patterns = {
                'dob_context': (
                    r'(?:date of birth|dob|born on|birthday|birth date)[:\s]*([^\n,;.]+)',
                    '[DOB]'
                ),
                'address_context': (
                    r'(?:address|live at|located at|residing at)[:\s]*([^\n;.]+)',
                    '[ADDRESS]'
                ),
                'name_context': (
                    r'(?:my name is|i am|call me)[:\s]*([A-Za-z\s]+)',
                    '[NAME]'
                )
            }

        def mask_pii(self, text):
            """Mask PII in the given text"""
            masked_text = text
            
            # Apply standard patterns
            for pii_type, (pattern, replacement) in self.patterns.items():
                # Skip certain patterns for context-based detection
                if pii_type in ['bank_account', 'drivers_license', 'passport']:
                    # Only apply these if they appear in specific contexts
                    context_pattern = rf'(?:account\s*(?:number|#)?|license\s*(?:number|#)?|passport\s*(?:number|#)?)[:\s]*({pattern})'
                    masked_text = re.sub(context_pattern, replacement, masked_text, flags=re.IGNORECASE)
                else:
                    masked_text = re.sub(pattern, replacement, masked_text, flags=re.IGNORECASE)
            
            # Apply context-based patterns
            for context_type, (pattern, replacement) in self.context_patterns.items():
                matches = re.finditer(pattern, masked_text, re.IGNORECASE)
                for match in matches:
                    # Replace the captured group (the actual PII) with the mask
                    if match.group(1):
                        masked_text = masked_text.replace(match.group(1), replacement)
            
            return masked_text


class KoreChatHistoryExtractor:
    def __init__(self, base_url: str, stream_id: str, jwt_token: str):
        """
        Initialize the Kore.ai Chat History Extractor
        
        Args:
            base_url: The base URL for Kore.ai API (e.g., https://bots.kore.ai)
            stream_id: The stream ID (bot ID)
            jwt_token: JWT authentication token
        """
        self.base_url = base_url.rstrip('/')  # Remove trailing slash if present
        self.stream_id = stream_id
        self.jwt_token = jwt_token
        self.api_url = f"{self.base_url}/api/public/bot/{stream_id}/getMessagesV2"
        self.headers = {
            'auth': jwt_token,
            'Content-Type': 'application/json',
            'accept-encoding': 'gzip, deflate, br'
        }
        self.pii_masker = PIIMasker()
        
    def fetch_chat_history(self, date_from: str, date_to: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch chat history from Kore.ai API with pagination support
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary mapping session IDs to their messages
        """
        print(f"\nFetching all chat history from {date_from} to {date_to}")
        print(f"API URL: {self.api_url}")
        
        all_messages_by_session = {}
        skip = 0
        total_messages = 0
        
        while True:
            # Prepare request body for POST
            request_body = {
                'dateFrom': date_from,
                'dateTo': date_to,
                'limit': 10000,
                'skip': skip
            }
            
            # Debug: Print request body
            print(f"Request body: {json.dumps(request_body, indent=2)}")
            
            try:
                print(f"\nFetching messages (skip={skip})...")
                response = requests.post(self.api_url, headers=self.headers, json=request_body)
                print(f"Response status code: {response.status_code}")
                response.raise_for_status()
                
                data = response.json()
                messages = data.get('messages', [])
                
                # Debug: Print the full response structure
                print(f"Response data keys: {list(data.keys())}")
                print(f"Total messages in response: {len(messages)}")
                print(f"Total count from API: {data.get('total', 'N/A')}")
                print(f"More available: {data.get('moreAvailable', 'N/A')}")
                if 'error' in data:
                    print(f"API Error: {data.get('error')}")
                
                if not messages:
                    print(f"No more messages found.")
                    break
                
                # Group messages by session ID
                for message in messages:
                    session_id = message.get('sessionId', 'unknown')
                    if session_id not in all_messages_by_session:
                        all_messages_by_session[session_id] = []
                    all_messages_by_session[session_id].append(message)
                    total_messages += 1
                
                print(f"Retrieved {len(messages)} messages (total: {total_messages})")
                print(f"Unique sessions found so far: {len(all_messages_by_session)}")
                
                # Check if we've retrieved all messages
                if len(messages) < 10000:
                    break
                
                skip += len(messages)
                
                # Add delay between API calls to avoid rate limiting
                if len(messages) == 10000:  # Only delay if we're fetching more pages
                    print("Waiting 5 seconds before next API call to avoid rate limiting...")
                    time.sleep(5)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                if hasattr(e.response, 'text'):
                    print(f"Response: {e.response.text}")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break
        
        # Print summary
        print(f"\nTotal messages retrieved: {total_messages}")
        print(f"Total unique sessions: {len(all_messages_by_session)}")
        
        # Sort sessions by first message timestamp
        sorted_sessions = {}
        for session_id, messages in all_messages_by_session.items():
            if messages:
                # Sort messages within each session by timestamp
                sorted_messages = sorted(messages, key=lambda x: x.get('createdOn', ''))
                sorted_sessions[session_id] = sorted_messages
        
        return sorted_sessions
    
    def format_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """
        Format messages into a conversation string
        
        Args:
            messages: List of message objects
            
        Returns:
            Formatted conversation string
        """
        if not messages:
            return "No messages found"
        
        # Sort messages by timestamp
        sorted_messages = sorted(messages, key=lambda x: x.get('createdOn', ''))
        
        conversation_parts = []
        
        for msg in sorted_messages:
            # Extract message text from components
            message_text = ""
            components = msg.get('components', [])
            
            for component in components:
                if component.get('data', {}).get('text'):
                    message_text = component['data']['text']
                    break
            
            if not message_text:
                continue
            
            # Determine if it's a user or bot message
            msg_type = msg.get('type', 'unknown')
            timestamp = msg.get('createdOn', '')
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_time = timestamp
            
            # Format the message
            if msg_type == 'incoming':
                prefix = "User"
            elif msg_type == 'outgoing':
                prefix = "Bot"
            else:
                prefix = msg_type.capitalize()
            
            conversation_parts.append(f"[{formatted_time}] {prefix}: {message_text}")
        
        return "\n".join(conversation_parts)
    
    def save_to_csv(self, messages_by_session: Dict[str, List[Dict[str, Any]]], 
                    output_file: str, mask_pii: bool = True):
        """
        Save chat history to CSV file with optional PII masking
        
        Args:
            messages_by_session: Dictionary mapping session IDs to messages
            output_file: Output CSV file path
            mask_pii: Whether to apply PII masking
        """
        print(f"\nSaving data to {output_file}")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Session ID', 'Chat History'])
            
            # Write data for each session
            sessions_written = 0
            for session_id, messages in messages_by_session.items():
                if messages:  # Only write sessions that have messages
                    conversation = self.format_conversation(messages)
                    
                    if mask_pii:
                        conversation = self.pii_masker.mask_pii(conversation)
                    
                    writer.writerow([session_id, conversation])
                    sessions_written += 1
            
        print(f"Successfully saved {sessions_written} sessions to CSV")


def get_user_input():
    """Get required inputs from user"""
    print("Kore.ai Chat History Extractor with PII Masking")
    print("="*50)
    
    # Get API configuration
    print("\nAPI Configuration:")
    print("Example URL: https://bots.kore.ai")
    base_url = input("Enter Kore.ai API URL: ").strip()
    if not base_url.startswith('http'):
        base_url = 'https://' + base_url
    
    stream_id = input("Enter Stream ID (Bot ID): ").strip()
    
    print("\nAuthentication:")
    jwt_token = input("Enter JWT Token: ").strip()
    
    # Get date range
    print("\nDate Range:")
    while True:
        date_from = input("Enter start date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(date_from, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD")
    
    while True:
        date_to = input("Enter end date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(date_to, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD")
    
    # Output file
    output_file = input("\nEnter output CSV filename (default: chat_history_masked.csv): ").strip()
    if not output_file:
        output_file = "chat_history_masked.csv"
    
    # Summary of inputs
    print("\n" + "="*50)
    print("Configuration Summary:")
    print(f"API URL: {base_url}")
    print(f"Stream ID: {stream_id}")
    print(f"JWT Token: {'*' * min(len(jwt_token), 20)}...")
    print(f"Date Range: {date_from} to {date_to}")
    print(f"Output File: {output_file}")
    print("="*50)
    
    confirm = input("\nProceed with these settings? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    return base_url, stream_id, jwt_token, date_from, date_to, output_file


def main():
    """Main function"""
    try:
        # Get user inputs
        base_url, stream_id, jwt_token, date_from, date_to, output_file = get_user_input()
        
        # Create extractor instance
        extractor = KoreChatHistoryExtractor(base_url, stream_id, jwt_token)
        
        # Fetch chat history (no session IDs needed)
        print("\nFetching all chat history...")
        messages_by_session = extractor.fetch_chat_history(date_from, date_to)
        
        # Save to CSV with PII masking
        extractor.save_to_csv(messages_by_session, output_file, mask_pii=True)
        
        print(f"\nProcess completed successfully!")
        print(f"Output file: {output_file}")
        print("\nThe chat history has been extracted and PII data has been masked.")
        
    except KeyboardInterrupt:
        print("\n\nProcess cancelled by user")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())