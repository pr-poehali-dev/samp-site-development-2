import json
import os
import urllib.request
import urllib.error
import pymysql
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class DonateRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50)
    amount: int = Field(..., gt=0, le=1000000)


class ConfirmRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50)
    amount: int = Field(..., gt=0, le=1000000)
    payment_id: str = Field(..., min_length=1)


def send_telegram_message_with_buttons(bot_token: str, chat_id: str, message: str, payment_id: str) -> Dict[str, Any]:
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
            result = json.loads(response.read().decode('utf-8'))
            print(f'Telegram API response: {result}')
            return {'success': True, 'data': result}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f'Telegram API error: {error_body}')
        return {'success': False, 'error': error_body}
    except Exception as e:
        print(f'Telegram send error: {str(e)}')
        return {'success': False, 'error': str(e)}


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> Dict[str, Any]:
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
            result = json.loads(response.read().decode('utf-8'))
            print(f'Telegram API response: {result}')
            return {'success': True, 'data': result}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f'Telegram API error: {error_body}')
        return {'success': False, 'error': error_body}
    except Exception as e:
        print(f'Telegram send error: {str(e)}')
        return {'success': False, 'error': str(e)}


def add_donate_to_samp_db(nickname: str, amount: int) -> Dict[str, Any]:
    '''Добавление донат рублей игроку в базу данных SAMP сервера'''
    host = os.environ.get('SAMP_DB_HOST', '')
    port = int(os.environ.get('SAMP_DB_PORT', '3306'))
    user = os.environ.get('SAMP_DB_USER', '')
    password = os.environ.get('SAMP_DB_PASSWORD', '')
    database = os.environ.get('SAMP_DB_NAME', '')
    table = os.environ.get('SAMP_DB_TABLE', 'players')
    column_name = 'Name'
    column_donate = os.environ.get('SAMP_DB_COLUMN_DONATE', 'Donate')
    
    if not all([host, user, password, database]):
        print('Missing SAMP database configuration')
        return {'success': False, 'error': 'Database configuration missing'}
    
    connection: Optional[pymysql.connections.Connection] = None
    
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=10
        )
        
        with connection.cursor() as cursor:
            sql = f"UPDATE `{table}` SET `{column_donate}` = `{column_donate}` + %s WHERE `{column_name}` = %s"
            rows_affected = cursor.execute(sql, (amount, nickname))
            connection.commit()
            
            if rows_affected == 0:
                print(f'Player {nickname} not found in database')
                return {'success': False, 'error': 'Player not found'}
            
            print(f'Successfully added {amount} donate rubles to {nickname}')
            return {'success': True, 'rows_affected': rows_affected}
            
    except pymysql.MySQLError as e:
        print(f'MySQL error: {str(e)}')
        return {'success': False, 'error': f'Database error: {str(e)}'}
    except Exception as e:
        print(f'Error adding donate: {str(e)}')
        return {'success': False, 'error': str(e)}
    finally:
        if connection:
            connection.close()


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
        
        db_result = add_donate_to_samp_db(confirm_req.nickname, confirm_req.amount)
        
        if db_result.get('success'):
            telegram_message = (
                f'✅ <b>Пользователь подтвердил оплату!</b>\n\n'
                f'Игрок: <code>{confirm_req.nickname}</code>\n'
                f'Сумма: <b>{confirm_req.amount} ₽</b>\n'
                f'ID платежа: <code>{confirm_req.payment_id}</code>\n\n'
                f'💎 Донат рубли успешно добавлены в базу данных!'
            )
        else:
            telegram_message = (
                f'⚠️ <b>Пользователь подтвердил оплату, но возникла проблема!</b>\n\n'
                f'Игрок: <code>{confirm_req.nickname}</code>\n'
                f'Сумма: <b>{confirm_req.amount} ₽</b>\n'
                f'ID платежа: <code>{confirm_req.payment_id}</code>\n\n'
                f'❌ Ошибка базы данных: {db_result.get("error", "Unknown error")}\n'
                f'Проверьте настройки подключения к MySQL!'
            )
        
        send_telegram_message(bot_token, chat_id, telegram_message)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'db_success': db_result.get('success', False),
                'db_error': db_result.get('error')
            }),
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
    
    print(f'Processing donate: nickname={donate_req.nickname}, amount={donate_req.amount}')
    print(f'Bot token length: {len(bot_token)}, Chat ID: {chat_id}')
    
    telegram_message = (
        f'💰 <b>Новый донат!</b>\n\n'
        f'Игрок: <code>{donate_req.nickname}</code>\n'
        f'Сумма: <b>{donate_req.amount} ₽</b>\n'
        f'ID платежа: <code>{payment_id}</code>\n\n'
        f'Реквизиты карты: <code>2200 7020 5523 2552</code>'
    )
    
    telegram_result = send_telegram_message_with_buttons(bot_token, chat_id, telegram_message, payment_id)
    print(f'Telegram send result: {telegram_result}')
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'card_number': '2200 7020 5523 2552',
            'payment_id': payment_id,
            'telegram_sent': telegram_result.get('success', False)
        }),
        'isBase64Encoded': False
    }