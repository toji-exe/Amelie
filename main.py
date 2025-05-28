import os
from flask import Flask, render_template, request, redirect, session
import openai

app = Flask(__name__)
app.secret_key = os.urandom(24)

PASSWORD = "ameliepass"
BOT_NAME = "Amelie"

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Store chat history in session
def get_history():
    if "history" not in session:
        session["history"] = []
    return session["history"]

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == PASSWORD:
            session["logged_in"] = True
            session["history"] = []
            return redirect("/chat")
        else:
            return render_template("login.html", error="Wrong password, try again!")
    return render_template("login.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if not session.get("logged_in"):
        return redirect("/")
    history = get_history()
    user_input = None
    bot_response = None

    if request.method == "POST":
        user_input = request.form.get("message")
        if user_input:
            history.append({"role": "user", "content": user_input})

            # Decide if image generation is requested
            if "generate image" in user_input.lower():
                prompt = user_input.lower().replace("generate image", "").strip()
                if not prompt:
                    prompt = "a beautiful fantasy landscape"
                try:
                    response = openai.Image.create(
                        prompt=prompt,
                        n=1,
                        size="512x512"
                    )
                    image_url = response['data'][0]['url']
                    bot_response = f"<img src='{image_url}' alt='Generated Image' style='max-width:300px;' />"
                except Exception as e:
                    bot_response = f"Sorry, I couldn't generate the image. Error: {str(e)}"
            else:
                # Chat completion
                messages = [{"role": "system", "content": f"You are {BOT_NAME}, a feminine, sarcastic, flirty, and funny AI bot. Remember the conversation."}]
                messages.extend(history)
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=200,
                        temperature=0.8,
                    )
                    bot_response = response.choices[0].message.content
                except Exception as e:
                    bot_response = "Oops, something went wrong with the AI response."

            history.append({"role": "assistant", "content": bot_response})

    return render_template("index.html", history=history, bot_response=bot_response)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)from flask import Flask, request, render_template, redirect, url_for, session
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
