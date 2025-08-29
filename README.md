# Kore.ai Chat History Extractor with PII Masking

This Python script extracts chat history from Kore.ai API v2 and automatically masks personally identifiable information (PII) to protect sensitive data.

## Features

- Extracts chat history from Kore.ai using API v2
- Automatically detects and masks various types of PII including:
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
