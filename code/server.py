from flask import Flask, request
from ultralytics import YOLO
import os

app = Flask(__name__)


model = YOLO("yolov5n.pt")

@app.route("/detect", methods=["POST"])
def detect_person():
    if 'file' not in request.files:
        return "no"

    file = request.files["file"]
    save_path = "received.jpg"
    file.save(save_path)

    print("received file:", save_path)
    results = model(save_path)[0]
    results.save(filename="result.jpg")

    for label, conf in zip(results.boxes.cls, results.boxes.conf):
        if model.names[int(label)] == "person" and conf > 0.4:
            print("✅ detect person(conf:", float(conf), "）")
            return "yes"

    print("❌ no person")
    return "no"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)