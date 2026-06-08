class Detection {
  final String label;
  final double confidence;
  final Rect boundingBox;

  const Detection({
    required this.label,
    required this.confidence,
    required this.boundingBox,
  });
}

class Rect {
  final double x, y, width, height;
  const Rect({required this.x, required this.y, required this.width, required this.height});
}
