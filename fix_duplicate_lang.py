with open("lib/features/settings/settings_screen.dart", encoding="utf-8") as f:
    lines = f.readlines()

# Remove duplicate lines - keep first occurrence
seen = []
new_lines = []
skip_patterns = [
    "_languageController.text = await _settings.getLanguage();",
    "await _settings.saveLanguage(",
    "_languageController.dispose();",
]

counts = {p: 0 for p in skip_patterns}

for line in lines:
    stripped = line.strip()
    is_dup = False
    for p in skip_patterns:
        if p in stripped:
            counts[p] += 1
            if counts[p] > 1:
                is_dup = True
                break
    if not is_dup:
        new_lines.append(line)

# Also fix duplicate RESPONSE LANGUAGE section in UI
content = "".join(new_lines)

# Find second occurrence of RESPONSE LANGUAGE section and remove it
first = content.find("_sectionLabel('RESPONSE LANGUAGE')")
second = content.find("_sectionLabel('RESPONSE LANGUAGE')", first + 1)

if second != -1:
    # Find the end of the second block (next _sectionLabel or save button)
    end = content.find("const SizedBox(height: 32),\n          ElevatedButton(", second)
    if end == -1:
        end = content.find("_sectionLabel(", second + 1)
    if end != -1:
        content = content[:second] + content[end:]

with open("lib/features/settings/settings_screen.dart", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
