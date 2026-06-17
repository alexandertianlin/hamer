 # GPU2-3 本地部署 HAMER 工作日志
 ## 2026-06-17

 ---

 ## 环境配置
 | 项目 | 说明 |
 |------|------|
 | 系统 | Windows 10 22H2 |
 | GPU | NVIDIA GeForce RTX 4080 Laptop GPU (12GB VRAM) |
 | CUDA Driver | 12.8 |
 | Python | 3.10.20 (conda env: `hamer`) |
 | PyTorch | 2.6.0+cu124 |

 ---

 ## 依赖包
 - smplx 0.1.28, timm 1.0.27, pytorch_lightning 2.6.5
 - opencv-python 4.13.0, scipy 1.15.3, numpy 2.2.6
 - chumpy (patched for numpy 2.x compat)
 - mmpose (patched to skip mmcv dependency)
 - mmdet 3.3.0, mmcv 2.1.0
 - mediapipe 0.10.35, webdataset

 ---

 ## 模型文件
 | 文件 | 路径 | 大小 |
 |------|------|------|
 | HAMER checkpoint | `D:\hamer_data\_DATA\hamer_ckpts\checkpoints\hamer.ckpt` | 2.5 GB |
 | HAMER config | `D:\hamer_data\_DATA\hamer_ckpts\model_config.yaml` | 2 KB |
 | MANO model | `D:\hamer_data\_DATA\data\mano\MANO_RIGHT.pkl` | 3.8 MB |
 | MANO mean params | `D:\hamer_data\_DATA\data\mano_mean_params.npz` | 1.2 KB |
 | ViTPose checkpoint | `D:\hamer_data\_DATA\vitpose_ckpts\vitpose+_huge\wholebody.pth` | 3.8 GB |
 | ViTPose config | `hamer_code/.../coco-wholebody/ViTPose_huge_wholebody_256x192.py` | 4 KB |
 | ViTPose base configs | `third-party/ViTPose/configs/_base_/*` | 2 files |

 ## 代码目录
 ```
 C:\Users\Administrator\Documents\Codex\2026-06-16\files-mentioned-by-the-user-gpu2-3\
 ├── hamer_code/hamer-main/          ← HAMER 源码 (pip install -e .)
 │   └── third-party/ViTPose/        ← ViTPose 配置 & mmpose
 ├── _DATA/ → D:\hamer_data\_DATA\   ← 符号链接
 ├── run_hamer_camera.py             ← 摄像头推理脚本
 ├── download_hamer_data.py          ← 权重下载脚本
 └── WORK_LOG.md                     ← 本日志
 ```

 ---

 ## 推理管线
 1. **摄像头采集** (640×480, CAP_DSHOW)
 2. **ViTPose 全身姿态估计** (GPU) → 133 个关键点
 3. **手部筛选** → 从 133 个关键点中提取左右手 (各 21 点)
 4. **同手去重** → 左右手中心 < 50px 时保留置信度高的
 5. **ViTDetDataset** → 裁剪归一化为 256×256 输入
 6. **HAMER 3D 重建** (GPU) → 预测 3D 手部网格 + 2D 投影
 7. **坐标映射** → crop [0,1] → 原图像素坐标
 8. **OpenCV 渲染** → 绘制骨架线和关键点

 ---

 ## 延迟分析
 当前问题: **手部与画面延迟约 1 秒**

 ### 延迟来源
 | 环节 | 预计耗时 | 占比 |
 |------|---------|------|
 | ViTPose 推理 | 高 (3.8G 模型) | 主要瓶颈 |
 | HAMER 推理 | 中 (672M 模型) | 次要 |
 | 图像预处理 + 后处理 | 低 | 可忽略 |

 ### 优化方案
 1. **降低 ViTPose 推理频率**: 每 N 帧运行一次 ViTPose，中间帧用跟踪
 2. **使用更轻量的手部检测器**: 替换 ViTPose 为 MediaPipe / YOLOv8n-pose
 3. **ONNX Runtime / TensorRT 加速**: 模型导出为 ONNX 用 FP16 推理
 4. **流水线并行**: ViTPose 与 HAMER 分离到不同流

 ---

 ## 待办
 - [ ] 实施延迟优化（帧跳过 / 轻量检测器）
 - [ ] 3D 手部网格实时渲染
 - [ ] 手套追踪精度评估
 - [ ] 集成到完整标注管线
