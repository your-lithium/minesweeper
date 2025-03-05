from loguru import logger
from starlette.websockets import WebSocket

from app.schemas import Cell, GameResponse
from app.services import FieldService


class GameService:
    def __init__(self) -> None:
        self.websocket: WebSocket | None = None
        self.field_service: FieldService | None = None

    async def start_game(self, websocket: WebSocket) -> None:
        """Start the game — wait for the first click, initialise the FieldService
        with requested parameters and listen for new user input.

        Args:
            websocket (WebSocket): The WebSocket to listen on and send data through.

        Raises:
            ValueError: If the first payload is in bad format.
        """
        self.websocket = websocket
        request_body = await self.receive_click(first=True)
        assert isinstance(request_body, dict)

        if request_body["type"] == "start":
            start = Cell.from_sequence(request_body["start"])
            self.field_service = FieldService(
                start=start, n_mines=request_body["mines"], height=request_body["height"], width=request_body["width"]
            )

            result: GameResponse | None = self.field_service.check_cell(cell=start)
            await self.send_result(result)
            logger.info(f"Game started with a first click at {request_body['start']}")

            while True:
                await self.process_click()
        else:
            raise ValueError("Incorrect starting payload.")

    async def process_click(self) -> None:
        """Process the following clicks received from frontend."""
        assert self.field_service is not None
        request_type, request_cell = await self.receive_click()

        if request_type == "click":
            logger.info(f"The user chose cell {request_cell}")
            result = self.field_service.check_cell(cell=request_cell)
            await self.send_result(result)
        elif request_type == "flag":
            logger.info(f"The user flagged cell {request_cell}")
            self.field_service.flag_cell(cell=request_cell)
        elif request_type == "remove_flag":
            logger.info(f"The user unflagged cell {request_cell}")
            self.field_service.flag_cell(cell=request_cell, remove_flag=True)
        elif request_type == "check_neighbours":
            logger.info(f"The user checked neighbours of cell {request_cell}")
            result = self.field_service.check_neighbouring_cells(cell=request_cell)
            await self.send_result(result)

        if self.field_service.check_win():
            await self.send_result(GameResponse(status="win"))

    async def receive_click(self, first: bool = False) -> dict | tuple[str, Cell]:
        """Receive click payload from frontend and parse it into request type and request cell.

        Returns:
            tuple[str, Cell]: The resulting request type and request cell.
        """
        assert self.websocket is not None
        request_body = await self.websocket.receive_json()
        if first:
            return request_body
        return request_body["type"], Cell.from_sequence(request_body["cell"])

    async def send_result(self, result: GameResponse | None) -> None:
        """Send the payload with results back to frontend.

        Args:
            result (GameResponse | None): The result to send.
        """
        if result and self.websocket:
            logger.info(f"Sending the result: {result}")
            await self.websocket.send_json(result.model_dump())
