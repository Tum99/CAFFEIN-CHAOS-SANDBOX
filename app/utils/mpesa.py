import base64
import requests
from datetime import datetime
from flask import current_app

def get_mpesa_access_token():
    consumer_key = current_app.config['MPESA_CONSUMER_KEY']
    consumer_secret = current_app.config['MPESA_CONSUMER_SECRET']
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def trigger_stk_push(phone_number, amount, account_reference):
    access_token = get_mpesa_access_token()
    if not access_token:
        return {'success': False, 'message': 'Failed to authenticate with M-Pesa gateway.'}

    # Format phone number to 2547XXXXXXXX
    phone = phone_number.strip().replace('+', '')
    if phone.startswith('0'):
        phone = '254' + phone[1:]

    shortcode = current_app.config['MPESA_SHORTCODE']
    passkey = current_app.config['MPESA_PASSKEY']
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Generate Password: Base64(Shortcode + Passkey + Timestamp)
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode('utf-8')

    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": current_app.config['MPESA_CALLBACK_URL'],
        "AccountReference": account_reference,
        "TransactionDesc": f"Subscription for {account_reference}"
    }

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    res = requests.post(url, json=payload, headers=headers)
    
    if res.status_code == 200:
        data = res.json()
        if data.get('ResponseCode') == '0':
            return {
                'success': True, 
                'checkout_request_id': data.get('CheckoutRequestID'),
                'message': 'STK Push sent to phone.'
            }
    
    return {'success': False, 'message': 'Failed to trigger M-Pesa payment prompt.'}