from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 遊戲變數
ROWS, COLS = 6, 7
board = [[0] * COLS for _ in range(ROWS)]
players = {}  # 存放玩家 socket ID
current_player = 1  # 當前回合玩家
game_over = False

def check_winner():
    """檢查是否有玩家獲勝"""
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == 0:
                continue
            player = board[r][c]

            # 水平檢查
            if c + 3 < COLS and all(board[r][c + i] == player for i in range(4)):
                return player
            # 垂直檢查
            if r + 3 < ROWS and all(board[r + i][c] == player for i in range(4)):
                return player
            # 右下對角線
            if r + 3 < ROWS and c + 3 < COLS and all(board[r + i][c + i] == player for i in range(4)):
                return player
            # 左下對角線
            if r + 3 < ROWS and c - 3 >= 0 and all(board[r + i][c - i] == player for i in range(4)):
                return player
    return 0  # 沒有勝者

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global players
    sid = request.sid

    if len(players) < 2:
        players[sid] = 1 if len(players) == 0 else 2
        join_room("game")
        emit('player_number', {"player": players[sid]}, room=sid)
        print(f"玩家 {players[sid]} 連接，ID: {sid}")
    else:
        emit('spectator', room=sid)

    emit('update_board', {"board": board, "current_player": current_player}, room="game")

@socketio.on('disconnect')
def handle_disconnect():
    global players, current_player
    sid = request.sid

    if sid in players:
        player_num = players[sid]
        del players[sid]
        print(f"玩家 {player_num} 離開，釋放位置")

        # 如果當前玩家離開，自動換對手回合
        if player_num == current_player:
            current_player = 3 - current_player  # 切換到另一名玩家

        emit('player_left', {"player": player_num, "current_player": current_player}, room="game")

@socketio.on('drop_piece')
def handle_drop_piece(data):
    global current_player, game_over
    if game_over:
        return
    
    sid = request.sid
    if players.get(sid) != current_player:
        emit('invalid_move', {"message": "不是你的回合"}, room=sid)
        return

    col = data["column"]
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == 0:
            board[row][col] = current_player
            winner = check_winner()
            if winner:
                game_over = True
                emit('game_over', {"winner": winner}, room="game")
            else:
                current_player = 3 - current_player  # 切換玩家
            emit('update_board', {"board": board, "current_player": current_player}, room="game")
            return
    emit('invalid_move', {"message": "此列已滿"}, room=sid)

@socketio.on('reset_game')
def handle_reset():
    global board, current_player, game_over
    board = [[0] * COLS for _ in range(ROWS)]
    current_player = 1
    game_over = False
    emit('update_board', {"board": board, "current_player": current_player}, room="game")

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
