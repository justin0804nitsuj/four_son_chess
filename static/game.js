const socket = io();
let playerNumber = 0;
let currentTurn = 1;
let resetClickCount = 0;
let resetTimer = null;

// 取得玩家編號
socket.on("player_number", (data) => {
    playerNumber = data.player;
    document.getElementById("player-info").innerText = `你是玩家 ${playerNumber}`;
});

// 更新棋盤狀態
socket.on("update_board", (data) => {
    currentTurn = data.current_player;
    updateTurnInfo();
    drawBoard(data.board);
});

// 當有玩家獲勝
socket.on("game_over", (data) => {
    alert(`玩家 ${data.winner} 獲勝！`);
});

// 如果遊戲已滿，進入觀戰模式
socket.on("spectator", () => {
    document.getElementById("player-info").innerText = "你正在觀戰";
});

// 當有玩家離開時，通知對手
socket.on("player_left", (data) => {
    alert(`玩家 ${data.player} 已離開！\n現在輪到玩家 ${data.current_player}。`);
});

// 無效移動（例如：不輪到你、列滿）
socket.on("invalid_move", (data) => {
    alert(data.message);
});

// 落子功能
function dropPiece(col) {
    if (playerNumber !== currentTurn) {
        alert("現在不是你的回合！");
        return;
    }
    socket.emit("drop_piece", { column: col });
}

// 重新開始遊戲（連點 3 下才能生效）
function resetGame() {
    resetClickCount++;

    // 更新按鈕顯示點擊次數
    let resetButton = document.getElementById("reset-button");
    resetButton.innerText = `連點 ${3 - resetClickCount} 下以重新開始`;

    // 若是第一次點擊，啟動 2 秒計時器
    if (resetClickCount === 1) {
        resetTimer = setTimeout(() => {
            resetClickCount = 0;
            resetButton.innerText = "連點3下以重新開始";
        }, 2000);
    }

    // 當點擊次數達到 3 次，執行重置
    if (resetClickCount >= 3) {
        clearTimeout(resetTimer);
        resetClickCount = 0;
        resetButton.innerText = "連點3下以重新開始";
        socket.emit("reset_game");
    }
}

// 更新當前回合資訊
function updateTurnInfo() {
    document.getElementById("turn-info").innerText = `現在輪到玩家 ${currentTurn} 落子`;
}

// 畫出棋盤
function drawBoard(board) {
    const boardDiv = document.getElementById("game-board");
    boardDiv.innerHTML = "";

    const letters = "ABCDEFG";  // 列標籤

    for (let r = 0; r < 6; r++) {
        for (let c = 0; c < 7; c++) {
            const cell = document.createElement("div");
            cell.classList.add("cell");
            cell.innerText = `${letters[c]}${r + 1}`;  // 顯示格子編號，例如 A1, B3

            // 根據玩家顏色填充格子
            if (board[r][c] === 1) cell.classList.add("player1");
            if (board[r][c] === 2) cell.classList.add("player2");

            cell.onclick = () => dropPiece(c);
            boardDiv.appendChild(cell);
        }
    }
}
