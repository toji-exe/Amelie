from flask import Flask, request, render_template, redirect, url_for, session
import openai
import os

app = Flask(__name__)
app.secret_key = "amelies-secret-key"

# Set your OpenAI API key securely in environment (don't hardcode in prod)
openai.api_key = os.getenv("OPENAI_API_KEY")

PASSWORD = "ameliepass"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == PASSWORD:
            session["logged_in"] = True
            session["history"] = []
            return redirect(url_for("chat"))
    return render_template("login.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if "history" not in session:
        session["history"] = []

    response = None
    image_url = None
    prompt = ""

    if request.method == "POST":
        prompt = request.form["prompt"]

        # Save user's message
        session["history"].append({"sender": "user", "text": prompt})

        if "generate image" in prompt.lower():
            # Generate an image
            image = openai.Image.create(prompt=prompt, n=1, size="512x512")
            image_url = image["data"][0]["url"]
            response_text = "Here’s your hot little image 😘"
        else:
            # Text response
            chat_completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You're Amelie, a flirty, sarcastic AI girlfriend."},
                    {"role": "user", "content": prompt}
                ]
            )
            response_text = chat_completion.choices[0].message.content

        # Save Amelie’s reply
        session["history"].append({
            "sender": "amelie",
            "text": response_text,
            "image_url": image_url
        })

    return render_template("index.html", history=session["history"])
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
