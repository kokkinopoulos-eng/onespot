with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    lines = f.readlines()

# Find the problematic section and rewrite it
start = None
for i, line in enumerate(lines):
    if "Flexible(child: SingleChildScrollView" in line:
        start = i
        break

if start is not None:
    # Find end of this section (the line with just "))")
    end = None
    for i in range(start, min(start+20, len(lines))):
        if "const Divider" in lines[i]:
            end = i
            break
    
    if end is not None:
        new_lines = [
            "              Flexible(child: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: _counts.entries.map((e) => Padding(\n",
            "                padding: const EdgeInsets.symmetric(vertical: 2),\n",
            "                child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [\n",
            "                  Expanded(child: Text(e.key, style: const TextStyle(color: Colors.white, fontSize: 12), overflow: TextOverflow.ellipsis)),\n",
            "                  Text(e.value.toString(), style: const TextStyle(color: Color(0xFF00FF88), fontSize: 14, fontWeight: FontWeight.bold)),\n",
            "                ]),\n",
            "              )).toList()))),\n",
        ]
        lines[start:end] = new_lines
        with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("Done")
    else:
        print("End not found")
else:
    print("Start not found")
