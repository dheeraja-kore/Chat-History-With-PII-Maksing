# Kore.ai Chat History Extractor with PII Masking

This Python script extracts chat history from Kore.ai API v2 and automatically masks personally identifiable information (PII) to protect sensitive data.

## Features

- Extracts chat history from Kore.ai using API v2
- Automatically detects and masks various types of PII, including:
  - Email addresses
  - Phone numbers
  - Social Security Numbers (SSN)
  - Credit card numbers
  - Dates of birth
  - IP addresses
  - Driver's license numbers
  - Passport numbers
  - Bank account numbers
  - Physical addresses
  - ZIP codes
- Groups conversations by session ID
- Exports data to CSV format
- Supports pagination for large datasets
- Context-aware PII detection

## Prerequisites

- Python 3.6 or higher
- `requests` library for API calls

## Installation

1. Clone or download the script to your local machine:
   ```bash
   git clone <repository-url>
   cd PII
   ```

2. Install required dependencies:
   ```bash
   pip install requests
   ```

## Usage

### Running the Script

1. Make the script executable (Unix/Linux/Mac):
   ```bash
   chmod +x "PII Maksing.py"
   ```

2. Run the script:
   ```bash
   python "PII Maksing.py"
   ```
   
   Or if using Python 3 specifically:
   ```bash
   python3 "PII Maksing.py"
   ```

### Required Information

When you run the script, you'll be prompted to provide the following information:

1. **Kore.ai API URL**: The base URL for your Kore.ai instance (e.g., `https://bots.kore.ai`)

2. **Stream ID (Bot ID)**: The unique identifier for your bot/stream

3. **JWT Token**: Your authentication token for accessing the Kore.ai API
   - To obtain a JWT token, refer to [Kore.ai documentation](https://developer.kore.ai/docs/bots/api-guide/apis/)

4. **Date Range**: 
   - Start date (format: YYYY-MM-DD)
   - End date (format: YYYY-MM-DD)

5. **Output filename**: The name for the CSV file (default: `chat_history_masked.csv`)

### Example Session

```
Kore.ai Chat History Extractor with PII Masking
==================================================

API Configuration:
Example URL: https://bots.kore.ai
Enter Kore.ai API URL: https://bots.kore.ai
Enter Stream ID (Bot ID): st-xxxx-xxxx-xxxx

Authentication:
Enter JWT Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Date Range:
Enter start date (YYYY-MM-DD): 2024-01-01
Enter end date (YYYY-MM-DD): 2024-01-31

Enter output CSV filename (default: chat_history_masked.csv): january_chats.csv

==================================================
Configuration Summary:
API URL: https://bots.kore.ai
Stream ID: st-xxxx-xxxx-xxxx
JWT Token: ********************...
Date Range: 2024-01-01 to 2024-01-31
Output File: january_chats.csv
==================================================

Proceed with these settings? (y/n): y

Fetching all chat history from 2024-01-01 to 2024-01-31
API URL: https://bots.kore.ai/api/public/bot/st-xxxx-xxxx-xxxx/getMessagesV2
Request body: {
  "dateFrom": "2024-01-01",
  "dateTo": "2024-01-31",
  "limit": 10000,
  "skip": 0
}

Fetching messages (skip=0)...
Response status code: 200
Response data keys: ['messages', 'total', 'moreAvailable']
Total messages in response: 1000
Total count from API: 2500
More available: true
Retrieved 1000 messages (total: 1000)
Unique sessions found so far: 45
Waiting 5 seconds before next API call to avoid rate limiting...

Fetching messages (skip=1000)...
Response status code: 200
Retrieved 1000 messages (total: 2000)
Unique sessions found so far: 92

Fetching messages (skip=2000)...
Response status code: 200
Retrieved 500 messages (total: 2500)
Unique sessions found so far: 115

Total messages retrieved: 2500
Total unique sessions: 115

Saving data to january_chats.csv
Successfully saved 115 sessions to CSV

Process completed successfully!
Output file: january_chats.csv

The chat history has been extracted and PII data has been masked.
```

## Output Format

The script generates a CSV file with two columns:
- **Session ID**: Unique identifier for each conversation session
- **Chat History**: The full conversation with PII masked

### Example Output

```csv
Session ID,Chat History
sess123,"[2024-01-15 10:30:45] User: My email is [EMAIL]
[2024-01-15 10:30:50] Bot: Thank you! I've noted your email address.
[2024-01-15 10:31:05] User: My phone number is [PHONE]
[2024-01-15 10:31:10] Bot: Got it! Your contact information has been updated."
sess124,"[2024-01-15 11:15:22] User: I need help with my account
[2024-01-15 11:15:25] Bot: I'd be happy to help you with your account. What specific issue are you experiencing?
[2024-01-15 11:15:40] User: I forgot my password for account [EMAIL]
[2024-01-15 11:15:45] Bot: I can help you reset your password. I'll send a reset link to your registered email."
```

## PII Types Detected and Masked

| PII Type | Example | Masked As |
|----------|---------|-----------|
| Email | john.doe@example.com | [EMAIL] |
| Phone | (555) 123-4567 | [PHONE] |
| SSN | 123-45-6789 | [SSN] |
| Credit Card | 1234 5678 9012 3456 | [CREDIT_CARD] |
| Date of Birth | 01/15/1990 | [DOB] |
| IP Address | 192.168.1.1 | [IP_ADDRESS] |
| Driver's License | DL12345678 | [DRIVERS_LICENSE] |
| Passport | P12345678 | [PASSPORT] |
| Bank Account | 12345678901234 | [BANK_ACCOUNT] |
| Address | 123 Main St, City, ST 12345 | [ADDRESS] |
| ZIP Code | 12345 | [ZIP] |

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Ensure your JWT token is valid and not expired
   - Check that you have the necessary permissions to access the chat history

2. **No Data Retrieved**
   - Verify the date range contains chat data
   - Check that the Stream ID is correct
   - Ensure the API URL is properly formatted

3. **Import Error for PIIMasker**
   - The script includes a built-in PIIMasker class as a fallback
   - No additional files are required

4. **Rate Limiting**
   - The script includes automatic delays between API calls
   - For large datasets, the extraction may take some time

### API Rate Limits

The script automatically handles pagination and includes delays to avoid rate limiting:
- Fetches up to 10,000 messages per request
- Waits 5 seconds between pagination requests
- Displays progress updates during extraction

## Security Notes

- The script masks PII data locally before saving to CSV
- Original chat data is not stored unmasked
- JWT tokens are displayed partially masked in the confirmation screen
- Always handle JWT tokens securely and never commit them to version control

For issues related to:
- The script itself: [Create an issue in this repository]
- Kore.ai API: [Refer to Kore.ai documentation](https://developer.kore.ai/)

