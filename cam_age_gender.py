import cv2
import time
from insightface.app import FaceAnalysis

def ema(alpha=0.3, init=None):
    state = {"y": init, "a": float(alpha)}
    def step(x):
        y = state["y"]; a = state["a"]; x = float(x)
        state["y"] = x if y is None else (a*x + (1.0-a)*y)
        return state["y"]
    return step

def open_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)  # macOS-friendly backend
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera. Allow Terminal in System Settings → Privacy & Security → Camera.")
    return cap

def main():
    app = FaceAnalysis(name="buffalo_l")        # detector + age/gender
    app.prepare(ctx_id=0, det_size=(640, 640))  # CPU

    cap = open_camera()
    font = cv2.FONT_HERSHEY_SIMPLEX

    age_smoothers = {}
    def key_for_bbox(b):
        x1, y1, x2, y2 = map(int, b)
        return (x1//24, y1//24, x2//24, y2//24)

    last_ts = time.time(); frames = 0; fps = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        faces = app.get(frame)

        # FPS
        frames += 1
        now = time.time()
        if now - last_ts >= 1.0:
            fps = frames / (now - last_ts)
            frames = 0
            last_ts = now
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), font, 0.8, (255, 255, 255), 2)

        for f in faces:
            x1, y1, x2, y2 = map(int, f.bbox)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            gender = "Male" if getattr(f, "gender", 1) == 1 else "Female"
            age_raw = int(getattr(f, "age", 0))

            k = key_for_bbox(f.bbox)
            if k not in age_smoothers:
                age_smoothers[k] = ema(alpha=0.3, init=age_raw)
            age = int(age_smoothers[k](age_raw))

            label = f"Age: {age} | Gender: {gender}"
            cv2.putText(frame, label, (x1, max(0, y1 - 10)), font, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow("Age & Gender (ESC to quit)", frame)
        if (cv2.waitKey(1) & 0xFF) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
PY
