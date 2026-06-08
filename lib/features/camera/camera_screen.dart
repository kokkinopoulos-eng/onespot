import 'dart:math' as math;
import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../core/services/vision_api_service.dart';
import '../../core/services/settings_service.dart';

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
  Map<String, int> _counts = {};
  bool _isIdentifying = false;
  bool _showingToast = false;
  String _toastMsg = '';
  String? _lastError;
  Offset? _tapPosition;
  Rect? _selectionRect;
  Offset? _dotPosition;
  double _zoomLevel = 1.0;
  double _maxZoom = 1.0;
  double _minZoom = 1.0;
  List<Rect> _boundingBoxes = [];
  // Actual rendered preview size and offset within the camera Expanded area.
  // Set by _buildCameraPreview's LayoutBuilder; used by the crop and bounding-box
  // mapping so all three coordinate systems stay in sync.
  Size _previewRenderSize = Size.zero;
  Offset _previewOffset = Offset.zero;
  final SettingsService _settings = SettingsService();
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
    debugPrint('ONESPOT: pointer down ${e.pointer} pos=${e.localPosition}');
    _pointers[e.pointer] = e.localPosition;
    if (_pointers.length == 1) {
      _gestureStart = e.localPosition;
      _moved = false;
      _isPinch = false;
      if (_boundingBoxes.isNotEmpty) setState(() => _boundingBoxes = []);
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
    debugPrint('ONESPOT: pointer up ${e.pointer} moved=$_moved wasTap-pending');
    final upPos = _pointers[e.pointer] ?? e.localPosition;
    final wasOnlyPointer = _pointers.length == 1;
    _pointers.remove(e.pointer);
    final wasTap = wasOnlyPointer && !_moved && !_isPinch;
    if (wasTap) {
      final normRect = _selectionRect != null ? _normalizeRect(_selectionRect!) : null;
      if (normRect != null && normRect.contains(upPos)) {
        setState(() => _dotPosition = upPos);
        _onTap(upPos);
      } else if (normRect == null) {
        _showToast('Draw a selection rect, then tap inside it');
      } else {
        setState(() { _selectionRect = null; _dotPosition = null; _boundingBoxes = []; });
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

  // ── Count similar objects ──────────────────────────────────────────────────

  Future<void> _onTap(Offset position) async {
    if (_isIdentifying) return;
    // Single outer try/catch so NOTHING in the tap path can crash silently —
    // every failure surfaces in the error card and the busy flag is always
    // reset in the finally block.
    try {
      setState(() { _tapPosition = position; _lastError = null; });

      final provider = await _settings.getProvider();
      final key = await _settings.getApiKey(provider);
      if (key == null || key.isEmpty) {
        setState(() => _lastError = 'No API key for "$provider". Add one in Settings.');
        _showToast('Add API key in Settings');
        return;
      }
      // Guard against a stale/unknown provider (e.g. a previously-saved 'yolo')
      // that would otherwise throw a StateError from firstWhere.
      ApiProvider? apiProvider;
      for (final e in ApiProvider.values) {
        if (e.name == provider) { apiProvider = e; break; }
      }
      if (apiProvider == null) {
        setState(() => _lastError = 'Unknown provider "$provider". Pick one in Settings.');
        _showToast('Pick a provider in Settings');
        return;
      }

      setState(() { _isIdentifying = true; _isPaused = true; });
      final image = await _controller!.takePicture();
      final fullBytes = await image.readAsBytes();
      Uint8List bytes = fullBytes;

      // Crop selection rect to use as the template for similarity search.
      // _selectionRect is guaranteed non-null here (guarded in _onPointerUp).
      final normRect = _normalizeRect(_selectionRect!);
      try {
        final codec = await ui.instantiateImageCodec(fullBytes);
        final frame = await codec.getNextFrame();
        final img = frame.image;
        // screen → image coordinate mapping (inverse of bounding-box mapping below):
        //   imageX = (screenX - offsetX) / previewW * img.width
        final scaleX = img.width / _previewRenderSize.width;
        final scaleY = img.height / _previewRenderSize.height;
        final ox = _previewOffset.dx;
        final oy = _previewOffset.dy;
        final srcRect = Rect.fromLTRB(
          ((normRect.left - ox) * scaleX).clamp(0, img.width.toDouble()),
          ((normRect.top - oy) * scaleY).clamp(0, img.height.toDouble()),
          ((normRect.right - ox) * scaleX).clamp(0, img.width.toDouble()),
          ((normRect.bottom - oy) * scaleY).clamp(0, img.height.toDouble()),
        );
        final recorder = ui.PictureRecorder();
        final canvas = Canvas(recorder);
        canvas.drawImageRect(img, srcRect, Rect.fromLTWH(0, 0, srcRect.width, srcRect.height), Paint());
        final cropped = await recorder.endRecording().toImage(srcRect.width.toInt(), srcRect.height.toInt());
        final byteData = await cropped.toByteData(format: ui.ImageByteFormat.png);
        if (byteData != null) bytes = byteData.buffer.asUint8List();
      } catch (_) {}

      final apiService = VisionApiService(
        provider: apiProvider,
        apiKey: key,
      );
      final boxes = await apiService.findSimilar(bytes, fullBytes);

      // image fraction (0–1) → screen px:  screenX = fx * previewW + offsetX
      // Snapshot the preview geometry at tap time — it may change as panels appear/disappear
      final pw = _previewRenderSize.width;
      final ph = _previewRenderSize.height;
      final ox = _previewOffset.dx;
      final oy = _previewOffset.dy;
      if (pw == 0 || ph == 0) { setState(() => _lastError = 'Preview not ready — try again'); return; }
      final rects = boxes.map<Rect>((b) {
        final fx = (b['x'] as num).toDouble();
        final fy = (b['y'] as num).toDouble();
        final fw = (b['w'] as num).toDouble();
        final fh = (b['h'] as num).toDouble();
        return Rect.fromLTWH(fx * pw + ox, fy * ph + oy, fw * pw, fh * ph);
      }).toList();

      debugPrint('BOXES: ${rects.length}  previewSize=$_previewRenderSize  offset=$_previewOffset');
      if (boxes.isNotEmpty) debugPrint('BOX_RAW: ${boxes[0]}');
      if (rects.isNotEmpty) debugPrint('BOX0: fraction=(${boxes[0]['x']},${boxes[0]['y']},${boxes[0]['w']},${boxes[0]['h']}) screen=${rects[0]}');
      setState(() {
        _isIdentifying = false;
        _boundingBoxes = rects;
        _counts['Similar'] = rects.length;
        _toastMsg = 'Found ${rects.length} similar objects';
        _showingToast = true;
      });
      Future.delayed(const Duration(seconds: 5), () {
        if (mounted) setState(() => _showingToast = false);
      });
      await Future.delayed(const Duration(seconds: 8));
      if (mounted) setState(() { _tapPosition = null; _isPaused = false; });
    } catch (e, st) {
      debugPrint('ONESPOT _onTap crashed: $e\n$st');
      if (mounted) setState(() => _lastError = e.toString());
    } finally {
      if (mounted) setState(() => _isIdentifying = false);
    }
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
      // SafeArea(top) reserves the status-bar inset so the camera area can
      // never paint over the top bar. bottom:false keeps the bottom bar's own
      // padding in charge of the nav-bar gap.
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            // ── Camera area ──
            Expanded(
              // The Listener WRAPS the whole camera Stack instead of being a
              // childless Positioned.fill sibling. A parent Listener with opaque
              // behavior is guaranteed to be in the hit-test path for its entire
              // area and receives every pointer its children don't consume; a
              // childless sibling above a Texture-backed CameraPreview can be
              // bypassed and never see the events.
              child: Listener(
                behavior: HitTestBehavior.opaque,
                onPointerDown: _onPointerDown,
                onPointerMove: _onPointerMove,
                onPointerUp: _onPointerUp,
                onPointerCancel: _onPointerCancel,
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    _buildCameraPreview(),
                    if (_boundingBoxes.isNotEmpty) _buildBoundingBoxes(),
                    if (_selectionRect != null) _buildSelectionRect(),
                    if (_dotPosition != null) _buildDot(),
                    _buildZoomSlider(),
                    if (_tapPosition != null) _buildRipple(),
                    if (_counts.isNotEmpty) _buildCounterOverlay(),
                    if (_isIdentifying) _buildIdentifyingIndicator(),
                    if (_showingToast) _buildToast(),
                    if (_lastError != null) _buildErrorCard(),
                  ],
                ),
              ),
            ),

            // ── Bottom bar (outside camera) ──
            _buildBottomBar(),
          ],
        ),
      ),
    );
  }

  // ── Camera preview ────────────────────────────────────────────────────────

  Widget _buildCameraPreview() {
    // LayoutBuilder measures the actual camera area so we can compute the
    // cover-fit geometry for coordinate mapping.  With BoxFit.cover the
    // rendered image overflows the box (offset can be negative) and the
    // visible portion is a centre-crop of the full sensor frame.
    return LayoutBuilder(builder: (context, constraints) {
      final areaW = constraints.maxWidth;
      final areaH = constraints.maxHeight;
      final imgW = _controller!.value.previewSize!.height.toDouble();
      final imgH = _controller!.value.previewSize!.width.toDouble();
      final scale = math.max(areaW / imgW, areaH / imgH);
      final rendW = imgW * scale;
      final rendH = imgH * scale;
      final ox = (areaW - rendW) / 2; // negative when image wider than area
      final oy = (areaH - rendH) / 2;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted) return;
        if (_previewRenderSize.width != rendW || _previewRenderSize.height != rendH ||
            _previewOffset.dx != ox || _previewOffset.dy != oy) {
          setState(() {
            _previewRenderSize = Size(rendW, rendH);
            _previewOffset = Offset(ox, oy);
          });
          debugPrint('ONESPOT PREVIEW: size=$_previewRenderSize offset=$_previewOffset '
              'area=${areaW}x$areaH img=${imgW}x$imgH scale=$scale');
        }
      });
      return SizedBox.expand(
        child: FittedBox(
          fit: BoxFit.cover,
          child: SizedBox(
            width: imgW,
            height: imgH,
            child: CameraPreview(_controller!),
          ),
        ),
      );
    });
  }
  Widget _buildTopBar() {
    return Container(
      color: Colors.black,
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Flexible so the title yields width to the buttons instead of
          // pushing them off the right edge (which clipped ⚙️ and 📋).
          Flexible(
            child: RichText(
              overflow: TextOverflow.ellipsis,
              text: const TextSpan(
                style: TextStyle(fontFamily: 'BebasNeue', fontSize: 24, letterSpacing: 2),
                children: [
                  TextSpan(text: 'ONE', style: TextStyle(color: Colors.white)),
                  TextSpan(text: 'SPOT', style: TextStyle(color: Color(0xFF00FF88))),
                ],
              ),
            ),
          ),
          Row(mainAxisSize: MainAxisSize.min, children: [
            _iconBtn(_torchOn ? '🔦' : '🔆', _toggleTorch),
            const SizedBox(width: 6),
            _iconBtn('🔄', _flipCamera),
            const SizedBox(width: 6),
            _iconBtn('📋', () => Navigator.pushNamed(context, '/history')),
            const SizedBox(width: 6),
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
        width: 32, height: 32,
        decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.white24)),
        child: Center(child: Text(icon, style: const TextStyle(fontSize: 18))),
      ),
    );
  }

  // ── Counter panel ─────────────────────────────────────────────────────────


  // ── Bottom bar ────────────────────────────────────────────────────────────

  Widget _buildBottomBar() {
    return Container(
      color: Colors.black,
      padding: const EdgeInsets.fromLTRB(12, 12, 12, 24),
      child: Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [
        _barBtn('CLEAR', Icons.clear, () => setState(() {
          _counts.clear();
          _boundingBoxes.clear();
          _selectionRect = null;
          _dotPosition = null;
          _tapPosition = null;
        })),
        _barBtn('HISTORY', Icons.history, () => Navigator.pushNamed(context, '/history')),
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
            width: 52, height: 52,
            decoration: BoxDecoration(shape: BoxShape.circle,
              color: _isPaused ? const Color(0xFF00FF88) : Colors.transparent,
              border: Border.all(color: const Color(0xFF00FF88), width: 2)),
            child: Center(child: Text(_isPaused ? '▶' : '⏸',
              style: TextStyle(color: _isPaused ? Colors.black : const Color(0xFF00FF88), fontSize: 20))),
          ),
        ),
        _barBtn('SETTINGS', Icons.settings, () => Navigator.pushNamed(context, '/settings')),
        _barBtn('TORCH', _torchOn ? Icons.flashlight_on : Icons.flashlight_off, _toggleTorch),
        _barBtn('FLIP', Icons.flip_camera_android, _flipCamera),
        _barBtn('ABOUT', Icons.info_outline, () => Navigator.pushNamed(context, '/about')),
      ]),
    );
  }

  Widget _barBtn(String label, IconData icon, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Column(mainAxisSize: MainAxisSize.min, children: [
        Icon(icon, color: Colors.white54, size: 22),
        const SizedBox(height: 3),
        Text(label, style: const TextStyle(color: Colors.white38, fontSize: 9, letterSpacing: 0.5)),
      ]),
    );
  }

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
                child: Text('Tap inside to count',
                  style: TextStyle(color: Color(0xFF00FF88), fontSize: 10, letterSpacing: 1))))
          : null,
      ),
    );
  }

  Widget _buildCounterOverlay() {
    return Positioned(
      left: 12,
      bottom: 12,
      child: Container(
        constraints: const BoxConstraints(minWidth: 120, maxWidth: 180, maxHeight: 180),
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.75),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: const Color(0xFF00FF88).withOpacity(0.4)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('DETECTED', style: TextStyle(color: Color(0xFF00FF88), fontSize: 9, letterSpacing: 2)),
            const SizedBox(height: 6),
            ..._counts.entries.map((e) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 1),
              child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                Expanded(child: Text(e.key, style: const TextStyle(color: Colors.white, fontSize: 11), overflow: TextOverflow.ellipsis)),
                const SizedBox(width: 8),
                Text(e.value.toString(), style: const TextStyle(color: Color(0xFF00FF88), fontSize: 13, fontWeight: FontWeight.bold)),
              ]),
            )),
            const Divider(color: Color(0xFF00FF88), height: 10, thickness: 0.3),
            Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              const Text('TOTAL', style: TextStyle(color: Colors.white38, fontSize: 9)),
              Text(_counts.values.fold(0, (a, b) => a + b).toString(),
                style: const TextStyle(color: Color(0xFF00FF88), fontWeight: FontWeight.bold, fontSize: 12)),
            ]),
          ],
        ),
      ),
    );
  }

  Widget _buildBoundingBoxes() {
    return Stack(
      children: _boundingBoxes.asMap().entries.map((entry) {
        final r = entry.value;
        final idx = entry.key;
        // Cycle through distinct hues so overlapping boxes are distinguishable.
        final color = HSVColor.fromAHSV(1, (idx * 47.0) % 360, 1, 1).toColor();
        return Positioned(
          left: r.left,
          top: r.top,
          child: Container(
            width: r.width,
            height: r.height,
            decoration: BoxDecoration(
              border: Border.all(color: color, width: 2),
              color: color.withOpacity(0.08),
            ),
            child: r.height > 20
              ? Align(
                  alignment: Alignment.topLeft,
                  child: Container(
                    color: color.withOpacity(0.7),
                    padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                    child: Text('${idx + 1}',
                        style: const TextStyle(color: Colors.black, fontSize: 10, fontWeight: FontWeight.bold)),
                  ),
                )
              : null,
          ),
        );
      }).toList(),
    );
  }

  Widget _buildDot() {
    return Positioned(
      left: _dotPosition!.dx - 4,
      top: _dotPosition!.dy - 4,
      child: Container(
        width: 8, height: 8,
        decoration: const BoxDecoration(
          color: Color(0xFFFFD600),
          shape: BoxShape.circle,
          boxShadow: [BoxShadow(color: Color(0xFFFFD600), blurRadius: 3, spreadRadius: 1)],
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
