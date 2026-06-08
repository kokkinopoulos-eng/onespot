import 'dart:typed_data';
import 'package:ultralytics_yolo/ultralytics_yolo.dart';

/// Local, offline object detection using a YOLO TFLite model.
///
/// Produces the SAME result-map shape as [VisionApiService] so the camera
/// screen's popup and counter logic work unchanged:
///   - freeCount     -> {'objects': [{'name':.., 'count':..}, ...]}
///   - identify/count -> {'name':.., 'description':.., 'similar': N}
class YoloService {
  /// Official Ultralytics model ID. The plugin resolves this to the bundled
  /// asset `assets/models/yolo26s_int8.tflite` when present (fully offline),
  /// and otherwise downloads it once and caches it on-device.
  static const String modelPath = 'yolo26s';

  YOLO? _yolo;

  Future<void> _ensureLoaded() async {
    if (_yolo != null) return;
    // useGpu:false for first-run stability; the GPU delegate crashes on some
    // devices. A single tap-image inference is fast enough on CPU.
    final yolo = YOLO(modelPath: modelPath, task: YOLOTask.detect, useGpu: false);
    final ok = await yolo.loadModel();
    if (!ok) {
      throw Exception('YOLO model failed to load ($modelPath).');
    }
    _yolo = yolo;
  }

  /// Runs detection on a still image and maps it to the app's result shape.
  /// [mode] is the SpotMode name: 'identify' | 'countOne' | 'freeCount'.
  Future<Map<String, dynamic>> identify(
    Uint8List imageBytes,
    String mode, {
    double confidence = 0.4,
  }) async {
    await _ensureLoaded();
    final res = await _yolo!.predict(imageBytes, confidenceThreshold: confidence);
    final raw = (res['detections'] as List?) ?? const [];
    final dets = raw.map((d) => YOLOResult.fromMap(d as Map)).toList();

    if (dets.isEmpty) {
      if (mode == 'freeCount') return {'objects': <Map<String, dynamic>>[]};
      return {
        'name': 'Nothing detected',
        'description': 'No known objects in view',
        'similar': 0,
      };
    }

    // Count instances per class.
    final counts = <String, int>{};
    for (final d in dets) {
      counts[d.className] = (counts[d.className] ?? 0) + 1;
    }

    if (mode == 'freeCount') {
      final objects = counts.entries
          .map((e) => {'name': e.key, 'count': e.value})
          .toList();
      return {'objects': objects};
    }

    if (mode == 'countOne') {
      // Most frequent class is the subject; report how many of it are visible.
      final top = counts.entries.reduce((a, b) => b.value > a.value ? b : a);
      return {
        'name': top.key,
        'description': 'Local YOLO • ${top.value} found',
        'similar': top.value,
      };
    }

    // identify: single most confident detection.
    dets.sort((a, b) => b.confidence.compareTo(a.confidence));
    final top = dets.first;
    final pct = (top.confidence * 100).round();
    return {
      'name': top.className,
      'description': 'Local YOLO • $pct% confidence',
      'similar': counts[top.className] ?? 1,
    };
  }

  Future<void> dispose() async {
    await _yolo?.dispose();
    _yolo = null;
  }
}
