from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
import json

router = APIRouter(tags=["websockets"])

class GameRoom:
    def __init__(self):
        self.players: List[WebSocket] = []
        self.board: List[Optional[str]] = [None] * 9
        self.turn: str = "X"
        self.winner: Optional[str] = None
        self.is_draw: bool = False
        self.player_map: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket):
        if len(self.players) >= 2:
            await websocket.accept()
            await websocket.send_json({"type": "error", "message": "Room full"})
            await websocket.close()
            return

        await websocket.accept()
        self.players.append(websocket)
        
        # Assign roles
        role = "X" if len(self.players) == 1 else "O"
        self.player_map[websocket] = role
        
        await websocket.send_json({
            "type": "init",
            "role": role,
            "board": self.board,
            "turn": self.turn
        })
        
        if len(self.players) == 2:
            await self.broadcast({"type": "start", "message": "Game started!"})

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.players:
            self.players.remove(websocket)
            role = self.player_map.pop(websocket, None)
            await self.broadcast({
                "type": "opponent_disconnected",
                "message": f"Player {role} left the game."
            })

    async def broadcast(self, data: dict):
        for player in self.players:
            try:
                await player.send_json(data)
            except:
                pass

    def check_winner(self):
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for a, b, c in lines:
            if self.board[a] and self.board[a] == self.board[b] == self.board[a] == self.board[c]:
                return self.board[a], [a, b, c]
        return None, []

    async def handle_move(self, websocket: WebSocket, index: int):
        role = self.player_map.get(websocket)
        if not role or role != self.turn or self.board[index] or self.winner or self.is_draw:
            return

        self.board[index] = role
        winner, line = self.check_winner()
        
        if winner:
            self.winner = winner
            await self.broadcast({
                "type": "update",
                "board": self.board,
                "winner": winner,
                "winning_line": line
            })
        elif all(cell is not None for cell in self.board):
            self.is_draw = True
            await self.broadcast({
                "type": "update",
                "board": self.board,
                "is_draw": True
            })
        else:
            self.turn = "O" if self.turn == "X" else "X"
            await self.broadcast({
                "type": "update",
                "board": self.board,
                "turn": self.turn
            })

    async def reset(self):
        self.board = [None] * 9
        self.turn = "X"
        self.winner = None
        self.is_draw = False
        await self.broadcast({
            "type": "init",
            "board": self.board,
            "turn": self.turn,
            "reset": True
        })

rooms: Dict[str, GameRoom] = {}

@router.websocket("/ws/tictactoe/{room_id}")
async def tictactoe_websocket(websocket: WebSocket, room_id: str):
    if room_id not in rooms:
        rooms[room_id] = GameRoom()
    
    room = rooms[room_id]
    await room.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "move":
                await room.handle_move(websocket, data["index"])
            elif data["type"] == "reset":
                await room.reset()
    except WebSocketDisconnect:
        await room.disconnect(websocket)
        if not room.players:
            del rooms[room_id]
