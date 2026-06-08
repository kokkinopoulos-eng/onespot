with open("lib/core/services/vision_api_service.dart", encoding="utf-8") as f:
    code = f.read()

old_prompt = '"You are given two images:\\n"'
# Find the full prompt string
start = code.find('final prompt =')
end = code.find(';\n', start) + 2
old = code[start:end]
print(f"Found prompt at {start}-{end}")
print(old[:200])
