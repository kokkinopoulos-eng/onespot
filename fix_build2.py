with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

old = """    return Scaffold(
      backgroundColor: Colors.black,
      extendBodyBehindAppBar: true,
      body: Stack(
          fit: StackFit.expand,
          children: [
            SizedBox.expand(child: CameraPreview(_controller!)),
            _buildTopBar(),
            _buildModeSelector(),
            _buildCounterPanel(),
            _buildBottomBar(),
            if (_tapPosition != null) _buildRipple(),
            GestureDetector(onTapDown: _onTap, child: Container(color: Colors.transparent)),
            if (_identifyResult != null || _isIdentifying) _buildIdentifyPopup(),
          ],
        ),
      ),
    );"""

new = """    return Scaffold(
      backgroundColor: Colors.black,
      extendBodyBehindAppBar: true,
      body: Stack(
        fit: StackFit.expand,
        children: [
          SizedBox.expand(child: CameraPreview(_controller!)),
          _buildTopBar(),
          _buildModeSelector(),
          _buildCounterPanel(),
          _buildBottomBar(),
          if (_tapPosition != null) _buildRipple(),
          if (_identifyResult != null || _isIdentifying) _buildIdentifyPopup(),
          GestureDetector(onTapDown: _onTap, child: Container(color: Colors.transparent)),
        ],
      ),
    );"""

code = code.replace(old, new)
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done" if old in open("lib/features/camera/camera_screen.dart", encoding="utf-8").read() == False else "Not found")
