import os; os.environ["PYOPENGL_PLATFORM"] = "wgl"
import numpy as np; np.bool = bool
import sys
sys.path.insert(0, os.path.abspath("hamer_code/hamer-main"))
from hamer.models import load_hamer
import torch

CKPT = r"D:\hamer_data\_DATA\hamer_ckpts\checkpoints\hamer.ckpt"
os.chdir(r"D:\hamer_data")

model, cfg = load_hamer(CKPT, init_renderer=False)
dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(dev).eval()
print(f"HAMER loaded OK on {dev}")
print(f"Parameters: {sum(p.numel() for p in model.parameters())/1e6:.0f}M")

x = torch.randn(1, 3, 256, 256).to(dev)
out = model({"img": x})
print(f"Vertices:     {list(out['pred_vertices'].shape)}")
print(f"Keypoints 3D: {list(out['pred_keypoints_3d'].shape)}")
print(f"Camera:       {list(out['pred_cam'].shape)}")
print("All good!")
