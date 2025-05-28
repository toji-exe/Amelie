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
    app.run(host="0.0.0.0", port=port)