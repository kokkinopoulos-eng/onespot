import 'package:flutter/material.dart';
import '../../core/services/settings_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});
  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final SettingsService _settings = SettingsService();
  String _provider = 'claude';
  final TextEditingController _languageController = TextEditingController();
  final Map<String, TextEditingController> _controllers = {
    'claude': TextEditingController(),
    'chatgpt': TextEditingController(),
    'gemini': TextEditingController(),
  };
  final Map<String, bool> _obscured = {
    'claude': true,
    'chatgpt': true,
    'gemini': true,
  };

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final saved = await _settings.getProvider();
    _provider = (saved == 'yolo') ? 'local' : saved;
    _languageController.text = await _settings.getLanguage();
    final keys = await _settings.getAllKeys();
    keys.forEach((k, v) { if (v != null) _controllers[k]?.text = v; });
    setState(() {});
  }

  Future<void> _save() async {
    await _settings.saveProvider(_provider);
    await _settings.saveLanguage(_languageController.text.trim().isEmpty ? 'English' : _languageController.text.trim());
    for (final e in _controllers.entries) {
      if (e.value.text.isNotEmpty) await _settings.saveApiKey(e.key, e.value.text);
    }
    if (!mounted) return;
    final hasKey = _provider == 'local' ||
        (_controllers[_provider]?.text.isNotEmpty ?? false) ||
        (await _settings.getApiKey(_provider))?.isNotEmpty == true;
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      hasKey
        ? const SnackBar(content: Text('Settings saved ✓'), backgroundColor: Color(0xFF00FF88))
        : SnackBar(
            content: Text('Saved — αλλά δεν υπάρχει API key για $_provider'),
            backgroundColor: const Color(0xFFFF6B00),
            duration: const Duration(seconds: 4),
          ),
    );
  }

  @override
  void dispose() {
    _languageController.dispose();
    _controllers.values.forEach((c) => c.dispose());
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF080810),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F0F1A),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: RichText(text: const TextSpan(
          style: TextStyle(fontFamily: 'BebasNeue', fontSize: 22, letterSpacing: 2),
          children: [
            TextSpan(text: 'ONE', style: TextStyle(color: Colors.white)),
            TextSpan(text: 'SPOT', style: TextStyle(color: Color(0xFF00FF88))),
            TextSpan(text: ' Settings', style: TextStyle(color: Colors.white)),
          ],
        )),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _sectionLabel('AI PROVIDER'),
          _providerSelector(),
          const SizedBox(height: 24),
          _sectionLabel('API KEYS'),
          _keyField('claude', 'Claude (Anthropic)', 'sk-ant-...'),
          const SizedBox(height: 12),
          _keyField('chatgpt', 'ChatGPT (OpenAI)', 'sk-...'),
          const SizedBox(height: 12),
          _keyField('gemini', 'Gemini (Google)', 'AIza...'),
          const SizedBox(height: 24),
          _sectionLabel('HOW TO GET YOUR KEY'),
          _instructions(),
          const SizedBox(height: 24),
          _sectionLabel('RESPONSE LANGUAGE'),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFF0F0F1A),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFF1E1E32)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('AI will reply in this language', style: TextStyle(color: Colors.white54, fontSize: 11)),
                const SizedBox(height: 8),
                TextField(
                  controller: _languageController,
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                  decoration: const InputDecoration(
                    hintText: 'e.g. English, Greek, French...',
                    hintStyle: TextStyle(color: Colors.white24, fontSize: 13),
                    border: InputBorder.none,
                    isDense: true,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          const SizedBox(height: 32),
          ElevatedButton(
            onPressed: _save,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF00FF88),
              foregroundColor: Colors.black,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            child: const Text('SAVE', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, letterSpacing: 2)),
          ),
        ],
      ),
    );
  }

  Widget _sectionLabel(String text) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: Text(text, style: const TextStyle(color: Color(0xFF00FF88), fontSize: 10, letterSpacing: 2)),
  );

  Widget _providerSelector() {
    const icons = {'local': '📱', 'claude': '🤖', 'chatgpt': '💬', 'gemini': '✨'};
    const names = {'local': 'Local', 'claude': 'Claude', 'chatgpt': 'ChatGPT', 'gemini': 'Gemini'};
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: ['local', 'claude', 'chatgpt', 'gemini'].map((p) {
            final active = _provider == p;
            return Expanded(
              child: GestureDetector(
                onTap: () => setState(() => _provider = p),
                child: Container(
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  decoration: BoxDecoration(
                    color: active ? const Color(0xFF00FF88).withOpacity(0.1) : const Color(0xFF0F0F1A),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: active ? const Color(0xFF00FF88) : const Color(0xFF1E1E32)),
                  ),
                  child: Column(children: [
                    Text(icons[p]!, style: const TextStyle(fontSize: 22)),
                    const SizedBox(height: 4),
                    Text(names[p]!, style: TextStyle(color: active ? const Color(0xFF00FF88) : Colors.white38, fontSize: 11)),
                  ]),
                ),
              ),
            );
          }).toList(),
        ),
        Padding(
          padding: const EdgeInsets.only(top: 10),
          child: Text(
            _provider == 'local'
              ? 'Offline — χρησιμοποιεί template matching. Δεν χρειάζεται API key ή internet.'
              : 'Make sure you have entered the API key for ${names[_provider] ?? _provider} below.',
            style: const TextStyle(color: Colors.white38, fontSize: 11),
          ),
        ),
      ],
    );
  }

  Widget _keyField(String key, String label, String hint) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF0F0F1A),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF1E1E32)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(color: Colors.white54, fontSize: 11)),
          const SizedBox(height: 8),
          Row(children: [
            Expanded(
              child: TextField(
                controller: _controllers[key],
                obscureText: _obscured[key]!,
                style: const TextStyle(color: Colors.white, fontSize: 12, fontFamily: 'SpaceMono'),
                decoration: InputDecoration(
                  hintText: hint,
                  hintStyle: const TextStyle(color: Colors.white24, fontSize: 12),
                  border: InputBorder.none,
                  isDense: true,
                ),
              ),
            ),
            GestureDetector(
              onTap: () => setState(() => _obscured[key] = !_obscured[key]!),
              child: Icon(_obscured[key]! ? Icons.visibility_off : Icons.visibility, color: Colors.white38, size: 20),
            ),
          ]),
        ],
      ),
    );
  }

  Widget _instructions() {
    final data = {
      'claude': ('console.anthropic.com', 'Create account → API Keys → Create Key → starts with sk-ant-'),
      'chatgpt': ('platform.openai.com/api-keys', 'Create account → API Keys → Create secret key → starts with sk-'),
      'gemini': ('aistudio.google.com/app/apikey', 'Sign in with Google → Get API key → Create API key — FREE tier available'),
    };
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF0F0F1A),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF1E1E32)),
      ),
      child: Column(
        children: data.entries.map((e) => Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 20, height: 20,
                decoration: const BoxDecoration(color: Color(0xFF00FF88), shape: BoxShape.circle),
                child: Center(child: Text({'claude':'C','chatgpt':'G','gemini':'G2'}[e.key]!,
                  style: const TextStyle(color: Colors.black, fontSize: 9, fontWeight: FontWeight.bold))),
              ),
              const SizedBox(width: 10),
              Expanded(child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(e.value.$1, style: const TextStyle(color: Color(0xFF00FF88), fontSize: 11)),
                  const SizedBox(height: 2),
                  Text(e.value.$2, style: const TextStyle(color: Colors.white38, fontSize: 11, height: 1.5)),
                ],
              )),
            ],
          ),
        )).toList(),
      ),
    );
  }
}

