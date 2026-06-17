import os, time, cv2, numpy as np, torch
os.environ["PYOPENGL_PLATFORM"] = "wgl"
np.bool = bool
HAMER_DIR = r"C:\Users\Administrator\Documents\Codex\2026-06-16\files-mentioned-by-the-user-gpu2-3\hamer_code\hamer-main"
CKPT = os.path.join(HAMER_DIR, "_DATA", "hamer_ckpts","checkpoints","hamer.ckpt")
os.chdir(HAMER_DIR)
import sys; sys.path.insert(0, HAMER_DIR)
sys.path.insert(0, os.path.join(HAMER_DIR, "third-party", "ViTPose"))
from hamer.models import load_hamer
from hamer.datasets.vitdet_dataset import ViTDetDataset
from hamer.utils import recursive_to
from vitpose_model import ViTPoseModel
print("Loading models ..."); sys.stdout.flush()
m, c = load_hamer(CKPT, init_renderer=False)
d = torch.device("cuda" if torch.cuda.is_available() else "cpu")
m = m.to(d).eval()
cpm = ViTPoseModel("cuda")
imsz = c.MODEL.IMAGE_SIZE
# Measure camera alone
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened(): cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640); cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cam_read = []
for i in range(60):
    t0 = time.time(); r, f = cap.read()
    if r and i >= 5: cam_read.append(time.time()-t0)
cap.release()
cc = np.array(cam_read)*1000
print(f"\n=== Camera Only ===")
print(f"cap.read()  avg={cc.mean():.0f}ms  min={cc.min():.0f}ms  max={cc.max():.0f}ms  = {1000/cc.mean():.0f} FPS")
# Measure full pipeline (NO frame skip, 1 ViTPose + 1 HAMER per frame)
cap2 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap2.isOpened(): cap2 = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 640); cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
t_cam=[]; t_vit=[]; t_ham=[]; n_hands=0
for i in range(20):
    t0=time.time(); r,f=cap2.read()
    if not r: break
    h,w=f.shape[:2]; t_cam.append(time.time()-t0)
    det=[np.array([[0,0,w,h,0.9]])]
    vit=cpm.predict_pose(f,det); t_vit.append(time.time()-t0-sum(t_cam[-1:]))
    boxes=[];right=[]
    for vp in vit:
        kps=vp["keypoints"]
        for hk,ir in [(kps[-42:-21],False),(kps[-21:],True)]:
            v=hk[:,2]>0.5
            if sum(v)<4: continue
            x1b=int(hk[v,0].min()); y1b=int(hk[v,1].min())
            x2b=int(hk[v,0].max()); y2b=int(hk[v,1].max())
            boxes.append([x1b-20,y1b-20,x2b+20,y2b+20])
            right.append(1.0 if ir else 0.0)
    if boxes:
        ds=ViTDetDataset(c,f,np.stack(boxes).astype(np.float32),np.stack(right),rescale_factor=2.0)
        ld=torch.utils.data.DataLoader(ds,batch_size=4,shuffle=False,num_workers=0)
        for batch in ld:
            batch=recursive_to(batch,d)
            with torch.no_grad(): out=m(batch)
            n_hands+=batch["img"].shape[0]
    t_ham.append(time.time()-t0-sum(t_cam[-1:])-sum(t_vit[-1:]))
cap2.release()
cc2=np.array(t_cam)*1000; vv=np.array(t_vit)*1000; hh=np.array(t_ham)*1000
print(f"\n=== Full Pipeline (no frame skip) ===")
print(f"Capture     avg={cc2.mean():.0f}ms  min={cc2.min():.0f}ms  max={cc2.max():.0f}ms")
print(f"ViTPose     avg={vv.mean():.0f}ms  min={vv.min():.0f}ms  max={vv.max():.0f}ms")
print(f"HAMER       avg={hh.mean():.0f}ms  min={hh.min():.0f}ms  max={hh.max():.0f}ms" if hh.mean()>0 else f"HAMER       avg=0.0ms (no hands detected)")
total=(cc2+vv+hh).mean()
print(f"Per frame   avg={total:.0f}ms  = {1000/total:.1f} FPS (if total<1s)" if total<1000 else f"Per frame   avg={total:.0f}ms  = slow")
print(f"Hands detected in {n_hands} crops")
print(f"\n=== Summary ===")
print(f"AMERA is bottleneck: {cc.mean():.0f}ms/frame ({1000/cc.mean():.0f} FPS)")
print(f"ViTPose: {vv.mean():.0f}ms per run")
print(f"HAMER: {hh.mean():.0f}ms per hand" if hh.mean()>0 else "HAMER: no data")
print(f"With frame skip 5: ~{cc.mean()*1+vv.mean()/5+hh.mean()*1:.0f}ms = {1000/(cc.mean()/1000+vv.mean()/5000+hh.mean()/1000):.0f} FPS" if hh.mean()>0 else "")
print(f"With MediaPipe (~50ms): ~{cc.mean()+50+hh.mean()*1:.0f}ms = {1000/(cc.mean()+50+hh.mean())/1000:.0f} FPS" if hh.mean()>0 else "")
print("Done!")
