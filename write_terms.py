import os
os.makedirs("lib/features/onboarding", exist_ok=True)

code = """import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});
  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  bool _accepted = false;
  final ScrollController _scrollController = ScrollController();

  Future<void> _accept() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('terms_accepted', true);
    if (mounted) Navigator.pushReplacementNamed(context, '/camera');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF040D1E),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                controller: _scrollController,
                padding: const EdgeInsets.fromLTRB(20, 32, 20, 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Logo
                    Center(
                      child: RichText(
                        text: const TextSpan(
                          style: TextStyle(fontFamily: 'BebasNeue', fontSize: 48, letterSpacing: 4),
                          children: [
                            TextSpan(text: 'ONE', style: TextStyle(color: Colors.white)),
                            TextSpan(text: 'SPOT', style: TextStyle(color: Color(0xFFFFD600))),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Center(
                      child: Text('Spot one. Count all.',
                        style: TextStyle(color: Colors.white38, fontSize: 13, letterSpacing: 2)),
                    ),
                    const SizedBox(height: 40),

                    // How to use
                    _sectionTitle('HOW TO USE'),
                    _card(children: [
                      _step('1', 'Identify', 'Point your camera at any object and tap on it. OneSpot will identify what it is, describe it, and tell you how many similar objects are visible in the scene.'),
                      _divider(),
                      _step('2', 'Count One', 'Tap on a specific object to lock on it. OneSpot will count how many of that exact object appear in the frame — useful for inventory, stock checks, or simply satisfying your curiosity.'),
                      _divider(),
                      _step('3', 'Free Count', 'Let OneSpot scan the entire scene and automatically list every distinct object it finds, along with the count of each.'),
                    ]),
                    const SizedBox(height: 12),
                    _card(children: [
                      _info('🎯', 'Local YOLO', 'Works completely offline. No internet required. Fast and private.'),
                      _divider(),
                      _info('🤖', 'Claude / ChatGPT / Gemini', 'Cloud AI for deeper identification. Requires an API key. Gemini offers a free tier.'),
                      _divider(),
                      _info('🌍', 'Response Language', 'Go to Settings to choose the language in which AI replies.'),
                      _divider(),
                      _info('📋', 'History', 'Every identification is saved with a timestamp. Tap the clipboard icon to review past results.'),
                      _divider(),
                      _info('✂️', 'Smart Crop', 'OneSpot focuses on exactly where you tap — not the whole scene — for more accurate results.'),
                      _divider(),
                      _info('📤', 'Share', 'Share your detection results with anyone directly from the camera screen.'),
                      _divider(),
                      _info('🔦', 'Torch', 'Use the torch button for low-light environments.'),
                    ]),
                    const SizedBox(height, 32),

                    // Terms
                    _sectionTitle('TERMS OF USE'),
                    _card(children: [
                      _para('By using OneSpot, you agree to the following terms. Please read them carefully before proceeding.'),
                      _divider(),
                      _bullet('OneSpot is provided "as is" without warranties of any kind, express or implied.'),
                      _bullet('The app uses your device camera solely for real-time object detection. No images or video are stored, transmitted, or shared without your explicit action.'),
                      _bullet('When using cloud AI providers (Claude, ChatGPT, Gemini), image data is sent to the respective third-party API. You are responsible for reviewing their privacy policies.'),
                      _bullet('API keys entered in Settings are stored locally on your device only and are never transmitted to our servers.'),
                      _bullet('OneSpot is not liable for any inaccuracies in object identification or counting results.'),
                      _bullet('You may not use OneSpot for any unlawful purpose, including but not limited to surveillance, harassment, or privacy violations.'),
                      _bullet('The developer reserves the right to update these terms at any time. Continued use of the app constitutes acceptance of the updated terms.'),
                    ]),
                    const SizedBox(height: 20),

                    // Privacy
                    _sectionTitle('PRIVACY POLICY'),
                    _card(children: [
                      _para('OneSpot takes your privacy seriously. Here is exactly what we collect and what we do not.'),
                      _divider(),
                      _subTitle('What we collect'),
                      _bullet('Nothing. OneSpot does not collect, store, or transmit any personal data to our servers.'),
                      _divider(),
                      _subTitle('Camera'),
                      _bullet('Camera access is used exclusively for live object detection within the app. Frames are processed on-device when using YOLO, or sent to your chosen AI provider when using cloud mode.'),
                      _divider(),
                      _subTitle('API Keys'),
                      _bullet('Your API keys are stored locally using Android SharedPreferences and never leave your device.'),
                      _divider(),
                      _subTitle('History'),
                      _bullet('Detection history is stored locally on your device. You can clear it at any time from the History screen.'),
                      _divider(),
                      _subTitle('Third-party AI providers'),
                      _bullet('When using Claude, ChatGPT, or Gemini, cropped image data is sent to those services. Please review their respective privacy policies: Anthropic, OpenAI, Google.'),
                      _divider(),
                      _subTitle('Contact'),
                      _bullet('For privacy concerns, contact: dev@kokkinopoulos.gr'),
                    ]),
                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),

            // Accept bar
            Container(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 28),
              decoration: const BoxDecoration(
                color: Color(0xFF080D1E),
                border: Border(top: BorderSide(color: Color(0xFF1E1E32))),
              ),
              child: Column(
                children: [
                  GestureDetector(
                    onTap: () => setState(() => _accepted = !_accepted),
                    child: Row(
                      children: [
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          width: 22, height: 22,
                          decoration: BoxDecoration(
                            color: _accepted ? const Color(0xFFFFD600) : Colors.transparent,
                            border: Border.all(color: _accepted ? const Color(0xFFFFD600) : Colors.white38, width: 2),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: _accepted ? const Icon(Icons.check, size: 14, color: Colors.black) : null,
                        ),
                        const SizedBox(width: 12),
                        const Expanded(
                          child: Text('I have read and agree to the Terms of Use and Privacy Policy.',
                            style: TextStyle(color: Colors.white70, fontSize: 13)),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _accepted ? _accept : null,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFFFD600),
                        disabledBackgroundColor: const Color(0xFF1E1E32),
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      child: Text('GET STARTED',
                        style: TextStyle(
                          color: _accepted ? Colors.black : Colors.white24,
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                          letterSpacing: 2,
                        )),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _sectionTitle(String text) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: Text(text, style: const TextStyle(color: Color(0xFFFFD600), fontSize: 11, letterSpacing: 2, fontWeight: FontWeight.bold)),
  );

  Widget _card({required List<Widget> children}) => Container(
    margin: const EdgeInsets.only(bottom: 20),
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
      Container(
        width: 24, height: 24,
        decoration: const BoxDecoration(color: Color(0xFFFFD600), shape: BoxShape.circle),
        child: Center(child: Text(num, style: const TextStyle(color: Colors.black, fontSize: 12, fontWeight: FontWeight.bold))),
      ),
      const SizedBox(width: 12),
      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text(desc, style: const TextStyle(color: Colors.white54, fontSize: 13, height: 1.5)),
      ])),
    ]),
  );

  Widget _info(String icon, String title, String desc) => Padding(
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

  Widget _para(String text) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 6),
    child: Text(text, style: const TextStyle(color: Colors.white70, fontSize: 13, height: 1.6)),
  );

  Widget _bullet(String text) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 4),
    child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('• ', style: TextStyle(color: Color(0xFFFFD600), fontSize: 14)),
      Expanded(child: Text(text, style: const TextStyle(color: Colors.white54, fontSize: 13, height: 1.5))),
    ]),
  );

  Widget _subTitle(String text) => Padding(
    padding: const EdgeInsets.only(top: 4, bottom: 4),
    child: Text(text, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
  );

  Widget _divider() => const Divider(color: Color(0xFF1E2E4A), height: 20);
}
"""

with open("lib/features/onboarding/onboarding_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
