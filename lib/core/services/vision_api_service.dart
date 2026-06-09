import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

enum ApiProvider { claude, chatgpt, gemini }

class SimilarResult {
  final String name;
  final List<Map<String, dynamic>> items;
  SimilarResult({required this.name, required this.items});
}

class VisionApiService {
  final ApiProvider provider;
  final String apiKey;

  VisionApiService({required this.provider, required this.apiKey});

  Future<Map<String, dynamic>> identify(Uint8List imageBytes) async {
    return identifyWithPrompt(imageBytes,
      'What is the main object? Reply ONLY as JSON: {"name":"object name","description":"one sentence","similar":N} where N is count of similar objects visible.');
  }

  Future<Map<String, dynamic>> identifyWithPrompt(Uint8List imageBytes, String prompt) async {
    final base64Image = base64Encode(imageBytes);
    switch (provider) {
      case ApiProvider.claude:
        return _callClaude(base64Image, prompt);
      case ApiProvider.chatgpt:
        return _callOpenAI(base64Image, prompt);
      case ApiProvider.gemini:
        return _callGemini(base64Image, prompt);
    }
  }

  /// Sends [templateBytes] (the cropped selection) and [fullBytes] (the full
  /// camera frame) to the provider and returns bounding boxes for all objects
  /// in the full frame that match the template type.
  /// Each box: {x, y, w, h} as fractions (0.0–1.0) of full-image dimensions,
  /// where (x, y) is the top-left corner.
  Future<SimilarResult> findSimilar(
      Uint8List templateBytes, Uint8List fullBytes,
      {String language = 'Greek', String? userHint}) async {
    final b64Template = base64Encode(templateBytes);
    final b64Full = base64Encode(fullBytes);
    // Detect actual format from magic bytes so the declared media_type is always
    // correct. takePicture() always produces JPEG; toByteData(png) always produces
    // PNG — but relying on the call-site for that invariant has already caused a
    // Claude 400 error, so we detect here instead.
    final mimeTemplate = _detectMime(templateBytes);
    final mimeFull = _detectMime(fullBytes);
    final hintSection = userHint != null && userHint.trim().isNotEmpty
        ? 'USER INPUT: "${userHint.trim()}"\n'
          'The user may have written a question (e.g. "how many leaves?") or an instruction '
          '(e.g. "count only the red ones"). Either way, treat it as a directive that '
          'OVERRIDES OR REFINES the default counting rules below. '
          'If it is a question, answer it by counting accordingly.\n\n'
        : '';
    final prompt = hintSection +
        'You are a precise object detector. '
        'Image 1 is a TEMPLATE. The object you must search for is the one at the CENTRE of Image 1. '
        'Ignore anything near the edges of Image 1 — focus only on the central object. '
        'Study that central object carefully: note its type, shape, colour, and texture. '
        'Image 2 is the full camera scene. '
        'TASK: Find every real, physical instance in Image 2 that belongs to the SAME SPECIFIC TYPE '
        'as the central object in Image 1. '
        'SIMILARITY RULES: '
        '  • Must be the same specific type — do NOT generalise to a broader category. '
        '    Example: a small step-light ≠ a large globe lamp; a flip-flop ≠ a shoe. '
        '  • For natural/organic objects (leaves, seeds, petals, stones, etc.) size and angle '
        '    NATURALLY vary — count ALL instances of the same species/kind regardless of '
        '    orientation, partial overlap, or size difference caused by distance. '
        '  • For man-made objects (bottles, chairs, shoes, etc.) keep the stricter shape+size match. '
        'COUNTING RULES: '
        '1. Scan systematically: top-left → top-right, row by row, until bottom-right. '
        '2. Count ALL matching instances — even partially occluded, overlapping, or at image edges. '
        '3. For dense clusters (leaves on a plant, seeds in a pile): count each individual unit. '
        '   Do NOT stop early — scan the ENTIRE image. '
        '4. DO NOT count objects visible on a turned-on TV/monitor/phone screen. '
        '5. Count each object EXACTLY ONCE — no duplicates. '
        'After your initial scan, do ONE re-scan to confirm you have not missed any instances. '
        'BOUNDING BOX: Draw the tightest possible rectangle around each matched object. '
        'x1,y1 = TOP-LEFT corner, x2,y2 = BOTTOM-RIGHT corner, '
        'as fractions 0.0-1.0 of Image 2 dimensions. '
        'NAME: use the specific common name in $language (e.g. "σαγιονάρα", "φύλλο pothos"). '
        'If you cannot identify the exact type, use "αντικείμενο" — but still count and box every instance. '
        'Output ONLY raw JSON — no markdown, no extra text. '
        'Format: {"name":"object name in $language","items":[{"x1":0.1,"y1":0.2,"x2":0.3,"y2":0.4},...]}. '
        'If there are genuinely ZERO matching objects: {"name":"αντικείμενο","items":[]}';
    switch (provider) {
      case ApiProvider.claude:
        return _callClaudeSimilar(b64Template, mimeTemplate, b64Full, mimeFull, prompt);
      case ApiProvider.chatgpt:
        return _callOpenAISimilar(b64Template, mimeTemplate, b64Full, mimeFull, prompt);
      case ApiProvider.gemini:
        return _callGeminiSimilar(b64Template, mimeTemplate, b64Full, mimeFull, prompt);
    }
  }

  /// Returns 'image/jpeg' if [bytes] has the JPEG magic header, else 'image/png'.
  String _detectMime(Uint8List bytes) =>
      bytes.length >= 3 && bytes[0] == 0xFF && bytes[1] == 0xD8 && bytes[2] == 0xFF
          ? 'image/jpeg'
          : 'image/png';

  Future<Map<String, dynamic>> _callClaude(String base64Image, String prompt) async {
    final res = await http.post(
      Uri.parse('https://api.anthropic.com/v1/messages'),
      headers: {'Content-Type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01'},
      body: jsonEncode({
        'model': 'claude-sonnet-4-6',
        'max_tokens': 1024,
        'messages': [{
          'role': 'user',
          'content': [
            {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': base64Image}},
            {'type': 'text', 'text': prompt}
          ]
        }]
      }),
    );
    final data = jsonDecode(res.body);
    if (res.statusCode != 200) {
      throw Exception('Claude API ${res.statusCode}: ${_apiErrorMessage(data, res.body)}');
    }
    final content = data['content'];
    if (content is! List || content.isEmpty || content[0]['text'] == null) {
      throw Exception('Claude returned no text. Raw: ${res.body}');
    }
    return _extractJson(content[0]['text'] as String);
  }

  Future<Map<String, dynamic>> _callOpenAI(String base64Image, String prompt) async {
    final res = await http.post(
      Uri.parse('https://api.openai.com/v1/chat/completions'),
      headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $apiKey'},
      body: jsonEncode({
        'model': 'gpt-4o-mini',
        'max_tokens': 1024,
        'messages': [{
          'role': 'user',
          'content': [
            {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,$base64Image'}},
            {'type': 'text', 'text': prompt}
          ]
        }]
      }),
    );
    final data = jsonDecode(res.body);
    if (res.statusCode != 200) {
      throw Exception('OpenAI API ${res.statusCode}: ${_apiErrorMessage(data, res.body)}');
    }
    final choices = data['choices'];
    if (choices is! List || choices.isEmpty || choices[0]['message']?['content'] == null) {
      throw Exception('OpenAI returned no text. Raw: ${res.body}');
    }
    return _extractJson(choices[0]['message']['content'] as String);
  }

  Future<Map<String, dynamic>> _callGemini(String base64Image, String prompt) async {
    final res = await http.post(
      Uri.parse('https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$apiKey'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'contents': [{
          'parts': [
            {'inline_data': {'mime_type': 'image/jpeg', 'data': base64Image}},
            {'text': prompt}
          ]
        }]
      }),
    );
    final data = jsonDecode(res.body);
    if (res.statusCode != 200) {
      throw Exception('Gemini API ${res.statusCode}: ${_apiErrorMessage(data, res.body)}');
    }
    final candidates = data['candidates'];
    if (candidates is! List || candidates.isEmpty) {
      throw Exception('Gemini returned no candidates. Raw: ${res.body}');
    }
    final parts = candidates[0]['content']?['parts'];
    if (parts is! List || parts.isEmpty || parts[0]['text'] == null) {
      throw Exception('Gemini returned no text. Raw: ${res.body}');
    }
    return _extractJson(parts[0]['text'] as String);
  }

  // Pulls a human-readable message out of a provider error JSON body.
  String _apiErrorMessage(dynamic data, String rawBody) {
    if (data is Map) {
      final err = data['error'];
      if (err is Map && err['message'] != null) return err['message'].toString();
      if (err is String) return err;
      if (data['message'] != null) return data['message'].toString();
    }
    return rawBody;
  }

  Future<SimilarResult> _callClaudeSimilar(
      String b64Template, String mimeTemplate,
      String b64Full, String mimeFull,
      String prompt) async {
    final res = await http.post(
      Uri.parse('https://api.anthropic.com/v1/messages'),
      headers: {'Content-Type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01'},
      body: jsonEncode({
        'model': 'claude-sonnet-4-6',
        'max_tokens': 1024,
        'messages': [{
          'role': 'user',
          'content': [
            {'type': 'image', 'source': {'type': 'base64', 'media_type': mimeTemplate, 'data': b64Template}},
            {'type': 'image', 'source': {'type': 'base64', 'media_type': mimeFull, 'data': b64Full}},
            {'type': 'text', 'text': prompt},
          ],
        }],
      }),
    );
    final data = jsonDecode(res.body);
    if (res.statusCode != 200) throw Exception('Claude ${res.statusCode}: ${_apiErrorMessage(data, res.body)}');
    final content = data['content'];
    if (content is! List || content.isEmpty || content[0]['text'] == null) {
      throw Exception('Claude returned no text. Raw: ${res.body}');
    }
    final rawText = content[0]['text'] as String;
    debugPrint('SIMILAR_RAW: ${rawText.substring(0, rawText.length.clamp(0, 200))}');
    final result = _extractSimilarResult(rawText);
    debugPrint('SIMILAR_PARSED: name=${result.name} count=${result.items.length}');
    return result;
  }

  Future<SimilarResult> _callOpenAISimilar(
      String b64Template, String mimeTemplate,
      String b64Full, String mimeFull,
      String prompt) async {
    final res = await http.post(
      Uri.parse('https://api.openai.com/v1/chat/completions'),
      headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $apiKey'},
      body: jsonEncode({
        'model': 'gpt-4o-mini',
        'max_tokens': 1024,
        'messages': [{
          'role': 'user',
          'content': [
            {'type': 'image_url', 'image_url': {'url': 'data:$mimeTemplate;base64,$b64Template'}},
            {'type': 'image_url', 'image_url': {'url': 'data:$mimeFull;base64,$b64Full'}},
            {'type': 'text', 'text': prompt},
          ],
        }],
      }),
    );
    final data = jsonDecode(res.body);
    if (res.statusCode != 200) throw Exception('OpenAI ${res.statusCode}: ${_apiErrorMessage(data, res.body)}');
    final choices = data['choices'];
    if (choices is! List || choices.isEmpty || choices[0]['message']?['content'] == null) {
      throw Exception('OpenAI returned no text. Raw: ${res.body}');
    }
    return _extractSimilarResult(choices[0]['message']['content'] as String);
  }

  Future<SimilarResult> _callGeminiSimilar(
      String b64Template, String mimeTemplate,
      String b64Full, String mimeFull,
      String prompt) async {
    final res = await http.post(
      Uri.parse('https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$apiKey'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'contents': [{
          'parts': [
            {'inline_data': {'mime_type': mimeTemplate, 'data': b64Template}},
            {'inline_data': {'mime_type': mimeFull, 'data': b64Full}},
            {'text': prompt},
          ],
        }],
      }),
    );
    final data = jsonDecode(res.body);
    if (res.statusCode != 200) throw Exception('Gemini ${res.statusCode}: ${_apiErrorMessage(data, res.body)}');
    final candidates = data['candidates'];
    if (candidates is! List || candidates.isEmpty) throw Exception('Gemini no candidates. Raw: ${res.body}');
    final parts = candidates[0]['content']?['parts'];
    if (parts is! List || parts.isEmpty || parts[0]['text'] == null) {
      throw Exception('Gemini no text. Raw: ${res.body}');
    }
    return _extractSimilarResult(parts[0]['text'] as String);
  }

  // Robustly extracts a JSON object from model text that may include code
  // fences or surrounding prose.
  Map<String, dynamic> _extractJson(String text) {
    var t = text.replaceAll('```json', '').replaceAll('```', '').trim();
    final start = t.indexOf('{');
    final end = t.lastIndexOf('}');
    if (start != -1 && end != -1 && end > start) {
      t = t.substring(start, end + 1);
    }
    return jsonDecode(t) as Map<String, dynamic>;
  }

  // Parses {"name":"...","items":[{cx,cy},...]} from model output.
  // Falls back gracefully: if the model still returns a bare array, wraps it
  // with a generic name so nothing crashes.
  SimilarResult _extractSimilarResult(String text) {
    var t = text.replaceAll('```json', '').replaceAll('```', '').trim();
    // Try object format first
    final objStart = t.indexOf('{');
    final objEnd = t.lastIndexOf('}');
    if (objStart != -1 && objEnd > objStart) {
      try {
        final map = jsonDecode(t.substring(objStart, objEnd + 1)) as Map<String, dynamic>;
        final name = (map['name'] as String?) ?? 'αντικείμενο';
        final rawItems = map['items'];
        if (rawItems is List) {
          return SimilarResult(
            name: name,
            items: rawItems.whereType<Map<String, dynamic>>().toList(),
          );
        }
      } catch (_) {}
    }
    // Fallback: bare array (old format)
    final arrStart = t.indexOf('[');
    final arrEnd = t.lastIndexOf(']');
    if (arrStart != -1 && arrEnd > arrStart) {
      try {
        final list = jsonDecode(t.substring(arrStart, arrEnd + 1));
        if (list is List) {
          return SimilarResult(
            name: 'αντικείμενο',
            items: list.whereType<Map<String, dynamic>>().toList(),
          );
        }
      } catch (_) {}
    }
    return SimilarResult(name: 'αντικείμενο', items: []);
  }

  // Robustly extracts a JSON array from model text that may include code
  // fences or surrounding prose.
  List<Map<String, dynamic>> _extractJsonList(String text) {
    var t = text.replaceAll('```json', '').replaceAll('```', '').trim();
    final start = t.indexOf('[');
    final end = t.lastIndexOf(']');
    if (start == -1 || end == -1 || end <= start) return [];
    t = t.substring(start, end + 1);
    final list = jsonDecode(t);
    if (list is! List) return [];
    return list.whereType<Map<String, dynamic>>().toList();
  }
}
