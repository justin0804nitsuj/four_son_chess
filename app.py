from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 遊戲變數
ROWS, COLS = 6, 7
board = [[0] * COLS for _ in range(ROWS)]
players = {}  # 存放玩家 socket ID
player_slots = {1: None, 2: None}  # 追蹤哪個玩家在哪個位置
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
    """當玩家連接時"""
    global players, player_slots

    sid = request.sid  # ✅ 修正這裡，從 request.sid 獲取 session ID

    # 分配玩家 1 或 玩家 2
    assigned_player = None
    if player_slots[1] is None:
        player_slots[1] = sid
        assigned_player = 1
    elif player_slots[2] is None:
        player_slots[2] = sid
        assigned_player = 2

    if assigned_player:
        players[sid] = assigned_player
        join_room("game")
        emit('player_number', {"player": assigned_player}, room=sid)
        print(f"玩家 {assigned_player} 連接，ID: {sid}")
    else:
        emit('spectator', room=sid)  # 超過 2 人的變成觀戰者

    # 發送最新的棋盤給所有玩家
    emit('update_board', {"board": board, "current_player": current_player}, room="game")

@socketio.on('disconnect')
def handle_disconnect():
    """當玩家斷線時"""
    global players, player_slots, current_player

    sid = request.sid  # ✅ 修正這裡，從 request.sid 獲取 session ID

    if sid in players:
        player_num = players[sid]
        del players[sid]
        player_slots[player_num] = None  # 釋放該玩家的位置
        print(f"玩家 {player_num} 離開，釋放位置")

        # 如果當前玩家離開，自動換對手回合
        if player_num == current_player:
            current_player = 3 - current_player  # 切換到另一名玩家

        emit('player_left', {"player": player_num, "current_player": current_player}, room="game")

@socketio.on('drop_piece')
def handle_drop_piece(data):
    """當玩家落子時"""
    global current_player, game_over
    if game_over:
        return
    
    sid = request.sid  # ✅ 修正這裡，從 request.sid 獲取 session ID
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
    """重新開始遊戲"""
    global board, current_player, game_over
    board = [[0] * COLS for _ in range(ROWS)]
    current_player = 1
    game_over = False
    emit('update_board', {"board": board, "current_player": current_player}, room="game")

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
