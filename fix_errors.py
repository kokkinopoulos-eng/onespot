import re

# Fix history_screen.dart
with open("lib/features/history/history_screen.dart", encoding="utf-8") as f:
    code = f.read()
code = code.replace("'\\${obj['count']}'", "'${obj[\"count\"]}'")
code = code.replace("'\\${obj['name']}'", "'${obj[\"name\"]}'")
code = code.replace("'\\${result['similar']}'", "'${result[\"similar\"]}'")
code = code.replace("Similar: \\${result['similar']}", "Similar: ${result[\"similar\"]}")
code = code.replace("'\\${dt.day}/\\${dt.month}/\\${dt.year} \\${dt.hour.toString().padLeft(2,", "'${dt.day}/${dt.month}/${dt.year} ${dt.hour.toString().padLeft(2,")
code = code.replace("'0')}:\\${dt.minute.toString().padLeft(2,'0')}'", "'0')}:${dt.minute.toString().padLeft(2,'0')}'")
with open("lib/features/history/history_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)

# Fix camera_screen.dart - add async to setState block
with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()
code = code.replace(
    "setState(() {\n        _identifyResult = result;\n        _isIdentifying = false;\n        await _historyService.add(_mode.name, result);",
    "setState(() {\n        _identifyResult = result;\n        _isIdentifying = false;\n      });\n      await _historyService.add(_mode.name, result);\n      setState(() {"
)
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)

print("Done")
