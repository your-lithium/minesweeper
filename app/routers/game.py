from fastapi import APIRouter, Depends
from loguru import logger
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.services import GameService

game_router = APIRouter(
    prefix="/ws/play",
    tags=["game"],
)


@game_router.websocket("/")
async def play(websocket: WebSocket, game_service: GameService = Depends(GameService)) -> None:
    await websocket.accept()
    logger.info("Starting a game...")

    try:
        await game_service.start_game(websocket=websocket)
    except WebSocketDisconnect as wsde:
        logger.warning(f"WebSocket disconnected: {wsde}")
        return
    except ValueError as ve:
        logger.warning(f"ValueError: {ve}")
        await websocket.send_json({"error": str(ve), "status_code": 400})
        await websocket.close()
        return
