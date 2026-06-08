with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

old = """            else
              Flexible(child: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: _counts.entries.map((e) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                  Expanded(child: Text(e.key, style: const TextStyle(color: Colors.white, fontSize: 12), overflow: TextOverflow.ellipsis)),
                  Text('${e.value}', style: const TextStyle(color: Color(0xFF00FF88), fontSize: 14, fontWeight: FontWeight.bold)),
                ]),
              )),
            const Divider"""

new = """            else
              Flexible(child: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: _counts.entries.map((e) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                  Expanded(child: Text(e.key, style: const TextStyle(color: Colors.white, fontSize: 12), overflow: TextOverflow.ellipsis)),
                  Text('${e.value}', style: const TextStyle(color: Color(0xFF00FF88), fontSize: 14, fontWeight: FontWeight.bold)),
                ]),
              )).toList()))),
            const Divider"""

code = code.replace(old, new)
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done" if old in open("lib/features/camera/camera_screen.dart", encoding="utf-8").read() == False else "Not found")
