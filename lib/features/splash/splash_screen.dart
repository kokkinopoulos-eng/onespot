import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});
  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnim;
  late Animation<double> _scaleAnim;

  @override
  void initState() {
    super.initState();
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
    _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 1200));
    _fadeAnim = CurvedAnimation(parent: _controller, curve: Curves.easeIn);
    _scaleAnim = Tween<double>(begin: 0.85, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutBack));
    _controller.forward();
    Future.delayed(const Duration(milliseconds: 2800), () {
      if (mounted) Navigator.pushReplacementNamed(context, '/camera');
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF040D1E),
      body: Container(
        decoration: const BoxDecoration(
          gradient: RadialGradient(
            center: Alignment.center,
            radius: 1.2,
            colors: [Color(0xFF0A1A3A), Color(0xFF040D1E)],
          ),
        ),
        child: Center(
          child: FadeTransition(
            opacity: _fadeAnim,
            child: ScaleTransition(
              scale: _scaleAnim,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Image.asset('assets/icon/icon.png', width: 100, height: 100),
                  const SizedBox(height: 28),
                  RichText(
                    text: const TextSpan(
                      style: TextStyle(fontFamily: 'BebasNeue', fontSize: 64, letterSpacing: 4, height: 1),
                      children: [
                        TextSpan(text: 'ONE', style: TextStyle(color: Colors.white)),
                        TextSpan(text: 'SPOT', style: TextStyle(color: Color(0xFFFFD600))),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text('Spot one. Count all.',
                    style: TextStyle(color: Colors.white54, fontSize: 16, letterSpacing: 2, fontFamily: 'BebasNeue')),
                  const SizedBox(height: 48),
                  const Text('by Kokkinopoulos Babis',
                    style: TextStyle(color: Colors.white24, fontSize: 12, letterSpacing: 1.5)),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
