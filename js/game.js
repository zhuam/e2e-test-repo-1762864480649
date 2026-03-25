/**
 * Tetris Game - 俄罗斯方块
 * A modern implementation with smooth animations
 */

// Game constants
const COLS = 10;
const ROWS = 20;
const BLOCK_SIZE = 30;
const NEXT_BLOCK_SIZE = 25;

// Tetromino definitions
const TETROMINOES = {
    I: {
        shape: [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ],
        color: '#00f0f0'
    },
    O: {
        shape: [
            [1, 1],
            [1, 1]
        ],
        color: '#f0f000'
    },
    T: {
        shape: [
            [0, 1, 0],
            [1, 1, 1],
            [0, 0, 0]
        ],
        color: '#a000f0'
    },
    S: {
        shape: [
            [0, 1, 1],
            [1, 1, 0],
            [0, 0, 0]
        ],
        color: '#00f000'
    },
    Z: {
        shape: [
            [1, 1, 0],
            [0, 1, 1],
            [0, 0, 0]
        ],
        color: '#f00000'
    },
    J: {
        shape: [
            [1, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ],
        color: '#0000f0'
    },
    L: {
        shape: [
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 0]
        ],
        color: '#f0a000'
    }
};

const TETROMINO_KEYS = Object.keys(TETROMINOES);

// Game state
class GameState {
    constructor() {
        this.reset();
    }

    reset() {
        this.board = this.createBoard();
        this.score = 0;
        this.level = 1;
        this.lines = 0;
        this.gameOver = false;
        this.paused = false;
        this.currentPiece = null;
        this.nextPiece = null;
        this.dropInterval = 1000;
        this.lastDrop = 0;
    }

    createBoard() {
        return Array.from({ length: ROWS }, () => Array(COLS).fill(null));
    }
}

// Piece class
class Piece {
    constructor(type) {
        this.type = type;
        this.shape = TETROMINOES[type].shape.map(row => [...row]);
        this.color = TETROMINOES[type].color;
        this.x = Math.floor(COLS / 2) - Math.floor(this.shape[0].length / 2);
        this.y = 0;
    }

    rotate() {
        const n = this.shape.length;
        const rotated = Array.from({ length: n }, () => Array(n).fill(0));
        for (let i = 0; i < n; i++) {
            for (let j = 0; j < n; j++) {
                rotated[j][n - 1 - i] = this.shape[i][j];
            }
        }
        return rotated;
    }
}

// Main game class
class TetrisGame {
    constructor() {
        this.canvas = document.getElementById('gameBoard');
        this.ctx = this.canvas.getContext('2d');
        this.nextCanvas = document.getElementById('nextPiece');
        this.nextCtx = this.nextCanvas.getContext('2d');

        this.state = new GameState();
        this.animationId = null;
        this.clearingLines = [];
        this.clearAnimationTime = 0;

        this.initUI();
        this.bindEvents();
        this.showStartScreen();
    }

    initUI() {
        this.overlay = document.getElementById('gameOverlay');
        this.overlayTitle = document.getElementById('overlayTitle');
        this.overlayScore = document.getElementById('overlayScore');
        this.startBtn = document.getElementById('startBtn');
        this.scoreEl = document.getElementById('score');
        this.levelEl = document.getElementById('level');
        this.linesEl = document.getElementById('lines');
        this.pauseOverlay = document.createElement('div');
        this.pauseOverlay.className = 'pause-overlay hidden';
        this.pauseOverlay.innerHTML = '<div class="pause-text">PAUSED</div>';
        this.canvas.parentElement.appendChild(this.pauseOverlay);
    }

    bindEvents() {
        // Start button
        this.startBtn.addEventListener('click', () => this.startGame());

        // Keyboard controls
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));

        // Prevent spacebar scrolling
        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && e.target === document.body) {
                e.preventDefault();
            }
        });
    }

    showStartScreen() {
        this.overlayTitle.textContent = '俄罗斯方块';
        this.overlayScore.textContent = '按按钮开始游戏';
        this.startBtn.textContent = '开始游戏';
        this.overlay.classList.remove('hidden');
    }

    startGame() {
        this.state.reset();
        this.state.currentPiece = this.randomPiece();
        this.state.nextPiece = this.randomPiece();
        this.state.gameOver = false;
        this.state.paused = false;
        this.clearingLines = [];
        this.updateUI();
        this.draw();
        this.overlay.classList.add('hidden');
        this.pauseOverlay.classList.add('hidden');

        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        this.lastTime = 0;
        this.gameLoop();
    }

    randomPiece() {
        const type = TETROMINO_KEYS[Math.floor(Math.random() * TETROMINO_KEYS.length)];
        return new Piece(type);
    }

    gameLoop(timestamp = 0) {
        if (this.state.gameOver) {
            this.showGameOver();
            return;
        }

        if (!this.state.paused) {
            const deltaTime = timestamp - this.lastTime;
            this.lastTime = timestamp;

            if (deltaTime >= this.state.dropInterval && this.clearingLines.length === 0) {
                this.moveDown();
            }

            this.draw();
        }

        this.animationId = requestAnimationFrame((t) => this.gameLoop(t));
    }

    handleKeyPress(e) {
        if (this.state.gameOver) return;

        // Pause toggle
        if (e.code === 'KeyP') {
            this.togglePause();
            return;
        }

        if (this.state.paused || this.clearingLines.length > 0) return;

        switch (e.code) {
            case 'ArrowLeft':
                this.moveLeft();
                break;
            case 'ArrowRight':
                this.moveRight();
                break;
            case 'ArrowDown':
                this.moveDown();
                break;
            case 'ArrowUp':
                this.rotate();
                break;
            case 'Space':
                this.hardDrop();
                break;
        }
    }

    togglePause() {
        if (this.state.gameOver) return;
        this.state.paused = !this.state.paused;
        this.pauseOverlay.classList.toggle('hidden', !this.state.paused);
    }

    isValidMove(piece, offsetX = 0, offsetY = 0, newShape = null) {
        const shape = newShape || piece.shape;
        for (let y = 0; y < shape.length; y++) {
            for (let x = 0; x < shape[y].length; x++) {
                if (shape[y][x]) {
                    const newX = piece.x + x + offsetX;
                    const newY = piece.y + y + offsetY;

                    if (newX < 0 || newX >= COLS || newY >= ROWS) {
                        return false;
                    }
                    if (newY >= 0 && this.state.board[newY][newX]) {
                        return false;
                    }
                }
            }
        }
        return true;
    }

    moveLeft() {
        if (this.isValidMove(this.state.currentPiece, -1, 0)) {
            this.state.currentPiece.x--;
            this.draw();
        }
    }

    moveRight() {
        if (this.isValidMove(this.state.currentPiece, 1, 0)) {
            this.state.currentPiece.x++;
            this.draw();
        }
    }

    moveDown() {
        if (this.isValidMove(this.state.currentPiece, 0, 1)) {
            this.state.currentPiece.y++;
        } else {
            this.lockPiece();
        }
        this.draw();
    }

    rotate() {
        const rotated = this.state.currentPiece.rotate();
        if (this.isValidMove(this.state.currentPiece, 0, 0, rotated)) {
            this.state.currentPiece.shape = rotated;
            this.draw();
        } else if (this.isValidMove(this.state.currentPiece, 1, 0, rotated)) {
            this.state.currentPiece.x++;
            this.state.currentPiece.shape = rotated;
            this.draw();
        } else if (this.isValidMove(this.state.currentPiece, -1, 0, rotated)) {
            this.state.currentPiece.x--;
            this.state.currentPiece.shape = rotated;
            this.draw();
        }
    }

    hardDrop() {
        while (this.isValidMove(this.state.currentPiece, 0, 1)) {
            this.state.currentPiece.y++;
            this.state.score += 2;
        }
        this.lockPiece();
        this.updateUI();
        this.draw();
    }

    lockPiece() {
        const piece = this.state.currentPiece;
        for (let y = 0; y < piece.shape.length; y++) {
            for (let x = 0; x < piece.shape[y].length; x++) {
                if (piece.shape[y][x]) {
                    const boardY = piece.y + y;
                    const boardX = piece.x + x;
                    if (boardY >= 0) {
                        this.state.board[boardY][boardX] = piece.color;
                    }
                }
            }
        }

        this.checkLines();
        this.state.currentPiece = this.state.nextPiece;
        this.state.nextPiece = this.randomPiece();

        if (!this.isValidMove(this.state.currentPiece, 0, 0)) {
            this.state.gameOver = true;
        }

        this.updateUI();
    }

    checkLines() {
        this.clearingLines = [];

        for (let y = ROWS - 1; y >= 0; y--) {
            if (this.state.board[y].every(cell => cell !== null)) {
                this.clearingLines.push(y);
            }
        }

        if (this.clearingLines.length > 0) {
            this.clearAnimationTime = 300;

            setTimeout(() => {
                for (const lineY of this.clearingLines) {
                    this.state.board.splice(lineY, 1);
                    this.state.board.unshift(Array(COLS).fill(null));
                }

                // Scoring: 1=100, 2=300, 3=500, 4=800
                const scores = [0, 100, 300, 500, 800];
                this.state.score += scores[this.clearingLines.length] * this.state.level;
                this.state.lines += this.clearingLines.length;

                // Level up every 10 lines
                const newLevel = Math.floor(this.state.lines / 10) + 1;
                if (newLevel > this.state.level) {
                    this.state.level = newLevel;
                    this.state.dropInterval = Math.max(100, 1000 - (this.state.level - 1) * 100);
                }

                this.clearingLines = [];
                this.updateUI();
            }, this.clearAnimationTime);
        }
    }

    updateUI() {
        this.scoreEl.textContent = this.state.score;
        this.levelEl.textContent = this.state.level;
        this.linesEl.textContent = this.state.lines;
    }

    showGameOver() {
        this.overlayTitle.textContent = '游戏结束';
        this.overlayScore.textContent = `最终得分：${this.state.score}`;
        this.startBtn.textContent = '再玩一次';
        this.overlay.classList.remove('hidden');
    }

    draw() {
        // Clear canvas
        this.ctx.fillStyle = '#0f0f1a';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid
        this.drawGrid();

        // Draw board
        this.drawBoard();

        // Draw current piece
        if (this.state.currentPiece && !this.state.gameOver) {
            this.drawPiece(this.state.currentPiece);
        }

        // Draw next piece preview
        this.drawNextPiece();

        // Draw ghost piece
        if (this.state.currentPiece && !this.state.gameOver && !this.state.paused) {
            this.drawGhostPiece();
        }
    }

    drawGrid() {
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        this.ctx.lineWidth = 1;

        for (let x = 0; x <= COLS; x++) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * BLOCK_SIZE, 0);
            this.ctx.lineTo(x * BLOCK_SIZE, ROWS * BLOCK_SIZE);
            this.ctx.stroke();
        }

        for (let y = 0; y <= ROWS; y++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * BLOCK_SIZE);
            this.ctx.lineTo(COLS * BLOCK_SIZE, y * BLOCK_SIZE);
            this.ctx.stroke();
        }
    }

    drawBoard() {
        for (let y = 0; y < ROWS; y++) {
            for (let x = 0; x < COLS; x++) {
                const cell = this.state.board[y][x];
                if (cell) {
                    this.drawBlock(x, y, cell);
                }
            }
        }

        // Draw clearing animation
        if (this.clearingLines.length > 0) {
            this.ctx.fillStyle = `rgba(255, 255, 255, ${0.5 + Math.sin(Date.now() / 50) * 0.5})`;
            for (const lineY of this.clearingLines) {
                this.ctx.fillRect(0, lineY * BLOCK_SIZE, COLS * BLOCK_SIZE, BLOCK_SIZE);
            }
        }
    }

    drawPiece(piece, offsetX = 0, offsetY = 0, alpha = 1) {
        for (let y = 0; y < piece.shape.length; y++) {
            for (let x = 0; x < piece.shape[y].length; x++) {
                if (piece.shape[y][x]) {
                    this.drawBlock(
                        piece.x + x + offsetX,
                        piece.y + y + offsetY,
                        piece.color,
                        alpha
                    );
                }
            }
        }
    }

    drawGhostPiece() {
        let ghostY = this.state.currentPiece.y;
        while (this.isValidMove(this.state.currentPiece, 0, ghostY - this.state.currentPiece.y + 1)) {
            ghostY++;
        }

        for (let y = 0; y < this.state.currentPiece.shape.length; y++) {
            for (let x = 0; x < this.state.currentPiece.shape[y].length; x++) {
                if (this.state.currentPiece.shape[y][x]) {
                    const boardX = this.state.currentPiece.x + x;
                    const boardY = ghostY + y;
                    if (boardY >= 0) {
                        this.ctx.fillStyle = this.state.currentPiece.color + '30';
                        this.ctx.fillRect(
                            boardX * BLOCK_SIZE + 1,
                            boardY * BLOCK_SIZE + 1,
                            BLOCK_SIZE - 2,
                            BLOCK_SIZE - 2
                        );
                        this.ctx.strokeStyle = this.state.currentPiece.color + '60';
                        this.ctx.lineWidth = 2;
                        this.ctx.strokeRect(
                            boardX * BLOCK_SIZE + 1,
                            boardY * BLOCK_SIZE + 1,
                            BLOCK_SIZE - 2,
                            BLOCK_SIZE - 2
                        );
                    }
                }
            }
        }
    }

    drawBlock(x, y, color, alpha = 1) {
        const px = x * BLOCK_SIZE;
        const py = y * BLOCK_SIZE;
        const padding = 1;
        const size = BLOCK_SIZE - padding * 2;

        this.ctx.globalAlpha = alpha;

        // Main block
        this.ctx.fillStyle = color;
        this.ctx.fillRect(px + padding, py + padding, size, size);

        // Highlight (top-left)
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        this.ctx.fillRect(px + padding, py + padding, size, 4);
        this.ctx.fillRect(px + padding, py + padding, 4, size);

        // Shadow (bottom-right)
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        this.ctx.fillRect(px + padding, py + padding + size - 4, size, 4);
        this.ctx.fillRect(px + padding + size - 4, py + padding, 4, size);

        // Inner highlight
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        this.ctx.fillRect(px + padding + 6, py + padding + 6, size - 12, size - 12);

        this.ctx.globalAlpha = 1;
    }

    drawNextPiece() {
        this.nextCtx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        this.nextCtx.fillRect(0, 0, this.nextCanvas.width, this.nextCanvas.height);

        if (!this.state.nextPiece) return;

        const piece = this.state.nextPiece;
        const pieceWidth = piece.shape[0].length * NEXT_BLOCK_SIZE;
        const pieceHeight = piece.shape.length * NEXT_BLOCK_SIZE;
        const offsetX = (this.nextCanvas.width - pieceWidth) / 2;
        const offsetY = (this.nextCanvas.height - pieceHeight) / 2;

        for (let y = 0; y < piece.shape.length; y++) {
            for (let x = 0; x < piece.shape[y].length; x++) {
                if (piece.shape[y][x]) {
                    const px = offsetX + x * NEXT_BLOCK_SIZE;
                    const py = offsetY + y * NEXT_BLOCK_SIZE;
                    const size = NEXT_BLOCK_SIZE - 2;

                    this.nextCtx.fillStyle = piece.color;
                    this.nextCtx.fillRect(px + 1, py + 1, size, size);

                    this.nextCtx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                    this.nextCtx.fillRect(px + 1, py + 1, size, 3);
                    this.nextCtx.fillRect(px + 1, py + 1, 3, size);

                    this.nextCtx.fillStyle = 'rgba(0, 0, 0, 0.3)';
                    this.nextCtx.fillRect(px + 1, py + 1 + size - 3, size, 3);
                    this.nextCtx.fillRect(px + 1 + size - 3, py + 1, 3, size);
                }
            }
        }
    }
}

// Initialize game when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.game = new TetrisGame();
});
