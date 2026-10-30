# PipeBot AI Model Engineering Workspace

This directory is the dedicated machine learning workspace for PipeBot's real-time computer vision defect detection pipeline.

## 1. System Mission & Defect Detection Objective

PipeBot inspects municipal and residential PVC drainage pipelines (150 mm to 300 mm internal diameter). As the crawler traverses the conduit, optical camera frames from an onboard ESP32-CAM (OV2640 sensor) are ingested by the FastAPI backend and evaluated by a YOLOv8 neural network to localize and classify structural anomalies.

## 2. Approved Dataset Reference

- Dataset Title: `Pipe Defect Detection.v7 Dataset Pipe.yolov8`
- Source: Roboflow Universe
- Target Task: Bounding box object detection (`yolo detect`)
- Class Count: Exactly 4 canonical anomaly classes

## 3. Canonical Defect Classes

All model outputs, backend database records, and frontend dashboards adhere to these exact zero-indexed classes:

| Class ID | Canonical Name | Definition & Engineering Criteria |
| :---: | :--- | :--- |
| **0** | **Deformation** | Loss of conduit circular cross-section, vertical ovality flattening, or external soil load denting |
| **1** | **Misalignment** | Longitudinal or angular offset at PVC bell-and-spigot conduit joints |
| **2** | **Obstacle** | Physical conduit obstructions: tree root intrusion, heavy sediment build-up, or mechanical foreign objects |
| **3** | **Rupture** | Structural wall breach: longitudinal fractures, shear cracks, punctures, or blowouts |

## 4. Hardware Environment & Training Constraints

- Development Environment: WSL Ubuntu 22.04 on Windows 11
- Primary Compute Accelerator: NVIDIA GeForce RTX 2050 Laptop GPU
- Video RAM (VRAM): 4096 MB (4 GB GDDR6)
- Target Python Version: 3.10.x
- Deep Learning Framework: PyTorch 2.x with CUDA 12.x acceleration
- Vision Toolkit: `ultralytics>=8.3.0`

### VRAM Budgeting & Optimization Rules:
Due to the 4 GB VRAM limitation:
1. Model Choice: Prefer `yolov8n.pt` (Nano, ~3.2M params) or `yolov8s.pt` (Small, ~11.2M params). Avoid medium or large models during edge development.
2. Batch Size: Use `batch=8` (or `batch=16` with YOLOv8n). If CUDA Out-Of-Memory errors occur, step down to `batch=8`.
3. Input Resolution: Standard `imgsz=640`.
4. Mixed Precision: Always enable automatic mixed precision (`amp=True`, FP16) to conserve GPU memory and accelerate Tensor Core math.
5. Workers: Use `workers=4` to balance data loading throughput.

## 5. Workspace Directory Organization

```text
ai-model/
├── README.md               # Architecture, dataset, and training specifications (this file)
├── configs/
│   └── yolov8_pipebot.yaml # Ultralytics dataset configuration matching 4 canonical classes
├── dataset/                # Dataset splits (train/valid/test images and labels)
├── training/               # Training run scripts and hyperparameter tuning recipes
├── inference/              # Local inference verification and image benchmarking scripts
├── evaluation/             # Model evaluation metrics (mAP@0.5, confusion matrices, PR curves)
├── weights/                # Trained model weights (best.pt, best.onnx, quantized artifacts)
└── runs/                   # Ultralytics training logs and tensorboard events (git-ignored)
```

## 6. Training Execution Blueprint

When the dataset is placed into `ai-model/dataset/`, training is initiated using the following command inside the Python virtual environment:

```bash
# Activate virtual environment
source /mnt/d/PipeBot/backend/.venv/bin/activate

# Execute YOLOv8 training on GPU 0
yolo detect train \
  data=/mnt/d/PipeBot/ai-model/configs/yolov8_pipebot.yaml \
  model=yolov8n.pt \
  epochs=100 \
  imgsz=640 \
  batch=8 \
  device=0 \
  workers=4 \
  project=/mnt/d/PipeBot/ai-model/runs \
  name=pipebot_v8n_baseline
```

## 7. Model Export & Backend Deployment

Once training achieves target mAP (mean Average Precision > 85% at IoU 0.5):
1. Copy the resulting weights to `ai-model/weights/best.pt`.
2. Export to ONNX format for cross-platform inference:
   ```bash
   yolo export model=/mnt/d/PipeBot/ai-model/weights/best.pt format=onnx imgsz=640 optimize=True
   ```
3. Update `backend/.env` with the active model path:
   ```ini
   VISION_MODEL_PATH=/mnt/d/PipeBot/ai-model/weights/best.pt
   ```
4. The FastAPI backend loads this model dynamically through `app.vision.ultralytics_provider.UltralyticsInferenceProvider` and automatically dispatches defect detections to the database and WebSocket clients.
