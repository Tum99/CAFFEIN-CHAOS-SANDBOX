# app/mpesa/utils.py
# ─────────────────────────────────────────────────────────────
# M-Pesa Daraja API utility functions
# Handles: token generation, phone formatting, password building,
#          and STK push initiation
# ─────────────────────────────────────────────────────────────
import os
import base64
import requests
from datetime import datetime


def get_mpesa_token():
    """Get OAuth access token from Safaricom Daraja API."""
    env            = os.environ.get('MPESA_ENV', 'sandbox')
    consumer_key   = os.environ.get('MPESA_CONSUMER_KEY')
    consumer_secret = os.environ.get('MPESA_CONSUMER_SECRET')

    if env == 'sandbox':
        url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    else:
        url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    response = requests.get(url, auth=(consumer_key, consumer_secret))
    response.raise_for_status()
    return response.json()['access_token']


def format_phone(phone):
    """
    Convert any Kenyan phone format to the 2547XXXXXXXX format
    that M-Pesa requires.
    
    Accepts: 0712345678, +254712345678, 254712345678, 712345678
    Returns: 254712345678
    """
    phone = str(phone).strip().replace(' ', '').replace('-', '')

    if phone.startswith('+254'):
        phone = phone[1:]           # remove +
    elif phone.startswith('0'):
        phone = '254' + phone[1:]   # replace leading 0 with 254
    elif phone.startswith('7') or phone.startswith('1'):
        phone = '254' + phone       # bare number — prepend 254

    return phone


def build_password(shortcode, passkey, timestamp):
    """
    Build the base64-encoded password Safaricom requires.
    Formula: base64(shortcode + passkey + timestamp)
    """
    raw = shortcode + passkey + timestamp
    return base64.b64encode(raw.encode()).decode()


def stk_push(phone, amount, account_ref, description):
    """
    Initiate an M-Pesa STK Push (Lipa Na M-Pesa Online).
    
    Args:
        phone       : buyer's phone number (any Kenyan format)
        amount      : amount in KES (integer)
        account_ref : reference shown on buyer's phone (e.g. order ID)
        description : short description shown on buyer's phone
    
    Returns:
        dict with 'success' bool and either 'checkout_request_id' or 'error'
    """
    env          = os.environ.get('MPESA_ENV', 'sandbox')
    shortcode    = os.environ.get('MPESA_SHORTCODE', '174379')
    passkey      = os.environ.get('MPESA_PASSKEY')
    callback_url = os.environ.get('MPESA_CALLBACK_URL')

    if env == 'sandbox':
        url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    else:
        url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password  = build_password(shortcode, passkey, timestamp)
    phone_fmt = format_phone(phone)

    try:
        token   = get_mpesa_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type':  'application/json'
        }
        payload = {
            'BusinessShortCode': shortcode,
            'Password':          password,
            'Timestamp':         timestamp,
            'TransactionType':   'CustomerPayBillOnline',
            'Amount':            int(amount),
            'PartyA':            phone_fmt,
            'PartyB':            shortcode,
            'PhoneNumber':       phone_fmt,
            'CallBackURL':       callback_url,
            'AccountReference':  str(account_ref)[:12],  # max 12 chars
            'TransactionDesc':   str(description)[:13]   # max 13 chars
        }

        response = requests.post(url, json=payload, headers=headers)
        data     = response.json()

        if data.get('ResponseCode') == '0':
            return {
                'success':             True,
                'checkout_request_id': data.get('CheckoutRequestID'),
                'merchant_request_id': data.get('MerchantRequestID'),
                'response_description': data.get('ResponseDescription')
            }
        else:
            return {
                'success': False,
                'error':   data.get('errorMessage') or data.get('ResponseDescription', 'STK push failed')
            }

    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'error': f'Unexpected error: {str(e)}'}