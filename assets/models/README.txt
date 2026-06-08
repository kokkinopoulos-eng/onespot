Bundled YOLO model for offline detection.

  yolo26s_int8.tflite  — Ultralytics YOLO26-small, INT8, COCO 80 classes.
  Source: https://github.com/ultralytics/yolo-flutter-app/releases/download/v0.3.5/yolo26s_int8.tflite

YoloService uses modelPath 'yolo26s'; the ultralytics_yolo plugin maps that to
this bundled asset (no network needed). To use a different size, download the
matching {id}_int8.tflite from the same release (yolo26n/s/m/l/x) and update
YoloService.modelPath.
