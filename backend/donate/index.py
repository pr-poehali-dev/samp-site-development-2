import json
import os
import uuid
import base64
import urllib.request
import urllib.error
from typing import Dict, Any
from pydantic import BaseModel, Field


class DonateRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50)
    amount: int = Field(..., gt=0, le=1000000)


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    '''Отправка сообщения в Telegram'''
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = json.dumps({
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except urllib.error.URLError:
        return False


def create_yukassa_payment(shop_id: str, secret_key: str, amount: int, nickname: str) -> Dict[str, Any]:
    '''Создание платежа через ЮKassa API'''
    url = 'https://api.yookassa.ru/v3/payments'
    
    payment_data = {
        'amount': {
            'value': f'{amount}.00',
            'currency': 'RUB'
        },
        'confirmation': {
            'type': 'redirect',
            'return_url': f'https://{os.environ.get("PROJECT_ID", "")}.poehali.dev/?success=true'
        },
        'capture': True,
        'description': f'Донат от игрока {nickname}',
        'metadata': {
            'nickname': nickname
        }
    }
    
    idempotence_key = str(uuid.uuid4())
    credentials = base64.b64encode(f'{shop_id}:{secret_key}'.encode()).decode()
    
    data = json.dumps(payment_data).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'Idempotence-Key': idempotence_key,
            'Authorization': f'Basic {credentials}'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
            return {
                'success': True,
                'payment_url': result['confirmation']['confirmation_url'],
                'payment_id': result['id']
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return {
            'success': False,
            'error': f'Payment error: {error_body}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Создание платежа для доната и отправка уведомления в Telegram
    Args: event - содержит httpMethod, body с nickname и amount
          context - объект с атрибутами request_id, function_name
    Returns: HTTP ответ с URL для оплаты или ошибкой
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
    
    try:
        body_data = json.loads(event.get('body', '{}'))
        donate_req = DonateRequest(**body_data)
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Invalid request: {str(e)}'}),
            'isBase64Encoded': False
        }
    
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
    shop_id = os.environ.get('YUKASSA_SHOP_ID', '')
    secret_key = os.environ.get('YUKASSA_SECRET_KEY', '')
    
    if not all([bot_token, chat_id, shop_id, secret_key]):
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Server configuration error'}),
            'isBase64Encoded': False
        }
    
    payment_result = create_yukassa_payment(
        shop_id, 
        secret_key, 
        donate_req.amount, 
        donate_req.nickname
    )
    
    if not payment_result['success']:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': payment_result['error']}),
            'isBase64Encoded': False
        }
    
    telegram_message = (
        f'💰 <b>Новый донат!</b>\n\n'
        f'Игрок: <code>{donate_req.nickname}</code>\n'
        f'Сумма: <b>{donate_req.amount} ₽</b>\n'
        f'ID платежа: <code>{payment_result["payment_id"]}</code>'
    )
    
    send_telegram_message(bot_token, chat_id, telegram_message)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'payment_url': payment_result['payment_url'],
            'payment_id': payment_result['payment_id']
        }),
        'isBase64Encoded': False
    }