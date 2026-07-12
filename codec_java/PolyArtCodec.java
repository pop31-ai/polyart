import java.io.*;
import java.util.*;
import java.lang.Math;

/**
 * PolyArt Video Codec v1.0 - Java Implementation
 * Polynomial video compression and decompression.
 */
public class PolyArtCodec {

    // ============================================================
    //  DATA STRUCTURES
    // ============================================================

    static class PolyObject {
        String id;
        String kind;
        double[] xCoeff;
        double[] yCoeff;
        double tMin = 0.0;
        double tMax = 1.0;
        double cx = 0, cy = 0, r = 0;
        String color = "#c8a040";
        double linewidth = 1.0;
        double alpha = 0.8;

        PolyObject() {}
        PolyObject(String kind, String color) {
            this.kind = kind;
            this.color = color;
            this.id = "obj_" + Integer.toHexString(hashCode());
        }
    }

    static class PolyFrame {
        int index;
        String type = "keyframe";
        int width = 640, height = 480;
        String background = "#0d0a1a";
        ArrayList<PolyObject> objects = new ArrayList<>();
        int deltaFrom = -1;
        ArrayList<PolyObject> added = new ArrayList<>();
        ArrayList<String> removed = new ArrayList<>();
        ArrayList<PolyObject> modified = new ArrayList<>();
    }

    static class PolyVideo {
        String format = "polyvid/1.0";
        int width, height, fps;
        int totalFrames;
        int keyframeInterval = 10;
        int polynomialDegree = 6;
        int quantBits = 8;
        ArrayList<PolyFrame> frames = new ArrayList<>();
    }

    // ============================================================
    //  ENCODER
    // ============================================================

    static class PolyVideoEncoder {
        int degree;
        int quantBits;

        PolyVideoEncoder(int degree, int quantBits) {
            this.degree = degree;
            this.quantBits = quantBits;
        }

        boolean[] detectEdges(double[] image, int w, int h, double threshold) {
            boolean[] edges = new boolean[w * h];
            for (int y = 1; y < h - 1; y++) {
                for (int x = 1; x < w - 1; x++) {
                    double gx = -image[(y-1)*w + (x-1)] + image[(y-1)*w + (x+1)]
                              - 2*image[y*w + (x-1)] + 2*image[y*w + (x+1)]
                              - image[(y+1)*w + (x-1)] + image[(y+1)*w + (x+1)];
                    double gy = -image[(y-1)*w + (x-1)] - 2*image[(y-1)*w + x] - image[(y-1)*w + (x+1)]
                              + image[(y+1)*w + (x-1)] + 2*image[(y+1)*w + x] + image[(y+1)*w + (x+1)];
                    double mag = Math.sqrt(gx * gx + gy * gy) / 4.0;
                    edges[y * w + x] = mag > threshold;
                }
            }
            return edges;
        }

        ArrayList<double[]> extractContours(boolean[] edges, int w, int h) {
            ArrayList<double[]> points = new ArrayList<>();
            boolean[] visited = new boolean[w * h];
            for (int y = 1; y < h - 1; y++) {
                for (int x = 1; x < w - 1; x++) {
                    if (edges[y * w + x] && !visited[y * w + x]) {
                        visited[y * w + x] = true;
                        points.add(new double[]{x, y});
                        for (int dy = -1; dy <= 1; dy++) {
                            for (int dx = -1; dx <= 1; dx++) {
                                int nx = x + dx, ny = y + dy;
                                if (nx >= 0 && nx < w && ny >= 0 && ny < h && edges[ny * w + nx] && !visited[ny * w + nx]) {
                                    visited[ny * w + nx] = true;
                                    points.add(new double[]{nx, ny});
                                }
                            }
                        }
                    }
                }
            }
            return points;
        }

        double[] polyfit(double[] x, double[] y, int deg) {
            int n = x.length;
            int m = deg + 1;
            double[][] A = new double[n][m];
            double[] b = new double[n];
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < m; j++) {
                    A[i][j] = Math.pow(x[i], deg - j);
                }
                b[i] = y[i];
            }
            // Normal equations: (A^T A) x = A^T b
            double[][] AtA = new double[m][m];
            double[] Atb = new double[m];
            for (int i = 0; i < m; i++) {
                for (int j = 0; j < m; j++) {
                    double sum = 0;
                    for (int k = 0; k < n; k++) sum += A[k][i] * A[k][j];
                    AtA[i][j] = sum;
                }
                double sum = 0;
                for (int k = 0; k < n; k++) sum += A[k][i] * b[k];
                Atb[i] = sum;
            }
            // Gaussian elimination
            for (int i = 0; i < m; i++) {
                int maxRow = i;
                for (int k = i + 1; k < m; k++) {
                    if (Math.abs(AtA[k][i]) > Math.abs(AtA[maxRow][i])) maxRow = k;
                }
                double[] tmp = AtA[i]; AtA[i] = AtA[maxRow]; AtA[maxRow] = tmp;
                double t = Atb[i]; Atb[i] = Atb[maxRow]; Atb[maxRow] = t;
                if (Math.abs(AtA[i][i]) < 1e-12) continue;
                for (int k = i + 1; k < m; k++) {
                    double factor = AtA[k][i] / AtA[i][i];
                    for (int j = i; j < m; j++) AtA[k][j] -= factor * AtA[i][j];
                    Atb[k] -= factor * Atb[i];
                }
            }
            double[] coeffs = new double[m];
            for (int i = m - 1; i >= 0; i--) {
                coeffs[i] = Atb[i];
                for (int j = i + 1; j < m; j++) coeffs[i] -= AtA[i][j] * coeffs[j];
                if (Math.abs(AtA[i][i]) > 1e-12) coeffs[i] /= AtA[i][i];
            }
            return coeffs;
        }

        double polyval(double[] c, double t) {
            double result = 0;
            for (int i = 0; i < c.length; i++) {
                result += c[i] * Math.pow(t, c.length - 1 - i);
            }
            return result;
        }

        PolyFrame encodeFrame(double[] image, int w, int h) {
            PolyFrame frame = new PolyFrame();
            frame.width = w;
            frame.height = h;
            boolean[] edges = detectEdges(image, w, h, 0.3);
            ArrayList<double[]> contours = extractContours(edges, w, h);
            if (contours.size() < 4) return frame;
            int step = Math.max(1, contours.size() / 50);
            ArrayList<double[]> sampled = new ArrayList<>();
            for (int i = 0; i < contours.size(); i += step) sampled.add(contours.get(i));
            if (sampled.size() < 4) return frame;
            double[] tx = new double[sampled.size()];
            double[] ty = new double[sampled.size()];
            double[] px = new double[sampled.size()];
            double[] py = new double[sampled.size()];
            for (int i = 0; i < sampled.size(); i++) {
                tx[i] = (double) i / (sampled.size() - 1);
                px[i] = sampled.get(i)[0] / w * 2.0 - 1.0;
                py[i] = sampled.get(i)[1] / h * 2.0 - 1.0;
            }
            int deg = Math.min(degree, sampled.size() - 1);
            double[] xc = polyfit(tx, px, deg);
            double[] yc = polyfit(tx, py, deg);
            PolyObject obj = new PolyObject("polyline", "#c8a040");
            obj.xCoeff = xc;
            obj.yCoeff = yc;
            frame.objects.add(obj);
            return frame;
        }

        PolyFrame encodeDelta(PolyFrame prev, PolyFrame curr) {
            PolyFrame delta = new PolyFrame();
            delta.type = "delta";
            delta.width = curr.width;
            delta.height = curr.height;
            delta.deltaFrom = prev.index;
            delta.added.addAll(curr.objects);
            for (PolyObject p : prev.objects) {
                boolean found = false;
                for (PolyObject c : curr.objects) {
                    if (p.id != null && p.id.equals(c.id)) { found = true; break; }
                }
                if (!found) delta.removed.add(p.id);
            }
            return delta;
        }
    }

    // ============================================================
    //  DECODER
    // ============================================================

    static class PolyVideoDecoder {

        void renderPolyline(double[] image, int w, int h, PolyObject obj) {
            if (obj.xCoeff == null || obj.yCoeff == null) return;
            int steps = 200;
            int prevX = -1, prevY = -1;
            for (int i = 0; i <= steps; i++) {
                double t = (double) i / steps;
                double x = 0, y = 0;
                for (int j = 0; j < obj.xCoeff.length; j++) {
                    x += obj.xCoeff[j] * Math.pow(t, obj.xCoeff.length - 1 - j);
                    y += obj.yCoeff[j] * Math.pow(t, obj.yCoeff.length - 1 - j);
                }
                int px = (int) ((x + 1) / 2 * w);
                int py = (int) ((y + 1) / 2 * h);
                px = Math.max(0, Math.min(w - 1, px));
                py = Math.max(0, Math.min(h - 1, py));
                if (prevX >= 0 && prevX < w && prevY >= 0 && prevY < h) {
                    drawLine(image, w, h, prevX, prevY, px, py);
                }
                prevX = px;
                prevY = py;
            }
        }

        void drawLine(double[] image, int w, int h, int x0, int y0, int x1, int y1) {
            int dx = Math.abs(x1 - x0), dy = Math.abs(y1 - y0);
            int sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1;
            int err = dx - dy;
            int maxIter = 1000;
            while (maxIter-- > 0) {
                if (x0 >= 0 && x0 < w && y0 >= 0 && y0 < h) {
                    image[y0 * w + x0] = 1.0;
                }
                if (x0 == x1 && y0 == y1) break;
                int e2 = 2 * err;
                if (e2 > -dy) { err -= dy; x0 += sx; }
                if (e2 < dx) { err += dx; y0 += sy; }
            }
        }

        double[] decodeFrame(PolyFrame frame, int w, int h) {
            double[] image = new double[w * h];
            for (PolyObject obj : frame.objects) {
                if ("polyline".equals(obj.kind)) {
                    renderPolyline(image, w, h, obj);
                }
            }
            return image;
        }

        PolyFrame reconstructDelta(PolyFrame keyframe, PolyFrame delta) {
            PolyFrame result = new PolyFrame();
            result.index = delta.index;
            result.type = "keyframe";
            result.width = keyframe.width;
            result.height = keyframe.height;
            result.background = keyframe.background;
            result.objects.addAll(keyframe.objects);
            for (PolyObject add : delta.added) result.objects.add(add);
            result.objects.removeIf(obj -> delta.removed.contains(obj.id));
            return result;
        }
    }

    // ============================================================
    //  CODEC
    // ============================================================

    int degree = 6;
    int quantBits = 8;
    int keyframeInterval = 10;

    PolyVideo compress(double[][] frames, int w, int h, int fps) {
        PolyVideoEncoder encoder = new PolyVideoEncoder(degree, quantBits);
        PolyVideo video = new PolyVideo();
        video.width = w;
        video.height = h;
        video.fps = fps;
        video.totalFrames = frames.length;
        video.keyframeInterval = keyframeInterval;
        video.polynomialDegree = degree;
        video.quantBits = quantBits;

        PolyFrame lastKeyframe = null;
        for (int i = 0; i < frames.length; i++) {
            PolyFrame frame = encoder.encodeFrame(frames[i], w, h);
            frame.index = i;
            if (i % keyframeInterval == 0 || lastKeyframe == null) {
                frame.type = "keyframe";
                lastKeyframe = frame;
            } else {
                frame = encoder.encodeDelta(lastKeyframe, frame);
            }
            video.frames.add(frame);
        }
        return video;
    }

    double[][] decompress(PolyVideo video) {
        PolyVideoDecoder decoder = new PolyVideoDecoder();
        double[][] frames = new double[video.totalFrames][];
        PolyFrame currentFrame = null;
        for (int i = 0; i < video.frames.size(); i++) {
            PolyFrame f = video.frames.get(i);
            if ("keyframe".equals(f.type)) {
                currentFrame = f;
            } else if (currentFrame != null) {
                currentFrame = decoder.reconstructDelta(currentFrame, f);
            }
            if (currentFrame != null) {
                frames[i] = decoder.decodeFrame(currentFrame, video.width, video.height);
            } else {
                frames[i] = new double[video.width * video.height];
            }
        }
        return frames;
    }

    void printStats(PolyVideo video) {
        int keyframes = 0, deltaFrames = 0;
        int totalObjects = 0;
        for (PolyFrame f : video.frames) {
            if ("keyframe".equals(f.type)) keyframes++;
            else deltaFrames++;
            totalObjects += f.objects.size() + f.added.size();
        }
        System.out.println("[STATS] Format: " + video.format);
        System.out.println("[STATS] Resolution: " + video.width + "x" + video.height);
        System.out.println("[STATS] Total frames: " + video.totalFrames);
        System.out.println("[STATS] Keyframes: " + keyframes);
        System.out.println("[STATS] Delta frames: " + deltaFrames);
        System.out.println("[STATS] Polynomial degree: " + video.polynomialDegree);
        System.out.println("[STATS] Total objects: " + totalObjects);
    }

    // ============================================================
    //  JSON SERIALIZATION (manual)
    // ============================================================

    String toJson(PolyVideo video) {
        StringBuilder sb = new StringBuilder();
        sb.append("{\n");
        sb.append("  \"format\": \"" + video.format + "\",\n");
        sb.append("  \"width\": " + video.width + ",\n");
        sb.append("  \"height\": " + video.height + ",\n");
        sb.append("  \"fps\": " + video.fps + ",\n");
        sb.append("  \"total_frames\": " + video.totalFrames + ",\n");
        sb.append("  \"keyframe_interval\": " + video.keyframeInterval + ",\n");
        sb.append("  \"polynomial_degree\": " + video.polynomialDegree + ",\n");
        sb.append("  \"quant_bits\": " + video.quantBits + ",\n");
        sb.append("  \"frames\": [\n");
        for (int i = 0; i < video.frames.size(); i++) {
            PolyFrame f = video.frames.get(i);
            sb.append("    {\n");
            sb.append("      \"index\": " + f.index + ",\n");
            sb.append("      \"type\": \"" + f.type + "\",\n");
            sb.append("      \"width\": " + f.width + ",\n");
            sb.append("      \"height\": " + f.height + ",\n");
            sb.append("      \"objects\": [");
            for (int j = 0; j < f.objects.size(); j++) {
                if (j > 0) sb.append(",");
                PolyObject o = f.objects.get(j);
                sb.append("\n        {\"id\":\"" + o.id + "\",\"kind\":\"" + o.kind + "\",");
                if (o.xCoeff != null) {
                    sb.append("\"x_coeff\":[");
                    for (int k = 0; k < o.xCoeff.length; k++) {
                        if (k > 0) sb.append(",");
                        sb.append(String.format("%.6f", o.xCoeff[k]));
                    }
                    sb.append("],\"y_coeff\":[");
                    for (int k = 0; k < o.yCoeff.length; k++) {
                        if (k > 0) sb.append(",");
                        sb.append(String.format("%.6f", o.yCoeff[k]));
                    }
                    sb.append("]");
                }
                sb.append(",\"style\":{\"color\":\"" + o.color + "\",\"linewidth\":" + o.linewidth + ",\"alpha\":" + o.alpha + "}}");
            }
            sb.append("\n      ]\n");
            sb.append("    }");
            if (i < video.frames.size() - 1) sb.append(",");
            sb.append("\n");
        }
        sb.append("  ]\n}\n");
        return sb.toString();
    }

    // ============================================================
    //  DEMO
    // ============================================================

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  POLYART VIDEO CODEC - Java Implementation");
        System.out.println("============================================================");

        int w = 320, h = 240, nFrames = 10, fps = 24;
        PolyArtCodec codec = new PolyArtCodec();
        codec.degree = 6;

        // Generate test frames
        System.out.println("\n[1] Generating " + nFrames + " test frames...");
        double[][] frames = new double[nFrames][w * h];
        for (int i = 0; i < nFrames; i++) {
            double[] frame = frames[i];
            // Moving circle
            double cx = 80 + i * 16;
            double cy = 120;
            double radius = 30;
            for (int y = 0; y < h; y++) {
                for (int x = 0; x < w; x++) {
                    double dx = x - cx, dy = y - cy;
                    if (dx * dx + dy * dy < radius * radius) {
                        frame[y * w + x] = 0.8;
                    }
                }
            }
            // Rotating line
            double angle = i * 2 * Math.PI / nFrames;
            int x1 = w / 2, y1 = h / 2;
            int x2 = (int) (x1 + 80 * Math.cos(angle));
            int y2 = (int) (y1 + 80 * Math.sin(angle));
            // Draw line on frame
            int dx = Math.abs(x2 - x1), dy = Math.abs(y2 - y1);
            int sx = x1 < x2 ? 1 : -1, sy = y1 < y2 ? 1 : -1;
            int err = dx - dy;
            int cx2 = x1, cy2 = y1;
            for (int iter = 0; iter < 200; iter++) {
                if (cx2 >= 0 && cx2 < w && cy2 >= 0 && cy2 < h) {
                    frame[cy2 * w + cx2] = 1.0;
                }
                if (cx2 == x2 && cy2 == y2) break;
                int e2 = 2 * err;
                if (e2 > -dy) { err -= dy; cx2 += sx; }
                if (e2 < dx) { err += dx; cy2 += sy; }
            }
        }

        // Encode
        System.out.println("[2] Encoding to polyvid...");
        PolyVideo video = codec.compress(frames, w, h, fps);
        System.out.println("[ENCODE] Done: " + video.frames.size() + " frames");

        // Stats
        System.out.println("\n[3] Compression stats:");
        codec.printStats(video);

        // Decode
        System.out.println("\n[4] Decoding polyvid...");
        double[][] decoded = codec.decompress(video);
        System.out.println("[DECODE] Done: " + decoded.length + " frames");

        // Save JSON
        try {
            String json = codec.toJson(video);
            PrintWriter pw = new PrintWriter(new File("demo.polyvid"));
            pw.print(json);
            pw.close();
            System.out.println("\n[5] Saved demo.polyvid (" + json.length() + " bytes)");
        } catch (Exception e) {
            System.out.println("[ERROR] " + e.getMessage());
        }

        System.out.println("\n[DONE] Java codec demo complete.");
    }
}
