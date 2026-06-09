with open("lib/core/services/vision_api_service.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    """    const prompt =
        'Look at Image 1 (template object) and Image 2 (full scene). '
        'Find ALL objects in Image 2 that are the same type as Image 1. '
        'Output ONLY a raw JSON array with no explanation, no markdown, no text before or after. '
        'Format: [{"x":0.1,"y":0.2,"w":0.1,"h":0.1}] '
        'where values are 0.0-1.0 fractions of Image 2 dimensions. '
        'If none found output exactly: []';""",
    """    const prompt =
        'Look at Image 1 (template object) and Image 2 (full scene). '
        'Find ALL objects in Image 2 that are the same type as Image 1. '
        'For each object found, return the CENTER POINT only. '
        'Output ONLY a raw JSON array with no explanation, no markdown, no text before or after. '
        'Format: [{"cx":0.3,"cy":0.4},{"cx":0.6,"cy":0.7}] '
        'where cx,cy are 0.0-1.0 fractions of Image 2 dimensions (center of each object). '
        'If none found output exactly: []';"""
)

with open("lib/core/services/vision_api_service.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
