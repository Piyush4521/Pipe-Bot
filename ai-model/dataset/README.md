# PipeBot Defect Detection Dataset Directory

This directory hosts the approved training, validation, and testing dataset splits for PipeBot.

## Approved Dataset Reference

- Dataset Name: `Pipe Defect Detection.v7 Dataset Pipe.yolov8`
- Source Platform: Roboflow Universe
- Annotation Format: YOLOv8 PyTorch format (`images/` and `labels/` with normalized bounding boxes)

## Canonical Defect Classes

The pipeline inspection system targets four distinct structural anomalies:

| Class ID | Canonical Class Name | Description |
| :--- | :--- | :--- |
| `0` | `Deformation` | Cross-sectional crushing, ovality loss, or conduit wall flattening |
| `1` | `Misalignment` | Angular or axial joint offset between adjoining conduit sections |
| `2` | `Obstacle` | Root intrusion, debris accumulation, silt build-up, or mechanical blockage |
| `3` | `Rupture` | Longitudinal wall fractures, shear tears, punctures, or blowouts |

## Expected Directory Layout

```text
ai-model/dataset/
  train/
    images/
    labels/
  valid/
    images/
    labels/
  test/
    images/
    labels/
```
