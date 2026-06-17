import sys, os
hdir = r"C:\Users\Administrator\Documents\Codex\2026-06-16\files-mentioned-by-the-user-gpu2-3\hamer_code\hamer-main"
vtp  = os.path.join(hdir, "third-party", "ViTPose")
sys.path.insert(0, hdir); sys.path.insert(0, vtp)
os.chdir(hdir)
from vitpose_model import ViTPoseModel
import cv2, numpy as np
img = cv2.imread(r"D:\hamer_data\test_cam.jpg")
det = [np.array([[0,0,img.shape[1],img.shape[0],0.9]])]
print("Loading ViTPose ...")
cpm = ViTPoseModel("cpu")
print("ViTPose loaded, running inference ...")
out = cpm.predict_pose(img, det)
print(f"People detected: {len(out)}")
if out:
    kps = out[0]["keypoints"]
    print(f"Keypoints shape: {kps.shape}")
    lh = kps[-42:-21]; rh = kps[-21:]
    print(f"Left hand valid: {sum(lh[:,2]>0.5)}")
    print(f"Right hand valid: {sum(rh[:,2]>0.5)}")
    print("ViTPose OK!")
else:
    print("No people detected")
