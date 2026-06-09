import 'dart:math' as math;
import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/foundation.dart';
import 'vision_api_service.dart';

/// Offline object counting via Normalized Cross-Correlation (NCC).
/// No network, no AI model. Slides the template over the full image at
/// multiple scales and finds visually similar patches.
class LocalSimilarityService {
  /// Max dimension of the work image — bigger = more accurate but slower.
  static const int _dim = 130;

  /// NCC similarity threshold: 1.0 = identical, 0.0 = unrelated.
  /// Lower → more matches (but also more false positives).
  static const double _threshold = 0.60;

  /// Template scales to try — handles objects at different distances/sizes.
  static const List<double> _scales = [0.7, 0.85, 1.0, 1.2, 1.45];

  Future<SimilarResult> findSimilar(
      Uint8List templateBytes, Uint8List fullBytes) async {
    final tImg = await _decode(templateBytes);
    final fImg = await _decode(fullBytes);

    // Scale both images by the SAME factor so relative sizes are preserved.
    final s = _dim / math.max(fImg.width, fImg.height);
    final fw = math.max(1, (fImg.width * s).round());
    final fh = math.max(1, (fImg.height * s).round());

    final fScaled = await _resizeImg(fImg, fw, fh);
    final fGray = await _toGray(fScaled);

    final baseTw = math.max(4, (tImg.width * s).round());
    final baseTh = math.max(4, (tImg.height * s).round());
    final tBase = await _resizeImg(tImg, baseTw, baseTh);

    final allPeaks = <_Peak>[];

    for (final sf in _scales) {
      final tw = math.max(4, (baseTw * sf).round());
      final th = math.max(4, (baseTh * sf).round());
      if (tw >= fw || th >= fh) continue;

      final tScaled = await _resizeImg(tBase, tw, th);
      final tGray = await _toGray(tScaled);

      final rawPeaks = await compute(_nccCompute, _NccArgs(
        t: tGray, tw: tw, th: th,
        f: fGray, fw: fw, fh: fh,
        threshold: _threshold,
      ));

      for (final p in rawPeaks) {
        allPeaks.add(_Peak(
          x1: p.x / fw,
          y1: p.y / fh,
          x2: (p.x + tw) / fw,
          y2: (p.y + th) / fh,
          score: p.score,
        ));
      }
    }

    final final_ = _nms(allPeaks);
    final items = final_.map((p) =>
      <String, dynamic>{'x1': p.x1, 'y1': p.y1, 'x2': p.x2, 'y2': p.y2}
    ).toList();

    return SimilarResult(name: 'αντικείμενο', items: items);
  }

  // ── helpers ──────────────────────────────────────────────────────────────

  Future<ui.Image> _decode(Uint8List bytes) async {
    final codec = await ui.instantiateImageCodec(bytes);
    return (await codec.getNextFrame()).image;
  }

  Future<ui.Image> _resizeImg(ui.Image img, int w, int h) async {
    final rec = ui.PictureRecorder();
    ui.Canvas(rec).drawImageRect(
      img,
      ui.Rect.fromLTWH(0, 0, img.width.toDouble(), img.height.toDouble()),
      ui.Rect.fromLTWH(0, 0, w.toDouble(), h.toDouble()),
      ui.Paint(),
    );
    return rec.endRecording().toImage(w, h);
  }

  Future<Float32List> _toGray(ui.Image img) async {
    final bd = await img.toByteData(format: ui.ImageByteFormat.rawRgba);
    if (bd == null) return Float32List(img.width * img.height);
    final src = bd.buffer.asUint8List();
    final g = Float32List(img.width * img.height);
    for (int i = 0; i < g.length; i++) {
      g[i] = (0.299 * src[i * 4] + 0.587 * src[i * 4 + 1] + 0.114 * src[i * 4 + 2]) / 255.0;
    }
    return g;
  }

  List<_Peak> _nms(List<_Peak> peaks, {double iouThresh = 0.25}) {
    peaks.sort((a, b) => b.score.compareTo(a.score));
    final used = List.filled(peaks.length, false);
    final keep = <_Peak>[];
    for (int i = 0; i < peaks.length; i++) {
      if (used[i]) continue;
      keep.add(peaks[i]);
      for (int j = i + 1; j < peaks.length; j++) {
        if (!used[j] && _iou(peaks[i], peaks[j]) > iouThresh) used[j] = true;
      }
    }
    return keep;
  }

  double _iou(_Peak a, _Peak b) {
    final ix1 = math.max(a.x1, b.x1), iy1 = math.max(a.y1, b.y1);
    final ix2 = math.min(a.x2, b.x2), iy2 = math.min(a.y2, b.y2);
    if (ix2 <= ix1 || iy2 <= iy1) return 0;
    final inter = (ix2 - ix1) * (iy2 - iy1);
    return inter / ((a.x2-a.x1)*(a.y2-a.y1) + (b.x2-b.x1)*(b.y2-b.y1) - inter);
  }
}

// ── Isolate-safe types ────────────────────────────────────────────────────────

class _NccArgs {
  final Float32List t;
  final int tw, th;
  final Float32List f;
  final int fw, fh;
  final double threshold;
  const _NccArgs({
    required this.t, required this.tw, required this.th,
    required this.f, required this.fw, required this.fh,
    required this.threshold,
  });
}

class _RawPeak {
  final int x, y;
  final double score;
  const _RawPeak(this.x, this.y, this.score);
}

class _Peak {
  final double x1, y1, x2, y2, score;
  const _Peak({required this.x1, required this.y1, required this.x2, required this.y2, required this.score});
}

// ── Top-level isolate function ────────────────────────────────────────────────

List<_RawPeak> _nccCompute(_NccArgs a) {
  final t = a.t;
  final tw = a.tw, th = a.th;
  final f = a.f;
  final fw = a.fw, fh = a.fh;
  final threshold = a.threshold;

  final ow = fw - tw + 1;
  final oh = fh - th + 1;
  if (ow <= 0 || oh <= 0) return [];

  // Template mean + norm
  double tSum = 0;
  for (int i = 0; i < t.length; i++) tSum += t[i];
  final tMean = tSum / t.length;
  double tSsq = 0;
  for (int i = 0; i < t.length; i++) {
    final d = t[i] - tMean;
    tSsq += d * d;
  }
  final tNorm = math.sqrt(tSsq);
  if (tNorm < 1e-8) return [];

  final candidates = <_RawPeak>[];

  for (int y = 0; y < oh; y++) {
    for (int x = 0; x < ow; x++) {
      // Patch mean
      double pSum = 0;
      for (int j = 0; j < th; j++) {
        final rowBase = (y + j) * fw + x;
        for (int i = 0; i < tw; i++) pSum += f[rowBase + i];
      }
      final pMean = pSum / (tw * th);

      // NCC
      double num = 0, pSsq = 0;
      for (int j = 0; j < th; j++) {
        final fRow = (y + j) * fw + x;
        final tRow = j * tw;
        for (int i = 0; i < tw; i++) {
          final td = t[tRow + i] - tMean;
          final pd = f[fRow + i] - pMean;
          num += td * pd;
          pSsq += pd * pd;
        }
      }
      final denom = tNorm * math.sqrt(pSsq);
      final ncc = denom < 1e-8 ? 0.0 : num / denom;
      if (ncc >= threshold) candidates.add(_RawPeak(x, y, ncc));
    }
  }

  // Local NMS inside the isolate to reduce serialization cost.
  if (candidates.isEmpty) return [];
  candidates.sort((a, b) => b.score.compareTo(a.score));
  final minDist2 = ((tw + th) ~/ 4);
  final md2 = minDist2 * minDist2;
  final used = List.filled(candidates.length, false);
  final result = <_RawPeak>[];
  for (int i = 0; i < candidates.length; i++) {
    if (used[i]) continue;
    result.add(candidates[i]);
    if (result.length >= 80) break; // safety cap
    for (int j = i + 1; j < candidates.length; j++) {
      if (used[j]) continue;
      final dx = candidates[i].x - candidates[j].x;
      final dy = candidates[i].y - candidates[j].y;
      if (dx * dx + dy * dy < md2) used[j] = true;
    }
  }
  return result;
}
