from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect
from loguru import logger

from app.services import FieldService


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
        if request_body["type"] == "start":
            start = tuple(request_body["start"])
            field_service = FieldService(
                start=start,
                mines=request_body["mines"],
                height=request_body["height"],
                width=request_body["width"]
            )
            
            result = field_service.check_cell(coordinates=start)
            await websocket.send_json(result)
            logger.info(f"Game started with a first click at {request_body['start']}")
            
            while True:
                request_body = await websocket.receive_json()
                request_type = request_body["type"]
                request_cell = tuple(request_body['cell'])
                
                if request_type == "click":
                    logger.info(f"The user chose cell {request_cell}")
                    result = field_service.check_cell(coordinates=request_cell)
                    logger.info(f"Sending the result: {result}")
                    await websocket.send_json(result)
                elif request_type == "flag":
                    logger.info(f"The user flagged cell {request_cell}")
                    field_service.flag_cell(coordinates=request_cell)
                elif request_type == "remove_flag":
                    logger.info(f"The user unflagged cell {request_cell}")
                    field_service.flag_cell(coordinates=request_cell, remove_flag=True)
    except WebSocketDisconnect as e:
        logger.warning(f"WebSocket disconnected: {e}")
        return
