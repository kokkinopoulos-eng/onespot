with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

old = """    return Scaffold(
      backgroundColor: Colors.black,
      extendBodyBehindAppBar: true,
      body: Column(
        children: [
          Expanded(
            child: Stack(
              fit: StackFit.expand,
              children: [
                _buildFullScreenPreview(),
                Positioned.fill(
                  child: Listener(
                    behavior: HitTestBehavior.opaque,
                    onPointerDown: _onPointerDown,
                    onPointerMove: _onPointerMove,
                    onPointerUp: _onPointerUp,
                    onPointerCancel: _onPointerCancel,
                  ),
                ),
                _buildTopBar(),
                _buildModeSelector(),
                _buildCounterPanel(),
                if (_selectionRect != null) _buildSelectionRect(),
                if (_dotPosition != null) _buildDot(),
                _buildZoomSlider(),
                if (_tapPosition != null) _buildRipple(),
                if (_isIdentifying) _buildIdentifyingIndicator(),
                if (_showingToast) _buildToast(),
                if (_lastError != null) _buildErrorCard(),
              ],
            ),
          ),
          _buildBottomBar(),
        ],
      ),
    );"""

new = """    return Scaffold(
      backgroundColor: Colors.black,
      body: Column(
        children: [
          _buildTopBar(),
          _buildModeSelector(),
          Expanded(
            child: Stack(
              fit: StackFit.expand,
              children: [
                _buildFullScreenPreview(),
                Positioned.fill(
                  child: Listener(
                    behavior: HitTestBehavior.opaque,
                    onPointerDown: _onPointerDown,
                    onPointerMove: _onPointerMove,
                    onPointerUp: _onPointerUp,
                    onPointerCancel: _onPointerCancel,
                  ),
                ),
                if (_selectionRect != null) _buildSelectionRect(),
                if (_dotPosition != null) _buildDot(),
                _buildZoomSlider(),
                if (_tapPosition != null) _buildRipple(),
                if (_isIdentifying) _buildIdentifyingIndicator(),
                if (_showingToast) _buildToast(),
                if (_lastError != null) _buildErrorCard(),
              ],
            ),
          ),
          _buildCounterPanel(),
          _buildBottomBar(),
        ],
      ),
    );"""

code = code.replace(old, new)
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done" if old not in open("lib/features/camera/camera_screen.dart", encoding="utf-8").read() else "Not found")
