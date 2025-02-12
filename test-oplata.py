from yookassa import Configuration, Payment
import uuid
import json

def create_payment(amount, currency='RUB', description='Test payment'):
    try:
        # Configure YooKassa with correct shop ID
        Configuration.account_id = '1031560'
        Configuration.secret_key = 'test_4PDdPrgo5NyuyXiy1lF7-JSdkLbA3cJ9WkL_6P4pcv0'
        
        # Generate idempotence key
        idempotence_key = str(uuid.uuid4())
        
        # Create payment
        payment = Payment.create({
            "amount": {
                "value": amount,
                "currency": currency
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://getecu.ru"
            },
            "capture": True,
            "description": description,
            "metadata": {
                "order_id": str(uuid.uuid4())
            }
        }, idempotence_key)

        return {
            'success': True,
            'payment_id': payment.id,
            'payment_url': payment.confirmation.confirmation_url,
            'status': payment.status
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }

if __name__ == "__main__":
    # Create a test payment for 1 RUB
    result = create_payment("1.00")
    print(json.dumps(result, indent=2, ensure_ascii=False))
