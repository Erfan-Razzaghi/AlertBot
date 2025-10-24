from fastapi import HTTPException, APIRouter
from handlers.sms_handler.sms_handler import SMSHandler
from handlers.sms_handler.exceptions import SMSValidationError, SMSSendError
from handlers.telegram_handler.telegram_handler import TelegramHandler
from .. import env
import logging

# this route is only used for testing purposes in stage
router = APIRouter(
    prefix="/tests",
    tags=["tests"]    
)

test_logger = logging.getLogger()

@router.post("/telegram")
async def root():
    try:
        bot = TelegramHandler()
        await TelegramHandler().send_alert_message(chat_id=env.TG_GROUP_TEST_ID, text="Hello World From Alertbot")
        return {"message": "Message sent to telegram"}
    except Exception as e:
        print(f"Failed to send telegram message: {e}")
        return HTTPException(500,detail=f"Failed to send telegram message after {env.TG_SEND_RETRIES} attempts")

@router.post("/sms")
async def test_sms_bulk():
    try:
        sms_sender = SMSHandler(api_key=env.KAVENEGAR_API_KEY)
        sms_sender.send_sms(
            sender="2000008700",
            receptors=["NUMBER1", "NUMBER2"], 
            message="Hello World From Alertbot Bulk",
            cluster="test"
        )
        return {"message": "Bulk SMS sent successfully"}
    except SMSValidationError as e:
        return HTTPException(status_code=400, detail=str(e))
    except SMSSendError as e:
        return HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")