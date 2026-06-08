import 'package:flutter/material.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF040D1E),
      appBar: AppBar(
        backgroundColor: const Color(0xFF040D1E),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: RichText(text: const TextSpan(
          style: TextStyle(fontFamily: 'BebasNeue', fontSize: 22, letterSpacing: 2),
          children: [
            TextSpan(text: 'ONE', style: TextStyle(color: Colors.white)),
            TextSpan(text: 'SPOT', style: TextStyle(color: Color(0xFF00FF88))),
          ],
        )),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Logo
            Center(
              child: Column(children: [
                Image.asset('assets/icon/icon.png', width: 80, height: 80),
                const SizedBox(height: 12),
                RichText(text: const TextSpan(
                  style: TextStyle(fontFamily: 'BebasNeue', fontSize: 48, letterSpacing: 4),
                  children: [
                    TextSpan(text: 'ONE', style: TextStyle(color: Colors.white)),
                    TextSpan(text: 'SPOT', style: TextStyle(color: Color(0xFF00FF88))),
                  ],
                )),
                const Text('Spot one. Count all.',
                  style: TextStyle(color: Colors.white38, fontSize: 13, letterSpacing: 2)),
                const SizedBox(height: 4),
                const Text('Version 1.0.0',
                  style: TextStyle(color: Colors.white24, fontSize: 11)),
                const SizedBox(height: 4),
                const Text('by Kokkinopoulos Babis',
                  style: TextStyle(color: Colors.white38, fontSize: 12, letterSpacing: 1)),
              ]),
            ),
            const SizedBox(height: 40),

            // How to use
            _section('HOW TO USE'),
            _card([
              _step('1', 'Draw a rectangle', 'Drag your finger around the object you want to count.'),
              _divider(),
              _step('2', 'Tap inside', 'Tap anywhere inside the green rectangle to identify and count.'),
              _divider(),
              _step('3', 'See results', 'OneSpot finds all similar objects and draws bounding boxes around them.'),
              _divider(),
              _step('4', 'Freeze frame', 'Press ⏸ to freeze the camera before drawing for better accuracy.'),
            ]),
            const SizedBox(height: 24),

            // Tips
            _section('TIPS'),
            _card([
              _tip('🎯', 'Be specific', 'Draw a tight rectangle around just ONE object for best results.'),
              _divider(),
              _tip('💡', 'Good lighting', 'Use the torch button in low-light environments.'),
              _divider(),
              _tip('🔑', 'API Key', 'Add a free Gemini API key in Settings for best accuracy.'),
              _divider(),
              _tip('📋', 'History', 'All detections are saved in History with timestamps.'),
            ]),
            const SizedBox(height: 40),

            // Credits
            Center(
              child: Column(children: [
                const Text('Made with ❤️ in Greece',
                  style: TextStyle(color: Colors.white38, fontSize: 12)),
                const SizedBox(height: 4),
                const Text('© 2026 Kokkinopoulos Babis',
                  style: TextStyle(color: Colors.white24, fontSize: 11)),
              ]),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _section(String title) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: Text(title, style: const TextStyle(color: Color(0xFF00FF88), fontSize: 10, letterSpacing: 2, fontWeight: FontWeight.bold)),
  );

  Widget _card(List<Widget> children) => Container(
    margin: const EdgeInsets.only(bottom: 8),
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: const Color(0xFF0A1628),
      borderRadius: BorderRadius.circular(12),
      border: Border.all(color: const Color(0xFF1E2E4A)),
    ),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: children),
  );

  Widget _step(String num, String title, String desc) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 8),
    child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Container(width: 22, height: 22,
        decoration: const BoxDecoration(color: Color(0xFF00FF88), shape: BoxShape.circle),
        child: Center(child: Text(num, style: const TextStyle(color: Colors.black, fontSize: 11, fontWeight: FontWeight.bold)))),
      const SizedBox(width: 12),
      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
        const SizedBox(height: 2),
        Text(desc, style: const TextStyle(color: Colors.white54, fontSize: 12, height: 1.5)),
      ])),
    ]),
  );

  Widget _tip(String icon, String title, String desc) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 8),
    child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(icon, style: const TextStyle(fontSize: 18)),
      const SizedBox(width: 12),
      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
        const SizedBox(height: 2),
        Text(desc, style: const TextStyle(color: Colors.white54, fontSize: 12, height: 1.5)),
      ])),
    ]),
  );

  Widget _divider() => const Divider(color: Color(0xFF1E2E4A), height: 16);
}
