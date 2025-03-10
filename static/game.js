const socket = io();
let playerNumber = 0;
let currentTurn = 1;
let resetClickCount = 0;
let resetTimer = null;

socket.on("player_number", (data) => {
    playerNumber = data.player;
    document.getElementById("player-info").innerText = `你是玩家 ${playerNumber}`;
});

socket.on("update_board", (data) => {
    currentTurn = data.current_player;
    updateTurnInfo();
    drawBoard(data.board);
});

socket.on("game_over", (data) => {
    alert(`玩家 ${data.winner} 獲勝！`);
});

socket.on("game_full", () => {
    alert("遊戲人數已滿！");
});

socket.on("invalid_move", (data) => {
    alert(data.message);
});

function dropPiece(col) {
    if (playerNumber !== currentTurn) {
        alert("現在不是你的回合！");
        return;
    }
    socket.emit("drop_piece", { column: col });
}

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

function updateTurnInfo() {
    document.getElementById("turn-info").innerText = `現在輪到玩家 ${currentTurn} 落子`;
}

function drawBoard(board) {
    const boardDiv = document.getElementById("game-board");
    boardDiv.innerHTML = "";

    const letters = "ABCDEFG";
    
    for (let r = 0; r < 6; r++) {
        for (let c = 0; c < 7; c++) {
            const cell = document.createElement("div");
            cell.classList.add("cell");
            cell.innerText = `${letters[c]}${r + 1}`;
            if (board[r][c] === 1) cell.classList.add("player1");
            if (board[r][c] === 2) cell.classList.add("player2");
            cell.onclick = () => dropPiece(c);
            boardDiv.appendChild(cell);
        }
    }
}
