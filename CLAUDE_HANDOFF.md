# OneSpot — Claude Handoff Prompt

## Project
Flutter Android app called **OneSpot** at `C:\dev\onespot`.
Object identification via camera tap + counting. Test device: Samsung S25 Ultra.

## Stack
- Flutter 3.44.0, Dart 3.12.0
- camera package (CameraX)
- Android toolchain: **AGP 8.11.1, Gradle 8.14, Kotlin 2.2.20, Java 17**
- ultralytics_yolo 0.6.0 (TFLite, YOLO26)

## File structure
```
lib/
  main.dart
  core/
    services/
      vision_api_service.dart   — Claude/ChatGPT/Gemini API calls
      settings_service.dart     — shared_preferences wrapper
      yolo_service.dart         — local YOLO (offline)
    models/
      detection.dart
  features/
    camera/
      camera_screen.dart        — main screen
    settings/
      settings_screen.dart
assets/
  models/
    yolo26s_int8.tflite         — bundled model (9.6 MB, 80 COCO classes)
android/
  settings.gradle.kts           — AGP 8.11.1 / Kotlin 2.2.20
  gradle.properties             — builtInKotlin=false, newDsl=false
  gradle/wrapper/gradle-wrapper.properties — Gradle 8.14
  app/build.gradle.kts          — minSdk=max(24, flutter.minSdkVersion)
```

## What works (all confirmed on device)
- Camera preview fills full screen, no black box (Transform.scale cover fix)
- Tap → green ripple → "Identifying..." popup → result card (5s auto-dismiss)
- GestureDetector below UI controls, popup is topmost Stack child
- API error card (red, permanent, tap to dismiss) shows real error text
- Claude API: `claude-sonnet-4-6`, max_tokens=1024
- All 3 modes: Identify / Count One / Free Count
- Robust int parsing (_toInt) for API JSON responses
- YOLO tap-mode: offline, no API key, Settings → 🎯 YOLO

## All 4 providers
Settings screen has: **🎯 YOLO | 🤖 claude | 💬 chatgpt | ✨ gemini**
- YOLO → `YoloService.identify(bytes, mode.name)` → same result-map shape as API
- Others → `VisionApiService` with API key

## YoloService — result map shapes (identical to API shape)
```dart
// Identify / Count One:
{'name': 'cat', 'description': 'Local YOLO • 92% confidence', 'similar': 2}
// Free Count:
{'objects': [{'name': 'cat', 'count': 2}, {'name': 'chair', 'count': 3}]}
```
modelPath = 'yolo26s' (plugin auto-resolves to bundled yolo26s_int8.tflite)

## Remaining work (not done yet)
1. **Step 3**: Real-time YOLO mode — YOLOView widget with live bounding boxes as a separate mode option.
2. **Step 4**: Make Local YOLO the default provider (currently needs manual selection in Settings).
3. **Remove diagnostics**: strip `debugPrint('ONESPOT: ...')` lines from camera_screen.dart when stable.
4. **YOLO as default**: change SettingsService `getProvider()` fallback from `'claude'` to `'yolo'`.

## Rules from user
- One step at a time
- Give PowerShell scripts using Python for file writes (avoid heredoc encoding issues)
- Run `flutter analyze` before `flutter run`
- No inline Python with -c flag
- Questions/options in Greek

## Key files content

### lib/core/services/yolo_service.dart
```dart
import 'dart:typed_data';
import 'package:ultralytics_yolo/ultralytics_yolo.dart';

class YoloService {
  static const String modelPath = 'yolo26s';
  YOLO? _yolo;

  Future<void> _ensureLoaded() async {
    if (_yolo != null) return;
    final yolo = YOLO(modelPath: modelPath, task: YOLOTask.detect, useGpu: false);
    final ok = await yolo.loadModel();
    if (!ok) throw Exception('YOLO model failed to load ($modelPath).');
    _yolo = yolo;
  }

  Future<Map<String, dynamic>> identify(Uint8List imageBytes, String mode, {double confidence = 0.4}) async {
    await _ensureLoaded();
    final res = await _yolo!.predict(imageBytes, confidenceThreshold: confidence);
    final raw = (res['detections'] as List?) ?? const [];
    final dets = raw.map((d) => YOLOResult.fromMap(d as Map)).toList();

    if (dets.isEmpty) {
      if (mode == 'freeCount') return {'objects': <Map<String, dynamic>>[]};
      return {'name': 'Nothing detected', 'description': 'No known objects in view', 'similar': 0};
    }

    final counts = <String, int>{};
    for (final d in dets) { counts[d.className] = (counts[d.className] ?? 0) + 1; }

    if (mode == 'freeCount') {
      return {'objects': counts.entries.map((e) => {'name': e.key, 'count': e.value}).toList()};
    }
    if (mode == 'countOne') {
      final top = counts.entries.reduce((a, b) => b.value > a.value ? b : a);
      return {'name': top.key, 'description': 'Local YOLO • ${top.value} found', 'similar': top.value};
    }
    dets.sort((a, b) => b.confidence.compareTo(a.confidence));
    final top = dets.first;
    return {
      'name': top.className,
      'description': 'Local YOLO • ${(top.confidence * 100).round()}% confidence',
      'similar': counts[top.className] ?? 1,
    };
  }

  Future<void> dispose() async { await _yolo?.dispose(); _yolo = null; }
}
```

### lib/core/services/vision_api_service.dart (key parts)
- model: `claude-sonnet-4-6`, max_tokens: 1024
- Robust error handling: checks statusCode, no null-index crashes
- `_extractJson()` strips ```json fences and finds first `{...}` block
- `_apiErrorMessage()` extracts human-readable error from provider response

### android/settings.gradle.kts
```kotlin
id("com.android.application") version "8.11.1" apply false
id("org.jetbrains.kotlin.android") version "2.2.20" apply false
```

### android/gradle.properties
```
android.useAndroidX=true
android.newDsl=false
android.builtInKotlin=false
```

### android/gradle/wrapper/gradle-wrapper.properties
```
distributionUrl=https\://services.gradle.org/distributions/gradle-8.14-all.zip
```
