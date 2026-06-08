import os

code = """import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../core/services/vision_api_service.dart';
import '../../core/services/settings_service.dart';
import '../../core/services/yolo_service.dart';
import '../../core/models/history_entry.dart';

enum SpotMode { identify, countOne, freeCount }

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});
  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? _controller;
  List<CameraDescription> _cameras = [];
  int _cameraIndex = 0;
  bool _isInitialized = false;
  bool _isPaused = false;
  bool _torchOn = false;
  SpotMode _mode = SpotMode.identify;
  Map<String, int> _counts = {};
  bool _isIdentifying = false;
  bool _showingToast = false;
  String _toastMsg = '';
  String? _lastError;
  Offset? _tapPosition;
  Rect? _selectionRect;
  Offset? _dotPosition;
  Offset? _rectStart;
  double _zoomLevel = 1.0;
  double _maxZoom = 1.0;
  double _minZoom = 1.0;
  final SettingsService _settings = SettingsService();
  final YoloService _yolo = YoloService();
  final HistoryService _historyService = HistoryService();
  final Map<int, Offset> _pointers = {};
  Offset? _gestureStart;
  bool _moved = false;
  bool _isPinch = false;
  double _pinchBaseDist = 0;
  double _pinchBaseZoom = 1.0;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    final status = await Permission.camera.request();
    if (!status.isGranted) return;
    _cameras = await availableCameras();
    if (_cameras.isEmpty) return;
    await _startCamera(_cameras[_cameraIndex]);
  }

  Future<void> _startCamera(CameraDescription cam) async {
    _controller = CameraController(cam, ResolutionPreset.high, enableAudio: false);
    await _controller!.initialize();
    final maxZoom = await _controller!.getMaxZoomLevel();
    final minZoom = await _controller!.getMinZoomLevel();
    if (mounted) setState(() {
      _isInitialized = true;
      _maxZoom = maxZoom;
      _minZoom = minZoom;
    });
  }

  Future<void> _flipCamera() async {
    _cameraIndex = (_cameraIndex + 1) % _cameras.length;
    await _controller?.dispose();
    setState(() => _isInitialized = false);
    await _startCamera(_cameras[_cameraIndex]);
  }

  Future<void> _toggleTorch() async {
    if (_controller == null) return;
    _torchOn = !_torchOn;
    await _controller!.setFlashMode(_torchOn ? FlashMode.torch : FlashMode.off);
    setState(() {});
  }

  // ── Pointer handlers ──────────────────────────────────────────────────────

  void _onPointerDown(PointerDownEvent e) {
    _pointers[e.pointer] = e.localPosition;
    if (_pointers.length == 1) {
      _gestureStart = e.localPosition;
      _moved = false;
      _isPinch = false;
    } else if (_pointers.length == 2) {
      _isPinch = true;
      _moved = true;
      final pts = _pointers.values.toList();
      _pinchBaseDist = (pts[0] - pts[1]).distance;
      _pinchBaseZoom = _zoomLevel;
      setState(() => _selectionRect = null);
    }
  }

  void _onPointerMove(PointerMoveEvent e) {
    if (!_pointers.containsKey(e.pointer)) return;
    _pointers[e.pointer] = e.localPosition;
    if (_isPinch && _pointers.length >= 2) {
      final pts = _pointers.values.toList();
      final dist = (pts[0] - pts[1]).distance;
      if (_pinchBaseDist > 0) {
        final newZoom = (_pinchBaseZoom * (dist / _pinchBaseDist)).clamp(_minZoom, _maxZoom);
        _controller?.setZoomLevel(newZoom);
        setState(() => _zoomLevel = newZoom);
      }
    } else if (!_isPinch && _pointers.length == 1 && _gestureStart != null) {
      if ((e.localPosition - _gestureStart!).distance > 10) _moved = true;
      if (_moved) {
        setState(() {
          _selectionRect = Rect.fromPoints(_gestureStart!, e.localPosition);
          _dotPosition = null;
        });
      }
    }
  }

  void _onPointerUp(PointerUpEvent e) {
    final upPos = _pointers[e.pointer] ?? e.localPosition;
    final wasTap = _pointers.length == 1 && !_moved && !_isPinch;
    _pointers.remove(e.pointer);
    if (wasTap) {
      final normRect = _selectionRect != null ? _normalizeRect(_selectionRect!) : null;
      if (normRect != null && normRect.contains(upPos)) {
        setState(() => _dotPosition = upPos);
        _onTap(upPos);
      } else if (normRect == null) {
        _onTap(upPos);
      } else {
        setState(() { _selectionRect = null; _dotPosition = null; });
      }
    }
    _resetAfterPointerLift();
  }

  void _onPointerCancel(PointerCancelEvent e) {
    _pointers.remove(e.pointer);
    _resetAfterPointerLift();
  }

  void _resetAfterPointerLift() {
    if (_pointers.isEmpty) {
      _gestureStart = null;
      _isPinch = false;
      _moved = false;
    }
  }

  Rect _normalizeRect(Rect r) => Rect.fromLTRB(
    r.left < r.right ? r.left : r.right,
    r.top < r.bottom ? r.top : r.bottom,
    r.left > r.right ? r.left : r.right,
    r.top > r.bottom ? r.top : r.bottom,
  );

  // ── Identify ──────────────────────────────────────────────────────────────

  Future<void> _onTap(Offset position) async {
    if (_isIdentifying) return;
    setState(() { _tapPosition = position; _lastError = null; });

    final provider = await _settings.getProvider();
    final isYolo = provider == 'yolo';
    final language = await _settings.getLanguage();
    String? key;
    if (!isYolo) {
      key = await _settings.getApiKey(provider);
      if (key == null || key.isEmpty) {
        setState(() => _lastError = 'No API key for "$provider". Add one in Settings.');
        _showToast('Add API key in Settings');
        return;
      }
    }

    setState(() { _isIdentifying = true; _isPaused = true; });
    try {
      final image = await _controller!.takePicture();
      final fullBytes = await image.readAsBytes();
      Uint8List bytes = fullBytes;

      // Crop to selection rect if available
      final normRect = _selectionRect != null ? _normalizeRect(_selectionRect!) : null;
      if (normRect != null) {
        try {
          final codec = await ui.instantiateImageCodec(fullBytes);
          final frame = await codec.getNextFrame();
          final img = frame.image;
          final previewSize = _controller!.value.previewSize!;
          final screenW = MediaQuery.of(context).size.width;
          final screenH = MediaQuery.of(context).size.height * 0.75;
          final scaleX = img.width / screenW;
          final scaleY = img.height / screenH;
          final srcRect = Rect.fromLTRB(
            (normRect.left * scaleX).clamp(0, img.width.toDouble()),
            (normRect.top * scaleY).clamp(0, img.height.toDouble()),
            (normRect.right * scaleX).clamp(0, img.width.toDouble()),
            (normRect.bottom * scaleY).clamp(0, img.height.toDouble()),
          );
          final recorder = ui.PictureRecorder();
          final canvas = Canvas(recorder);
          final dst = Rect.fromLTWH(0, 0, srcRect.width, srcRect.height);
          canvas.drawImageRect(img, srcRect, dst, Paint());
          final cropped = await recorder.endRecording().toImage(srcRect.width.toInt(), srcRect.height.toInt());
          final byteData = await cropped.toByteData(format: ui.ImageByteFormat.png);
          if (byteData != null) bytes = byteData.buffer.asUint8List();
        } catch (_) {}
      }

      final Map<String, dynamic> result;
      if (isYolo) {
        result = await _yolo.identify(bytes, _mode.name);
      } else {
        final apiService = VisionApiService(
          provider: ApiProvider.values.firstWhere((e) => e.name == provider),
          apiKey: key!,
        );
        final langSuffix = ' Reply in \$language.';
        String prompt;
        if (_mode == SpotMode.identify) {
          prompt = 'What is the main object? Reply ONLY as JSON: {"name":"object name","description":"one sentence","similar":N} where N is count of similar objects visible.' + langSuffix;
        } else if (_mode == SpotMode.countOne) {
          prompt = 'What is the most prominent object? Count all similar ones. Reply ONLY as JSON: {"name":"object name","description":"one sentence","similar":N}' + langSuffix;
        } else {
          prompt = 'List ALL distinct objects and count each. Reply ONLY as JSON: {"objects":[{"name":"object","count":N}]}' + langSuffix;
        }
        result = await apiService.identifyWithPrompt(bytes, prompt);
      }

      setState(() { _isIdentifying = false; });
      await _historyService.add(_mode.name, result);
      _showResultToast(result);
      setState(() {
        if (_mode == SpotMode.freeCount && result['objects'] != null) {
          _counts.clear();
          for (final obj in (result['objects'] as List)) {
            final name = obj['name']?.toString() ?? 'Unknown';
            _counts[name] = _toInt(obj['count'], fallback: 1);
          }
        } else {
          final name = result['name']?.toString() ?? 'Unknown';
          final count = _mode == SpotMode.countOne ? _toInt(result['similar'], fallback: 1) : 1;
          _counts[name] = (_counts[name] ?? 0) + count;
        }
      });
    } catch (e) {
      setState(() { _isIdentifying = false; _lastError = e.toString(); });
      return;
    }
    await Future.delayed(const Duration(seconds: 5));
    if (mounted) setState(() { _tapPosition = null; _isPaused = false; });
  }

  int _toInt(dynamic v, {int fallback = 0}) {
    if (v is int) return v;
    if (v is double) return v.round();
    if (v is String) return int.tryParse(v.trim()) ?? fallback;
    return fallback;
  }

  void _showResultToast(Map<String, dynamic> result) {
    String msg;
    if (result['objects'] != null) {
      final count = (result['objects'] as List).length;
      final total = (result['objects'] as List).fold<int>(0, (sum, obj) => sum + (obj['count'] as int? ?? 1));
      msg = 'Found \$count types, \$total total → History';
    } else {
      final name = result['name'] ?? 'Unknown';
      final similar = result['similar'] ?? 0;
      msg = similar > 1 ? 'Found \$name x\$similar → History' : 'Found \$name → History';
    }
    setState(() { _toastMsg = msg; _showingToast = true; });
    Future.delayed(const Duration(seconds: 5), () {
      if (mounted) setState(() { _showingToast = false; });
    });
  }

  void _showToast(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: const Color(0xFF0F0F1A),
        behavior: SnackBarBehavior.floating, duration: const Duration(seconds: 3)),
    );
  }

  @override
  void dispose() {
    _controller?.dispose();
    _yolo.dispose();
    super.dispose();
  }

  // ── BUILD ─────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized || _controller == null) {
      return const Scaffold(
        backgroundColor: Color(0xFF080810),
        body: Center(child: CircularProgressIndicator(color: Color(0xFF00FF88))),
      );
    }
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Column(
          children: [
            // ── Top bar (outside camera) ──
            _buildTopBar(),
            // ── Mode selector (outside camera) ──
            _buildModeSelector(),
            // ── Camera area ──
            Expanded(
              child: Stack(
                fit: StackFit.expand,
                children: [
                  _buildCameraPreview(),
                  // Listener covers entire camera area — no UI controls overlap it
                  Positioned.fill(
                    child: Listener(
                      behavior: HitTestBehavior.opaque,
                      onPointerDown: _onPointerDown,
                      onPointerMove: _onPointerMove,
                      onPointerUp: _onPointerUp,
                      onPointerCancel: _onPointerCancel,
                    ),
                  ),
                  if (_selectionRect != null) _buildSelectionRect(),
                  if (_dotPosition != null) _buildDot(),
                  _buildZoomSlider(),
                  if (_tapPosition != null) _buildRipple(),
                  if (_isIdentifying) _buildIdentifyingIndicator(),
                  if (_showingToast) _buildToast(),
                  if (_lastError != null) _buildErrorCard(),
                ],
              ),
            ),
            // ── Counter panel (outside camera) ──
            _buildCounterPanel(),
            // ── Bottom bar (outside camera) ──
            _buildBottomBar(),
          ],
        ),
      ),
    );
  }

  // ── Camera preview ────────────────────────────────────────────────────────

  Widget _buildCameraPreview() {
    return LayoutBuilder(
      builder: (context, constraints) {
        final size = constraints.biggest;
        final scale = 1 / (_controller!.value.aspectRatio * size.aspectRatio);
        return ClipRect(
          clipper: _MediaSizeClipper(size),
          child: Transform.scale(
            scale: scale,
            alignment: Alignment.topCenter,
            child: CameraPreview(_controller!),
          ),
        );
      },
    );
  }

  // ── Top bar ───────────────────────────────────────────────────────────────

  Widget _buildTopBar() {
    return Container(
      color: Colors.black,
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          RichText(text: const TextSpan(
            style: TextStyle(fontFamily: 'BebasNeue', fontSize: 24, letterSpacing: 2),
            children: [
              TextSpan(text: 'ONE', style: TextStyle(color: Colors.white)),
              TextSpan(text: 'SPOT', style: TextStyle(color: Color(0xFF00FF88))),
            ],
          )),
          Row(children: [
            _iconBtn(_torchOn ? '🔦' : '🔆', _toggleTorch),
            const SizedBox(width: 8),
            _iconBtn('🔄', _flipCamera),
            const SizedBox(width: 8),
            _iconBtn('📋', () => Navigator.pushNamed(context, '/history')),
            const SizedBox(width: 8),
            _iconBtn('⚙️', () => Navigator.pushNamed(context, '/settings')),
          ]),
        ],
      ),
    );
  }

  Widget _iconBtn(String icon, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 38, height: 38,
        decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(10),
          border: Border.all(color: Colors.white24)),
        child: Center(child: Text(icon, style: const TextStyle(fontSize: 18))),
      ),
    );
  }

  // ── Mode selector ─────────────────────────────────────────────────────────

  Widget _buildModeSelector() {
    return Container(
      color: Colors.black,
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Center(
        child: Container(
          padding: const EdgeInsets.all(4),
          decoration: BoxDecoration(color: Colors.black87,
            borderRadius: BorderRadius.circular(30), border: Border.all(color: Colors.white12)),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            _modeBtn('Identify', SpotMode.identify),
            _modeBtn('Count One', SpotMode.countOne),
            _modeBtn('Free Count', SpotMode.freeCount),
          ]),
        ),
      ),
    );
  }

  Widget _modeBtn(String label, SpotMode mode) {
    final active = _mode == mode;
    return GestureDetector(
      onTap: () => setState(() { _mode = mode; _counts.clear(); }),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: active ? const Color(0xFF00FF88) : Colors.transparent,
          borderRadius: BorderRadius.circular(24),
        ),
        child: Text(label, style: TextStyle(
          color: active ? Colors.black : Colors.white54,
          fontSize: 12, fontWeight: active ? FontWeight.bold : FontWeight.normal)),
      ),
    );
  }

  // ── Counter panel ─────────────────────────────────────────────────────────

  Widget _buildCounterPanel() {
    return Container(
      color: Colors.black,
      width: double.infinity,
      constraints: const BoxConstraints(maxHeight: 160),
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text('DETECTED', style: TextStyle(color: Color(0xFF00FF88), fontSize: 9, letterSpacing: 2)),
          const SizedBox(height: 4),
          if (_counts.isEmpty)
            const Text('Tap to identify', style: TextStyle(color: Colors.white38, fontSize: 11))
          else
            Flexible(child: SingleChildScrollView(child: Column(
              mainAxisSize: MainAxisSize.min,
              children: _counts.entries.map((e) => Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(child: Text(e.key, style: const TextStyle(color: Colors.white, fontSize: 12), overflow: TextOverflow.ellipsis)),
                  Text(e.value.toString(), style: const TextStyle(color: Color(0xFF00FF88), fontSize: 13, fontWeight: FontWeight.bold)),
                ],
              )).toList(),
            ))),
          const Divider(color: Color(0xFF00FF88), height: 10, thickness: 0.3),
          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
            const Text('TOTAL', style: TextStyle(color: Colors.white38, fontSize: 10)),
            Text('\${_counts.values.fold(0, (a, b) => a + b)}',
              style: const TextStyle(color: Color(0xFF00FF88), fontWeight: FontWeight.bold)),
          ]),
        ],
      ),
    );
  }

  // ── Bottom bar ────────────────────────────────────────────────────────────

  Widget _buildBottomBar() {
    return Container(
      color: Colors.black,
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
      child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
        GestureDetector(
          onTap: () => setState(() => _counts.clear()),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(border: Border.all(color: Colors.white24), borderRadius: BorderRadius.circular(6)),
            child: const Text('CLEAR', style: TextStyle(color: Colors.white38, fontSize: 11)),
          ),
        ),
        GestureDetector(
          onTap: () async {
            if (_isPaused) {
              await _controller?.resumePreview();
            } else {
              await _controller?.pausePreview();
            }
            setState(() => _isPaused = !_isPaused);
          },
          child: Container(
            width: 56, height: 56,
            decoration: BoxDecoration(shape: BoxShape.circle,
              color: _isPaused ? const Color(0xFF00FF88) : Colors.transparent,
              border: Border.all(color: const Color(0xFF00FF88), width: 2)),
            child: Center(child: Text(_isPaused ? '▶' : '⏸',
              style: TextStyle(color: _isPaused ? Colors.black : const Color(0xFF00FF88), fontSize: 20))),
          ),
        ),
        GestureDetector(
          onTap: () {
            if (_counts.isEmpty) { _showToast('Nothing to share'); return; }
            _showToast(_counts.entries.map((e) => '\${e.key}: \${e.value}').join(', '));
          },
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(border: Border.all(color: Colors.white24), borderRadius: BorderRadius.circular(6)),
            child: const Text('SHARE', style: TextStyle(color: Colors.white38, fontSize: 11)),
          ),
        ),
      ]),
    );
  }

  // ── Overlays ──────────────────────────────────────────────────────────────

  Widget _buildSelectionRect() {
    final normalized = _normalizeRect(_selectionRect!);
    return Positioned(
      left: normalized.left,
      top: normalized.top,
      child: Container(
        width: normalized.width,
        height: normalized.height,
        decoration: BoxDecoration(
          border: Border.all(color: const Color(0xFF00FF88), width: 2),
          color: const Color(0xFF00FF88).withOpacity(0.08),
        ),
        child: normalized.width > 80 && normalized.height > 40
          ? const Align(alignment: Alignment.topCenter,
              child: Padding(padding: EdgeInsets.only(top: 4),
                child: Text('Tap inside to identify',
                  style: TextStyle(color: Color(0xFF00FF88), fontSize: 10, letterSpacing: 1))))
          : null,
      ),
    );
  }

  Widget _buildDot() {
    return Positioned(
      left: _dotPosition!.dx - 8,
      top: _dotPosition!.dy - 8,
      child: Container(
        width: 16, height: 16,
        decoration: const BoxDecoration(
          color: Color(0xFFFFD600),
          shape: BoxShape.circle,
          boxShadow: [BoxShadow(color: Color(0xFFFFD600), blurRadius: 6, spreadRadius: 2)],
        ),
      ),
    );
  }

  Widget _buildZoomSlider() {
    if (_maxZoom <= 1.0) return const SizedBox.shrink();
    return Positioned(
      right: 8, top: 20, bottom: 20,
      child: RotatedBox(
        quarterTurns: 3,
        child: Slider(
          value: _zoomLevel,
          min: _minZoom,
          max: _maxZoom,
          activeColor: const Color(0xFF00FF88),
          inactiveColor: Colors.white24,
          onChanged: (v) {
            setState(() => _zoomLevel = v);
            _controller?.setZoomLevel(v);
          },
        ),
      ),
    );
  }

  Widget _buildRipple() {
    return Positioned(
      left: _tapPosition!.dx - 30, top: _tapPosition!.dy - 30,
      child: TweenAnimationBuilder<double>(
        tween: Tween(begin: 0, end: 1),
        duration: const Duration(milliseconds: 600),
        builder: (_, v, __) => Opacity(
          opacity: 1 - v,
          child: Container(
            width: 60 + 60 * v, height: 60 + 60 * v,
            decoration: BoxDecoration(shape: BoxShape.circle,
              border: Border.all(color: const Color(0xFF00FF88), width: 2)),
          ),
        ),
      ),
    );
  }

  Widget _buildIdentifyingIndicator() {
    return Positioned(
      top: 20, left: 24, right: 24,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.75),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: const Color(0xFF00FF88).withOpacity(0.5)),
        ),
        child: const Row(mainAxisSize: MainAxisSize.min, mainAxisAlignment: MainAxisAlignment.center,
          children: [
            SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF00FF88))),
            SizedBox(width: 10),
            Text('Identifying...', style: TextStyle(color: Colors.white70, fontSize: 13)),
          ]),
      ),
    );
  }

  Widget _buildToast() {
    return Positioned(
      top: 20, left: 24, right: 24,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.75),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: const Color(0xFF00FF88).withOpacity(0.5)),
        ),
        child: Row(mainAxisSize: MainAxisSize.min, mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('✅ ', style: TextStyle(fontSize: 14)),
            Flexible(child: Text(_toastMsg, style: const TextStyle(color: Colors.white, fontSize: 13), textAlign: TextAlign.center)),
          ]),
      ),
    );
  }

  Widget _buildErrorCard() {
    return Positioned(
      top: 20, left: 16, right: 16,
      child: GestureDetector(
        onTap: () => setState(() => _lastError = null),
        child: Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF1A0000),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.redAccent),
          ),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('ERROR (tap to dismiss)',
              style: TextStyle(color: Colors.redAccent, fontSize: 11, letterSpacing: 1, fontWeight: FontWeight.bold)),
            const SizedBox(height: 6),
            Text(_lastError ?? '', style: const TextStyle(color: Colors.white, fontSize: 12, height: 1.4)),
          ]),
        ),
      ),
    );
  }
}

class _MediaSizeClipper extends CustomClipper<Rect> {
  final Size mediaSize;
  const _MediaSizeClipper(this.mediaSize);
  @override
  Rect getClip(Size size) => Rect.fromLTWH(0, 0, mediaSize.width, mediaSize.height);
  @override
  bool shouldReclip(_MediaSizeClipper oldClipper) => mediaSize != oldClipper.mediaSize;
}
"""

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
