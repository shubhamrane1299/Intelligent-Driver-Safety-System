import torch
from torchvision import models, transforms
from PIL import Image
import cv2
import os

classes = ['Normal','Drowsy','Yawning','Mobile']

model = None

# ✅ LOAD ONLY IF MODEL EXISTS
if os.path.exists("model.pth"):
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = torch.nn.Linear(model.last_channel, len(classes))
    model.load_state_dict(torch.load("model.pth", map_location="cpu"))
    model.eval()

tf = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

def predict(frame):
    if model is None:
        return "Normal"   # 🔥 fallback (no crash)

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = tf(img).unsqueeze(0)

    with torch.no_grad():
        out = model(img)
        idx = torch.argmax(out).item()

    return classes[idx]