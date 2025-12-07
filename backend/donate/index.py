import json
import os
import urllib.request
import urllib.error
from typing import Dict, Any
from pydantic import BaseModel, Field


class DonateRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50)
    amount: int = Field(..., gt=0, le=1000000)


class ConfirmRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50)
    amount: int = Field(..., gt=0, le=1000000)
    payment_id: str = Field(..., min_length=1)


def send_telegram_message_with_buttons(bot_token: str, chat_id: str, message: str, payment_id: str) -> bool:
    '''Отправка сообщения в Telegram с inline кнопками'''
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = json.dumps({
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'reply_markup': {
            'inline_keyboard': [[
                {
                    'text': '✅ Оплатил',
                    'callback_data': f'paid_{payment_id}'
                },
                {
                    'text': '❌ Не оплатил',
                    'callback_data': f'notpaid_{payment_id}'
                }
            ]]
        }
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


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    '''Отправка простого сообщения в Telegram'''
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


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Отправка реквизитов карты и уведомлений в Telegram
    Args: event - содержит httpMethod, body с nickname и amount, path для разных endpoint
          context - объект с атрибутами request_id, function_name
    Returns: HTTP ответ с данными или ошибкой
    '''
    method: str = event.get('httpMethod', 'GET')
    path: str = event.get('params', {}).get('path', '')
    
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
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Invalid JSON: {str(e)}'}),
            'isBase64Encoded': False
        }
    
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
    
    if not bot_token or not chat_id:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Server configuration error'}),
            'isBase64Encoded': False
        }
    
    if 'confirm' in path or body_data.get('action') == 'confirm':
        try:
            confirm_req = ConfirmRequest(**body_data)
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
        
        telegram_message = (
            f'✅ <b>Пользователь подтвердил оплату!</b>\n\n'
            f'Игрок: <code>{confirm_req.nickname}</code>\n'
            f'Сумма: <b>{confirm_req.amount} ₽</b>\n'
            f'ID платежа: <code>{confirm_req.payment_id}</code>'
        )
        
        send_telegram_message(bot_token, chat_id, telegram_message)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'success': True}),
            'isBase64Encoded': False
        }
    
    try:
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
    
    payment_id = f'{donate_req.nickname}_{donate_req.amount}_{context.request_id[:8]}'
    
    telegram_message = (
        f'💰 <b>Новый донат!</b>\n\n'
        f'Игрок: <code>{donate_req.nickname}</code>\n'
        f'Сумма: <b>{donate_req.amount} ₽</b>\n'
        f'ID платежа: <code>{payment_id}</code>\n\n'
        f'Реквизиты карты: <code>2200 7020 5523 2552</code>'
    )
    
    send_telegram_message_with_buttons(bot_token, chat_id, telegram_message, payment_id)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'card_number': '2200 7020 5523 2552',
            'payment_id': payment_id
        }),
        'isBase64Encoded': False
    }
