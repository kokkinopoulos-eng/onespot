with open("lib/core/services/vision_api_service.dart", encoding="utf-8") as f:
    code = f.read()

old_prompt = """    const prompt =
        'You are given two images:\\n'
        '- Image 1 (TEMPLATE): the specific object the user has selected to count\\n'
        '- Image 2 (FULL FRAME): the complete scene to search\\n\\n'
        'The object in Image 1 is what the user wants to count. '
        'Focus ONLY on finding more instances of THAT specific object type. '
        'Ignore all other objects even if they are prominent in the scene.\\n\\n'
        'Find EVERY instance of the same object CATEGORY as Image 1:\\n'
        '- Include ALL sizes (small, large, tiny)\\n'
        '- Include ALL colors and shades\\n'
        '- Include partially visible objects\\n'
        '- Include objects at different angles/orientations\\n'
        '- Return ONLY objects of the EXACT SAME CATEGORY as Image 1\\n'
        '- Do NOT return objects of other categories\\n\\n'
        'Return ONLY a JSON array, no other text:\\n'
        '[{"x":0.1,"y":0.2,"w":0.15,"h":0.2},...]\\n'
        'where x,y,w,h are fractions (0.0-1.0) of the FULL IMAGE (Image 2) dimensions.\\n'
        'x,y = top-left corner, w,h = width and height.\\n'
        'If none found return []';"""

new_prompt = """    const prompt =
        'Look at Image 1 (template object) and Image 2 (full scene). '
        'Find ALL objects in Image 2 that are the same type as Image 1. '
        'Output ONLY a raw JSON array with no explanation, no markdown, no text before or after. '
        'Format: [{"x":0.1,"y":0.2,"w":0.1,"h":0.1}] '
        'where values are 0.0-1.0 fractions of Image 2 dimensions. '
        'If none found output exactly: []';"""

code = code.replace(old_prompt, new_prompt)
with open("lib/core/services/vision_api_service.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done" if old_prompt not in open("lib/core/services/vision_api_service.dart", encoding="utf-8").read() else "Not found")
