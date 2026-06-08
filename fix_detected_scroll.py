with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "constraints: BoxConstraints(minWidth: 140, maxWidth: MediaQuery.of(context).size.width * 0.45, maxHeight: MediaQuery.of(context).size.height * 0.35),",
    "constraints: BoxConstraints(minWidth: 140, maxWidth: MediaQuery.of(context).size.width * 0.45, maxHeight: 220),"
)

# Make the items list scrollable
code = code.replace(
    "            else\n              ..._counts.entries.map((e) => Padding(",
    "            else\n              Flexible(child: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: _counts.entries.map((e) => Padding("
)

code = code.replace(
    "                ),\n              )),\n            const Divider(color: Color(0xFF00FF88)",
    "                ),\n              )).toList()))),\n            const Divider(color: Color(0xFF00FF88)"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
