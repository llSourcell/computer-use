"""A computer use loop in 40 lines. Screenshot, decide, act, repeat."""
import base64, io, json, pyautogui
from openai import OpenAI

MODEL = "gpt-6-astra"
EFFORT = "high"          # low | medium | high | xhigh | max
MAX_STEPS = 25           # the cap that stops a runaway agent
SYSTEM = (
    "You control a computer by looking at screenshots. You will receive one "
    "screenshot and one task. Return exactly one JSON object with a key called "
    "action, set to click, type, scroll, key or done, plus the fields that action "
    "needs. Coordinates are pixels from the top left of the image. Return no "
    "explanation and no markdown fence. If the task is already complete, return done."
)

client = OpenAI()

def screenshot():
    buf = io.BytesIO()
    pyautogui.screenshot().save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def act(a):
    kind = a.get("action")
    if kind == "click":  pyautogui.click(a["x"], a["y"])
    elif kind == "type": pyautogui.write(a["text"], interval=0.02)
    elif kind == "scroll": pyautogui.scroll(a.get("amount", -500))
    elif kind == "key":  pyautogui.press(a["key"])
    return kind == "done"

def run(task):
    for step in range(MAX_STEPS):
        r = client.responses.create(
            model=MODEL, reasoning={"effort": EFFORT}, instructions=SYSTEM,
            input=[{"role": "user", "content": [
                {"type": "input_text", "text": task},
                {"type": "input_image", "image_url": f"data:image/png;base64,{screenshot()}"}]}])
        a = json.loads(r.output_text)
        print(step, a)
        if act(a): return print("done in", step + 1, "steps")
    print("hit the step cap")

if __name__ == "__main__":
    run("Open the pricing page and read the cached input price.")
