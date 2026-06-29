import os
f = r"C:\Users\Administrator\Documents\Codex\2026-06-16\files-mentioned-by-the-user-gpu2-3\run_hamer_camera.py"
with open(f, "r") as fp: c = fp.read()
c = c.replace("boxes_list = []; right_list = []", "boxes_list = []; right_list = []; t_hamer = 0.0")
c = c.replace("        for batch in loader:\n", "        t_hamer_start = time.time()\n        for batch in loader:\n")
c = c.replace("    t_hamer = 0.0", "    t_hamer = time.time() - t_hamer_start" )
c = c.replace("t_vit = time.time()\n    canvas", "t_vit = time.time()\n    t_hamer = 0.0\n    canvas")
c = c.replace(",.7,(0,200,0),2)", ",.5,(0,255,0),2)")
with open(f, "w") as fp: fp.write(c)
print("Timing added")
