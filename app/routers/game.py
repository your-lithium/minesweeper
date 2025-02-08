from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect
from loguru import logger

from app.services import FieldService
from app.core import jinja2_templates


game_router = APIRouter(
    prefix="/ws/play",
    tags=["field"],
)


@game_router.websocket("/")
async def play(
    websocket: WebSocket,
) -> None:
    try:
        await websocket.accept()
        logger.info("Starting a game...")
        
        request_body = await websocket.receive_json()
        start = tuple(request_body["start"])
        field_service = FieldService(
            start=start,
            mines=request_body["mines"],
            height=request_body["height"],
            width=request_body["width"]
        )
        result = field_service.check_cell(coordinates=start)
        await websocket.send_text(result)
        logger.info(f"Game started with a first click at {request_body['start']}")
        while True:
            cell = await websocket.receive_json()
            logger.info(f"The user chose cell {cell}")
            result = field_service.check_cell(coordinates=tuple(cell))
            logger.info(f"Sending the result: {result}")
            await websocket.send_text(result)
    except WebSocketDisconnect as e:
        logger.warning(f"WebSocket disconnected: {e}")
        return
