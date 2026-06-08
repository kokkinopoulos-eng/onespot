code = """import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../core/services/vision_api_service.dart';
import '../../core/services/settings_service.dart';

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
  Map<String, dynamic>? _identifyResult;
  bool _isIdentifying = false;
  Offset? _tapPosition;
  final SettingsService _settings = SettingsService();

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
    if (mounted) setState(() => _isInitialized = true);
  }

  Future<void> _flipCamera() async {
    _cameraIndex = (_cameraIndex + 1) % _cameras.length;
    await _controller?.dispose();
    await _startCamera(_cameras[_cameraIndex]);
  }

  Future<void> _toggleTorch() async {
    if (_controller == null) return;
    _torchOn = !_torchOn;
    await _controller!.setFlashMode(_torchOn ? FlashMode.torch : FlashMode.off);
    setState(() {});
  }

  Future<void> _onTap(TapDownDetails details) async {
    if (_isIdentifying) return;
    setState(() { _tapPosition = details.localPosition; });
    final provider = await _settings.getProvider();
    final key = await _settings.getApiKey(provider);
    if (key == null || key.isEmpty) {
      _showToast('Add Gemini key (FREE) in Settings');
      return;
    }
    setState(() { _isIdentifying = true; _identifyResult = null; _isPaused = true; });
    try {
      final image = await _controller!.takePicture();
      final bytes = await image.readAsBytes();
      final apiService = VisionApiService(
        provider: ApiProvider.values.firstWhere((e) => e.name == provider),
        apiKey: key,
      );
      String prompt;
      if (_mode == SpotMode.identify) {
        prompt = 'What is the main object? Reply ONLY as JSON: {"name":"object name","description":"one sentence","similar":N} where N is count of similar objects visible.';
      } else if (_mode == SpotMode.countOne) {
        prompt = 'What is the most prominent object? Count all similar ones visible. Reply ONLY as JSON: {"name":"object name","description":"one sentence","similar":N} where N is total count of this object.';
      } else {
        prompt = 'List ALL distinct objects visible and count each. Reply ONLY as JSON: {"objects":[{"name":"object","count":N}]}';
      }
      final result = await apiService.identifyWithPrompt(bytes, prompt);
      setState(() {
        _identifyResult = result;
        _isIdentifying = false;
        if (_mode == SpotMode.freeCount && result['objects'] != null) {
          _counts.clear();
          for (final obj in result['objects']) {
            _counts[obj['name']] = obj['count'];
          }
        } else {
          final name = result['name'] as String? ?? 'Unknown';
          final count = _mode == SpotMode.countOne ? (result['similar'] as int? ?? 1) : 1;
          _counts[name] = (_counts[name] ?? 0) + count;
        }
      });
    } catch (e) {
      setState(() => _isIdentifying = false);
      _showToast('Error: ' + e.toString());
    }
    await Future.delayed(const Duration(seconds: 5));
    if (mounted) setState(() { _identifyResult = null; _tapPosition = null; _isPaused = false; });
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

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized) {
      return const Scaffold(
        backgroundColor: Color(0xFF080810),
        body: Center(child: CircularProgressIndicator(color: Color(0xFF00FF88))),
      );
    }
    return Scaffold(
      backgroundColor: Colors.black,
      extendBodyBehindAppBar: true,
      body: GestureDetector(
        onTapDown: _onTap,
        child: Stack(
          fit: StackFit.expand,
          children: [
            CameraPreview(_controller!),
            _buildTopBar(),
            _buildModeSelector(),
            _buildCounterPanel(),
            _buildBottomBar(),
            if (_tapPosition != null) _buildRipple(),
            if (_identifyResult != null || _isIdentifying) _buildIdentifyPopup(),
          ],
        ),
      ),
    );
  }

  Widget _buildTopBar() {
    return Positioned(
      top: 0, left: 0, right: 0,
      child: Container(
        padding: const EdgeInsets.fromLTRB(16, 48, 16, 16),
        decoration: const BoxDecoration(
          gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter,
            colors: [Colors.black87, Colors.transparent]),
        ),
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
              _iconBtn('⚙️', () => Navigator.pushNamed(context, '/settings')),
            ]),
          ],
        ),
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

  Widget _buildModeSelector() {
    return Positioned(
      top: 110, left: 0, right: 0,
      child: Center(
        child: Container(
          padding: const EdgeInsets.all(4),
          decoration: BoxDecoration(color: Colors.black.withOpacity(0.7),
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

  Widget _buildCounterPanel() {
    return Positioned(
      left: 16, bottom: 120,
      child: Container(
        constraints: const BoxConstraints(minWidth: 160, maxWidth: 200, maxHeight: 300),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.75), borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFF00FF88).withOpacity(0.3))),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min,
          children: [
            const Text('DETECTED', style: TextStyle(color: Color(0xFF00FF88), fontSize: 9, letterSpacing: 2)),
            const SizedBox(height: 8),
            if (_counts.isEmpty)
              const Text('Tap to identify', style: TextStyle(color: Colors.white38, fontSize: 11))
            else
              ..._counts.entries.map((e) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                  Expanded(child: Text(e.key, style: const TextStyle(color: Colors.white, fontSize: 12), overflow: TextOverflow.ellipsis)),
                  Text('\${e.value}', style: const TextStyle(color: Color(0xFF00FF88), fontSize: 14, fontWeight: FontWeight.bold)),
                ]),
              )),
            const Divider(color: Color(0xFF00FF88), height: 16, thickness: 0.3),
            Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              const Text('TOTAL', style: TextStyle(color: Colors.white38, fontSize: 10)),
              Text('\${_counts.values.fold(0, (a, b) => a + b)}',
                style: const TextStyle(color: Color(0xFF00FF88), fontWeight: FontWeight.bold)),
            ]),
          ],
        ),
      ),
    );
  }

  Widget _buildBottomBar() {
    return Positioned(
      bottom: 0, left: 0, right: 0,
      child: Container(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 36),
        decoration: const BoxDecoration(
          gradient: LinearGradient(begin: Alignment.bottomCenter, end: Alignment.topCenter,
            colors: [Colors.black87, Colors.transparent])),
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
            onTap: () => setState(() => _isPaused = !_isPaused),
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

  Widget _buildIdentifyPopup() {
    return Positioned(
      left: ((_tapPosition?.dx ?? 120) - 110).clamp(8, MediaQuery.of(context).size.width - 228),
      top: ((_tapPosition?.dy ?? 200) - 150).clamp(80, MediaQuery.of(context).size.height - 200),
      child: Container(
        width: 220, padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFF080810).withOpacity(0.95),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFF00FF88))),
        child: _isIdentifying
          ? const Row(children: [
              SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF00FF88))),
              SizedBox(width: 10),
              Text('Identifying...', style: TextStyle(color: Colors.white54, fontSize: 12)),
            ])
          : _identifyResult == null ? const SizedBox()
          : _identifyResult!['objects'] != null
            ? Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
                const Text('OBJECTS FOUND', style: TextStyle(color: Color(0xFF00FF88), fontSize: 10, letterSpacing: 1)),
                const SizedBox(height: 6),
                ...(_identifyResult!['objects'] as List).map((obj) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 2),
                  child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                    Text(obj['name'], style: const TextStyle(color: Colors.white, fontSize: 12)),
                    Text('\${obj['count']}', style: const TextStyle(color: Color(0xFF00FF88), fontWeight: FontWeight.bold)),
                  ]),
                )),
              ])
            : Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
                Text(_identifyResult!['name'] ?? '', style: const TextStyle(color: Color(0xFF00FF88), fontSize: 22, fontFamily: 'BebasNeue', letterSpacing: 1)),
                const SizedBox(height: 4),
                Text(_identifyResult!['description'] ?? '', style: const TextStyle(color: Colors.white54, fontSize: 11, height: 1.5)),
                if ((_identifyResult!['similar'] ?? 0) > 0) ...[
                  const SizedBox(height: 8),
                  Text('Similar visible: \${_identifyResult!['similar']}', style: const TextStyle(color: Colors.white70, fontSize: 11)),
                ],
              ]),
      ),
    );
  }
}
"""
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
