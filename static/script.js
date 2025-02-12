let currentHints = [];
let hintIndex = 0;
let playerName = "";

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("startBtn").addEventListener("click", startGame);
    
    document.getElementById("guessInput").addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            checkGuess();
        }
    });
});

async function startGame() {
    // Reset game state
    hintIndex = 0;
    const hintSection = document.getElementById("hintSection");
    const hintsElement = document.getElementById("hints");
    const messageElement = document.getElementById("message");
    const guessInput = document.getElementById("guessInput");
    const startBtn = document.getElementById("startBtn");
    const gameControls = document.getElementById("gameControls");

    // Initial UI setup
    hintSection.style.display = "none";
    hintsElement.innerText = "Loading...";
    messageElement.innerText = "";
    messageElement.className = "";
    guessInput.value = "";
    startBtn.style.display = "none";

    try {
        const response = await fetch("/start_game");
        const data = await response.json();

        if (data.status === "success") {
            currentHints = data.hints;
            
            hintSection.style.display = "block";
            hintsElement.innerText = currentHints[hintIndex];
            
            gameControls.style.display = "block";
            
            guessInput.disabled = false;
            guessInput.focus();
        } else {
            hintsElement.innerText = "Error! Please try again.";
            startBtn.style.display = "block";
            gameControls.style.display = "none";
        }
    } catch (error) {
        hintsElement.innerText = "Connection error. Please try again!";
        startBtn.style.display = "block";
        gameControls.style.display = "none";
    }
}

async function checkGuess() {
    const guessInput = document.getElementById("guessInput");
    const messageElement = document.getElementById("message");
    const guess = guessInput.value.trim();

    if (!guess) {
        messageElement.innerText = "Please enter a guess!";
        messageElement.className = "incorrect";
        return;
    }

    try {
        const response = await fetch("/check_answer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ guess: guess })
        });

        const data = await response.json();

        if (data.status === "correct") {
            messageElement.innerHTML = `🎉 Congratulations! You got it right!<br>The player was ${guess}!`;
            messageElement.className = "correct";
            document.getElementById("gameControls").style.display = "none";
            showRestartButton();
        } else {
            if (hintIndex < currentHints.length - 1) {
                hintIndex++;
                document.getElementById("hints").innerText = currentHints[hintIndex];
                guessInput.value = "";
                messageElement.innerText = "Try again with this new hint!";
                messageElement.className = "incorrect";
                guessInput.focus();
            } else {
                messageElement.innerHTML = `Game Over! The player was ${data.correct_answer}`;
                messageElement.className = "incorrect";
                document.getElementById("gameControls").style.display = "none";
                showRestartButton();
            }
        }
    } catch (error) {
        messageElement.innerText = "Error checking your guess. Please try again!";
        messageElement.className = "incorrect";
    }
}

function showRestartButton() {
    const restartButton = document.createElement("button");
    restartButton.innerText = "Play Again";
    restartButton.id = "startBtn";
    restartButton.onclick = startGame;
    document.querySelector(".game-container").appendChild(restartButton);
}