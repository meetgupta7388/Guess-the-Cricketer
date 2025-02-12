from flask import Flask, jsonify, render_template, request, session
import os
import requests
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# Fetch API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_player_hints():
    prompt = """
You are a cricket expert. First, randomly select one country from: Afghanistan, Australia, Bangladesh, England, India, Pakistan, New Zealand, Sri Lanka, South Africa, West Indies. Then, randomly select a well-known cricket player from that country who has played at least one match after 2010 (ensure this by mentioning a match or achievement after 2010 in the hints). Provide exactly 9 hints about the player, progressing from vague to very specific. Follow this exact format with no other text or explanations:

[First hint: Primarily their role (batting all-rounder/bowling all-rounder/specialist batsman/specialist bowler) and which country they represent]
[Second hint: Player's debut year and their batting and bowling hand]
[Third hint: Player's Test, ODI, and T20 stats]
[Fourth hint: IPL teams they have played for and in which years]
[Fifth hint: Major achievements or records]
[Sixth hint: Last match played by the player]
[Seventh hint: ICC tournaments the player participated in and the years]
[Eighth hint: Whether the player is retired or not (if retired, mention the year)]
[Nineth hint: Height of player]

Answer: [Player Name]

Important rules to follow strictly:
1. Player MUST have played at least one match after 2010
2. Include recent achievements or matches from 2010 onwards
3. For active players, mention recent performances
4. For retired players, ensure their retirement was after 2010
5. Be specific about IPL appearances after 2010
6. Include recent ICC tournament appearances
7. Stats should include matches played after 2010
8. Format hints exactly as shown above with no variations
9. No additional text before or after the hints
10. Keep the answer format exactly as specified
"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8
            }
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None, None

        # Extract API response
        data = response.json()
        raw_text = data["choices"][0]["message"]["content"].strip()

        # Debugging: Print full response
        print("==== RAW API RESPONSE ====")
        print(raw_text)
        print("==========================")

        return parse_api_response(raw_text)

    except Exception as e:
        print(f"Exception: {str(e)}")
        return None, None

def parse_api_response(raw_response):
    hints = []
    player_name = None

    # Split the response into lines
    lines = raw_response.strip().split('\n')
    
    # Process each line
    for line in lines:
        line = line.strip()
        if line.startswith('['):
            # Extract hint from within square brackets and remove the numbering prefix
            hint = line[1:-1]  # Remove the square brackets
            # Remove the "First hint:", "Second hint:", etc. prefix
            if ':' in hint:
                hint = hint.split(':', 1)[1].strip()
            hints.append(hint)
        elif line.startswith('Answer:'):
            # Extract player name after "Answer:"
            player_name = line.replace('Answer:', '').strip()

    return hints, player_name

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_game", methods=["GET"])
def start_game():
    hints, player = get_player_hints()
    print(f"Hints: {hints}, Player: {player}")  # Debugging output

    if hints and player:
        session["correct_player"] = player  # Store correct answer in session
        return jsonify({"status": "success", "hints": hints})  # Hide answer from client
    else:
        return jsonify({"status": "error", "message": "Failed to retrieve valid hints from Groq."})

@app.route("/check_answer", methods=["POST"])
def check_answer():
    user_guess = request.json.get("guess", "").strip().lower()
    correct_player = session.get("correct_player", "").strip().lower()

    if not correct_player:
        return jsonify({"status": "error", "message": "No active game. Please start a new game."})

    if user_guess == correct_player:
        return jsonify({
            "status": "correct", 
            "message": f"🎉 Congratulations! You correctly guessed {correct_player.title()}!"
        })
    else:
        return jsonify({
            "status": "incorrect",
            "message": "❌ Incorrect guess. Try again!",
            "correct_answer": correct_player  # Send correct player when game is over
        })

if __name__ == "__main__":
    app.run(debug=True)