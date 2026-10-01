from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html><body style="font-family:sans-serif; text-align:center; padding:40px; background:#f0f0f0;">
    <h1>FitBuddy - AI Fitness Plan 💪</h1>
    <p>Goal & Level kudunga, plan ready!</p>
    <form method="post" action="/generate">
        <input name="goal" placeholder="Goal: Weight Loss / Muscle Gain" required style="padding:12px; width:300px; border-radius:8px;"><br><br>
        <input name="level" placeholder="Level: Beginner / Intermediate" required style="padding:12px; width:300px; border-radius:8px;"><br><br>
        <button type="submit" style="padding:12px 25px; background:#28a745; color:white; border:none; border-radius:8px; font-size:16px;">Generate Plan</button>
    </form>
    </body></html>
    """

@app.post("/generate", response_class=HTMLResponse)
def generate(goal: str = Form(...), level: str = Form(...)):
    return f"""
    <html><body style="font-family:sans-serif; padding:30px; max-width:700px; margin:auto;">
    <h2>Your Fitness Plan for {goal} - {level}</h2>
    <hr>
    <h3>🏋️ 7-Day Workout Plan</h3>
    <ul>
        <li><b>Day 1:</b> Chest & Triceps - Pushups, Bench Press</li>
        <li><b>Day 2:</b> Back & Biceps - Pullups, Rows</li>
        <li><b>Day 3:</b> Legs - Squats, Lunges</li>
        <li><b>Day 4:</b> Cardio & Core - Running, Planks</li>
        <li><b>Day 5:</b> Shoulders - Shoulder Press</li>
        <li><b>Day 6:</b> Full Body HIIT</li>
        <li><b>Day 7:</b> Rest & Recovery</li>
    </ul>
    <h3>🥗 Nutrition Tips</h3>
    <p>For {goal}: Eat more protein, drink 3L water, avoid junk food. Daily 2000 calories target.</p>
    <br><a href="/" style="text-decoration:none; background:#007bff; color:white; padding:10px 20px; border-radius:5px;">Create Another Plan</a>
    </body></html>
    """