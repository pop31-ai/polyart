#pragma once

#define _USE_MATH_DEFINES
#include <vector>
#include <string>
#include <map>
#include <fstream>
#include <sstream>
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <iostream>
#include <iomanip>

struct PolyObject {
    std::string id;
    std::string kind; // "polyline", "circle", "polygon"
    std::vector<double> xCoeff; // polynomial coefficients for x
    std::vector<double> yCoeff; // polynomial coefficients for y
    double tMin = 0.0;
    double tMax = 1.0;
    // For circle
    double cx = 0, cy = 0, r = 0;
    // Style
    std::string color = "#c8a040";
    double linewidth = 1.0;
    double alpha = 0.8;
};

struct PolyFrame {
    int index = 0;
    std::string type = "keyframe"; // "keyframe" or "delta"
    int width = 640, height = 480;
    std::string background = "#0d0a1a";
    std::vector<PolyObject> objects;
    int deltaFrom = -1;
    std::vector<PolyObject> added;
    std::vector<std::string> removed;
    std::vector<PolyObject> modified;
};

struct PolyVideo {
    std::string format = "polyvid/1.0";
    int width = 640, height = 480;
    int fps = 24;
    int totalFrames = 0;
    int keyframeInterval = 10;
    int polynomialDegree = 6;
    int quantBits = 8;
    std::vector<PolyFrame> frames;
};

// ─────────────────────────── helpers ───────────────────────────

namespace polyart_internal {

inline std::string toLower(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(),
                   [](unsigned char c){ return std::tolower(c); });
    return s;
}

inline std::string trim(const std::string& s) {
    size_t a = s.find_first_not_of(" \t\r\n");
    if (a == std::string::npos) return "";
    size_t b = s.find_last_not_of(" \t\r\n");
    return s.substr(a, b - a + 1);
}

inline std::string escapeStr(const std::string& s) {
    std::string out;
    out.reserve(s.size() + 8);
    for (char c : s) {
        switch (c) {
            case '\\': out += "\\\\"; break;
            case '"':  out += "\\\""; break;
            case '\n': out += "\\n";  break;
            case '\t': out += "\\t";  break;
            default:   out += c;      break;
        }
    }
    return out;
}

inline std::string unescapeStr(const std::string& s) {
    std::string out;
    out.reserve(s.size());
    for (size_t i = 0; i < s.size(); ++i) {
        if (s[i] == '\\' && i + 1 < s.size()) {
            switch (s[i + 1]) {
                case '\\': out += '\\'; i++; break;
                case '"':  out += '"';  i++; break;
                case 'n':  out += '\n'; i++; break;
                case 't':  out += '\t'; i++; break;
                default:   out += s[i];       break;
            }
        } else {
            out += s[i];
        }
    }
    return out;
}

// colour parsing helpers
inline uint32_t hexToUint(const std::string& hex) {
    std::string h = hex;
    if (!h.empty() && h[0] == '#') h = h.substr(1);
    if (h.size() == 3) {
        h = std::string(1, h[0]) + h[0] + h[1] + h[1] + h[2] + h[2];
    }
    return static_cast<uint32_t>(std::stoul(h, nullptr, 16));
}

inline std::string uintToHex(uint32_t v, int digits = 6) {
    std::ostringstream os;
    os << "#" << std::hex << std::setfill('0') << std::setw(digits) << v;
    return os.str();
}

inline double clamp01(double v) { return v < 0.0 ? 0.0 : (v > 1.0 ? 1.0 : v); }

inline double lerp(double a, double b, double t) { return a + (b - a) * t; }

} // namespace polyart_internal

// ═══════════════════════════════════════════════════════════════
//  Encoder
// ═══════════════════════════════════════════════════════════════

class PolyVideoEncoder {
public:
    int degree = 6;

    // ── Edge detection (Sobel) ──────────────────────────────────
    std::vector<bool> detectEdges(const std::vector<double>& image,
                                  int w, int h, double threshold)
    {
        std::vector<bool> edges(w * h, false);
        // Sobel kernels
        const int gx[3][3] = {{-1,0,1},{-2,0,2},{-1,0,1}};
        const int gy[3][3] = {{-1,-2,-1},{0,0,0},{1,2,1}};

        for (int y = 1; y < h - 1; ++y) {
            for (int x = 1; x < w - 1; ++x) {
                double sx = 0, sy = 0;
                for (int ky = -1; ky <= 1; ++ky) {
                    for (int kx = -1; kx <= 1; ++kx) {
                        double v = image[(y + ky) * w + (x + kx)];
                        sx += v * gx[ky + 1][kx + 1];
                        sy += v * gy[ky + 1][kx + 1];
                    }
                }
                double mag = std::sqrt(sx * sx + sy * sy);
                if (mag > threshold)
                    edges[y * w + x] = true;
            }
        }
        return edges;
    }

    // ── Contour extraction (simple chain-code walk) ─────────────
    std::vector<std::pair<double,double>>
    extractContours(const std::vector<bool>& edges, int w, int h)
    {
        std::vector<std::pair<double,double>> pts;
        std::vector<bool> visited(w * h, false);

        const int dx8[8] = { 1, 1, 0,-1,-1,-1, 0, 1};
        const int dy8[8] = { 0, 1, 1, 1, 0,-1,-1,-1};

        for (int y = 1; y < h - 1; ++y) {
            for (int x = 1; x < w - 1; ++x) {
                if (!edges[y * w + x] || visited[y * w + x]) continue;
                // BFS along the contour
                int cx = x, cy = y;
                while (true) {
                    visited[cy * w + cx] = true;
                    pts.emplace_back(static_cast<double>(cx),
                                     static_cast<double>(cy));
                    bool found = false;
                    for (int d = 0; d < 8; ++d) {
                        int nx = cx + dx8[d], ny = cy + dy8[d];
                        if (nx >= 0 && nx < w && ny >= 0 && ny < h &&
                            edges[ny * w + nx] && !visited[ny * w + nx])
                        {
                            cx = nx; cy = ny;
                            found = true;
                            break;
                        }
                    }
                    if (!found) break;
                }
            }
        }
        return pts;
    }

    // ── Polynomial fitting (least squares) ──────────────────────
    std::vector<double> polyfit(const std::vector<double>& x,
                                const std::vector<double>& y,
                                int degree)
    {
        int n = static_cast<int>(x.size());
        int m = degree + 1;
        if (n == 0) return std::vector<double>(m, 0.0);
        if (n < m) m = n;

        // Build Vandermonde-style normal equations: (A^T A) c = A^T y
        std::vector<std::vector<double>> ata(m, std::vector<double>(m, 0.0));
        std::vector<double> aty(m, 0.0);

        for (int i = 0; i < n; ++i) {
            double xi = 1.0;
            for (int p = 0; p < m; ++p) {
                double xj = 1.0;
                for (int q = 0; q < m; ++q) {
                    ata[p][q] += xi * xj;
                    xj *= x[i];
                }
                aty[p] += xi * y[i];
                xi *= x[i];
            }
        }

        // Solve via Gaussian elimination with partial pivoting
        std::vector<std::vector<double>> aug(m, std::vector<double>(m + 1, 0.0));
        for (int i = 0; i < m; ++i) {
            for (int j = 0; j < m; ++j) aug[i][j] = ata[i][j];
            aug[i][m] = aty[i];
        }
        for (int col = 0; col < m; ++col) {
            int best = col;
            double bestVal = std::abs(aug[col][col]);
            for (int row = col + 1; row < m; ++row) {
                double v = std::abs(aug[row][col]);
                if (v > bestVal) { bestVal = v; best = row; }
            }
            std::swap(aug[col], aug[best]);
            double pivot = aug[col][col];
            if (std::abs(pivot) < 1e-15) {
                // Singular – skip
                continue;
            }
            for (int j = col; j <= m; ++j) aug[col][j] /= pivot;
            for (int row = 0; row < m; ++row) {
                if (row == col) continue;
                double factor = aug[row][col];
                for (int j = col; j <= m; ++j)
                    aug[row][j] -= factor * aug[col][j];
            }
        }
        std::vector<double> coeffs(m, 0.0);
        for (int i = 0; i < m; ++i) coeffs[i] = aug[i][m];
        return coeffs;
    }

    // ── Polynomial evaluation ───────────────────────────────────
    double polyval(const std::vector<double>& coeffs, double t) {
        double result = 0.0;
        double tp = 1.0;
        for (double c : coeffs) {
            result += c * tp;
            tp *= t;
        }
        return result;
    }

    // ── Quantize coefficients ───────────────────────────────────
    std::vector<int> quantize(const std::vector<double>& coeffs, int bits) {
        if (coeffs.empty()) return {};
        double maxAbs = 0.0;
        for (double c : coeffs) maxAbs = std::max(maxAbs, std::abs(c));
        if (maxAbs < 1e-15) return std::vector<int>(coeffs.size(), 0);

        int levels = (1 << bits) - 1;
        std::vector<int> out(coeffs.size());
        for (size_t i = 0; i < coeffs.size(); ++i) {
            double norm = (coeffs[i] + maxAbs) / (2.0 * maxAbs);
            out[i] = static_cast<int>(std::round(norm * levels));
        }
        return out;
    }

    // ── Foreground mask ─────────────────────────────────────────
    std::vector<bool> computeForegroundMask(const std::vector<double>& image,
                                            int w, int h, double threshold)
    {
        // Sample background from corners
        double bgR = (image[0] + image[(w - 1) * 3] +
                      image[(h - 1) * w * 3] + image[((h - 1) * w + w - 1) * 3]) / 4.0;
        double bgG = (image[1] + image[(w - 1) * 3 + 1] +
                      image[(h - 1) * w * 3 + 1] + image[((h - 1) * w + w - 1) * 3 + 1]) / 4.0;
        double bgB = (image[2] + image[(w - 1) * 3 + 2] +
                      image[(h - 1) * w * 3 + 2] + image[((h - 1) * w + w - 1) * 3 + 2]) / 4.0;

        std::vector<bool> mask(w * h, false);
        for (int y = 0; y < h; ++y) {
            for (int x = 0; x < w; ++x) {
                const double* p = &image[(y * w + x) * 3];
                double dr = p[0] - bgR, dg = p[1] - bgG, db = p[2] - bgB;
                double dist = std::sqrt(dr * dr + dg * dg + db * db);
                if (dist > threshold)
                    mask[y * w + x] = true;
            }
        }
        return mask;
    }

    // ── Connected components (flood fill) ───────────────────────
    std::vector<int> labelComponents(const std::vector<bool>& mask,
                                    int w, int h)
    {
        std::vector<int> labels(w * h, -1);
        int nextLabel = 0;
        std::vector<int> stack;
        const int dx4[4] = {1, -1, 0, 0};
        const int dy4[4] = {0, 0, 1, -1};

        for (int y = 0; y < h; ++y) {
            for (int x = 0; x < w; ++x) {
                if (!mask[y * w + x] || labels[y * w + x] >= 0) continue;
                stack.clear();
                stack.push_back(y * w + x);
                labels[y * w + x] = nextLabel;
                while (!stack.empty()) {
                    int idx = stack.back(); stack.pop_back();
                    int cx = idx % w, cy = idx / w;
                    for (int d = 0; d < 4; ++d) {
                        int nx = cx + dx4[d], ny = cy + dy4[d];
                        if (nx >= 0 && nx < w && ny >= 0 && ny < h &&
                            mask[ny * w + nx] && labels[ny * w + nx] < 0)
                        {
                            labels[ny * w + nx] = nextLabel;
                            stack.push_back(ny * w + nx);
                        }
                    }
                }
                ++nextLabel;
            }
        }
        return labels;
    }

    // ── Extract boundary of a labeled component ─────────────────
    std::vector<std::pair<double,double>>
    extractBoundary(const std::vector<int>& labels, int label,
                    int w, int h)
    {
        std::vector<std::pair<double,double>> boundary;
        const int dx4[4] = {1, -1, 0, 0};
        const int dy4[4] = {0, 0, 1, -1};

        for (int y = 0; y < h; ++y) {
            for (int x = 0; x < w; ++x) {
                if (labels[y * w + x] != label) continue;
                // Is it on the boundary? (at least one 4-neighbour is different)
                bool isBdy = false;
                for (int d = 0; d < 4; ++d) {
                    int nx = x + dx4[d], ny = y + dy4[d];
                    if (nx < 0 || nx >= w || ny < 0 || ny >= h ||
                        labels[ny * w + nx] != label)
                    {
                        isBdy = true;
                        break;
                    }
                }
                if (isBdy)
                    boundary.emplace_back(static_cast<double>(x),
                                          static_cast<double>(y));
            }
        }
        return boundary;
    }

    // ── Sort boundary points by angle from centroid ─────────────
    void sortBoundaryByAngle(std::vector<std::pair<double,double>>& pts)
    {
        if (pts.size() < 3) return;
        double cx = 0, cy = 0;
        for (auto& p : pts) { cx += p.first; cy += p.second; }
        cx /= pts.size(); cy /= pts.size();
        std::sort(pts.begin(), pts.end(),
            [cx, cy](const std::pair<double,double>& a,
                     const std::pair<double,double>& b) {
                double aa = std::atan2(a.second - cy, a.first - cx);
                double ab = std::atan2(b.second - cy, b.first - cx);
                return aa < ab;
            });
    }

    // ── Detect if component is circular ─────────────────────────
    bool isCircular(const std::vector<std::pair<double,double>>& boundary,
                    double& outCx, double& outCy, double& outR)
    {
        if (boundary.size() < 8) return false;
        // Compute centroid and radius consistency
        double cx = 0, cy = 0;
        for (auto& p : boundary) { cx += p.first; cy += p.second; }
        cx /= boundary.size(); cy /= boundary.size();

        double rSum = 0;
        for (auto& p : boundary) {
            double dx = p.first - cx, dy = p.second - cy;
            rSum += std::sqrt(dx * dx + dy * dy);
        }
        double meanR = rSum / boundary.size();

        // Compute coefficient of variation of radius
        double varSum = 0;
        for (auto& p : boundary) {
            double dx = p.first - cx, dy = p.second - cy;
            double r = std::sqrt(dx * dx + dy * dy);
            varSum += (r - meanR) * (r - meanR);
        }
        double stddev = std::sqrt(varSum / boundary.size());
        double cv = (meanR > 1e-6) ? stddev / meanR : 999.0;

        // Also check aspect ratio
        double minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9;
        for (auto& p : boundary) {
            minX = std::min(minX, p.first); maxX = std::max(maxX, p.first);
            minY = std::min(minY, p.second); maxY = std::max(maxY, p.second);
        }
        double spanX = maxX - minX + 1, spanY = maxY - minY + 1;
        double aspect = std::min(spanX, spanY) / std::max(spanX, spanY);

        outCx = cx; outCy = cy; outR = meanR;
        return (cv < 0.35 && aspect > 0.5);
    }

    // ── Compute average colour of component pixels ──────────────
    std::string averageColour(const std::vector<double>& image,
                              const std::vector<int>& labels, int label,
                              int w)
    {
        double r = 0, g = 0, b = 0;
        int count = 0;
        for (size_t i = 0; i < labels.size(); ++i) {
            if (labels[i] != label) continue;
            r += image[i * 3 + 0];
            g += image[i * 3 + 1];
            b += image[i * 3 + 2];
            ++count;
        }
        if (count == 0) return "#ffffff";
        r /= count; g /= count; b /= count;
        uint32_t hex = (static_cast<uint32_t>(r * 255) << 16) |
                       (static_cast<uint32_t>(g * 255) << 8) |
                        static_cast<uint32_t>(b * 255);
        return polyart_internal::uintToHex(hex);
    }

    // ── Encode frame ────────────────────────────────────────────
    PolyFrame encodeFrame(const std::vector<double>& image,
                          int w, int h)
    {
        PolyFrame frame;
        frame.width = w;
        frame.height = h;
        frame.type = "keyframe";

        // Compute foreground mask
        auto mask = computeForegroundMask(image, w, h, 0.08);

        // Connected components
        auto labels = labelComponents(mask, w, h);

        // Find how many components
        int numLabels = 0;
        for (int l : labels) numLabels = std::max(numLabels, l + 1);

        int objIdx = 0;
        for (int lab = 0; lab < numLabels; ++lab) {
            auto boundary = extractBoundary(labels, lab, w, h);
            if (boundary.size() < 6) continue;

            std::string col = averageColour(image, labels, lab, w);

            double cx, cy, r;
            if (isCircular(boundary, cx, cy, r) && r > 5.0) {
                // ── Circle ──────────────────────────────────────
                PolyObject obj;
                obj.id = "obj_" + std::to_string(objIdx++);
                obj.kind = "circle";
                obj.cx = cx; obj.cy = cy; obj.r = r;
                obj.color = col;
                obj.linewidth = 1.5;
                obj.alpha = 0.85;
                frame.objects.push_back(std::move(obj));
            } else {
                // ── Polyline (sort boundary by angle, fit poly) ─
                sortBoundaryByAngle(boundary);

                // Downsample
                int targetPts = std::min(100, static_cast<int>(boundary.size()));
                std::vector<std::pair<double,double>> sampled;
                double step = static_cast<double>(boundary.size()) / targetPts;
                for (int i = 0; i < targetPts; ++i)
                    sampled.push_back(boundary[static_cast<int>(i * step)]);

                int n = static_cast<int>(sampled.size());
                std::vector<double> tArr(n), xArr(n), yArr(n);
                for (int i = 0; i < n; ++i) {
                    tArr[i] = static_cast<double>(i) / std::max(1, n - 1);
                    xArr[i] = sampled[i].first;
                    yArr[i] = sampled[i].second;
                }

                int deg = std::min(degree, n - 1);
                if (deg < 2) deg = 2;

                PolyObject obj;
                obj.id = "obj_" + std::to_string(objIdx++);
                obj.kind = "polyline";
                obj.xCoeff = polyfit(tArr, xArr, deg);
                obj.yCoeff = polyfit(tArr, yArr, deg);
                obj.tMin = 0.0;
                obj.tMax = 1.0;
                obj.color = col;
                obj.linewidth = 1.0;
                obj.alpha = 0.8;
                frame.objects.push_back(std::move(obj));
            }
        }

        return frame;
    }

    // ── Encode delta ────────────────────────────────────────────
    PolyFrame encodeDelta(const PolyFrame& prev, const PolyFrame& curr) {
        PolyFrame delta = curr;
        delta.type = "delta";
        delta.deltaFrom = prev.index;
        delta.objects.clear();
        delta.added.clear();
        delta.removed.clear();
        delta.modified.clear();

        // Build lookup of previous object ids
        std::map<std::string, const PolyObject*> prevMap;
        for (auto& o : prev.objects) prevMap[o.id] = &o;

        std::map<std::string, bool> seen;
        for (auto& obj : curr.objects) {
            auto it = prevMap.find(obj.id);
            if (it == prevMap.end()) {
                delta.added.push_back(obj);
            } else {
                const PolyObject* po = it->second;
                bool changed = (obj.kind != po->kind ||
                                obj.xCoeff != po->xCoeff ||
                                obj.yCoeff != po->yCoeff ||
                                obj.cx != po->cx || obj.cy != po->cy ||
                                obj.r != po->r ||
                                obj.color != po->color ||
                                obj.linewidth != po->linewidth ||
                                obj.alpha != po->alpha);
                if (changed) delta.modified.push_back(obj);
                seen[obj.id] = true;
            }
        }
        for (auto& [id, ptr] : prevMap) {
            if (seen.find(id) == seen.end())
                delta.removed.push_back(id);
        }

        // Keep a minimal representation in delta.objects
        delta.objects = delta.added;
        for (auto& m : delta.modified) delta.objects.push_back(m);

        return delta;
    }
};

// ═══════════════════════════════════════════════════════════════
//  Decoder
// ═══════════════════════════════════════════════════════════════

class PolyVideoDecoder {
public:
    PolyVideoEncoder enc;

    double polyval(const std::vector<double>& c, double t) {
        return enc.polyval(c, t);
    }

    // ── Render polyline (Bresenham-ish with polynomial) ─────────
    void renderPolyline(std::vector<double>& image, int w, int h,
                        const PolyObject& obj)
    {
        // Parse colour
        uint32_t rgb = polyart_internal::hexToUint(obj.color);
        double cr = ((rgb >> 16) & 0xFF) / 255.0;
        double cg = ((rgb >>  8) & 0xFF) / 255.0;
        double cb = ((rgb      ) & 0xFF) / 255.0;
        double a = polyart_internal::clamp01(obj.alpha);

        int steps = std::max(200, (w + h) * 2);
        double prevPx = -1, prevPy = -1;

        for (int i = 0; i <= steps; ++i) {
            double t = obj.tMin + (obj.tMax - obj.tMin) * i / steps;
            double px = polyval(obj.xCoeff, t);
            double py = polyval(obj.yCoeff, t);

            // Draw line from (prevPx,prevPy) to (px,py)
            if (prevPx >= 0) {
                double dist = std::sqrt((px - prevPx) * (px - prevPx) +
                                        (py - prevPy) * (py - prevPy));
                int segSteps = std::max(1, static_cast<int>(dist * 2));
                for (int s = 0; s <= segSteps; ++s) {
                    double frac = static_cast<double>(s) / segSteps;
                    double lx = polyart_internal::lerp(prevPx, px, frac);
                    double ly = polyart_internal::lerp(prevPy, py, frac);

                    // Anti-aliased point
                    int ix = static_cast<int>(std::round(lx));
                    int iy = static_cast<int>(std::round(ly));
                    int radius = std::max(1, static_cast<int>(std::round(obj.linewidth * 0.5)));

                    for (int dy = -radius; dy <= radius; ++dy) {
                        for (int dx = -radius; dx <= radius; ++dx) {
                            int sx = ix + dx, sy = iy + dy;
                            if (sx < 0 || sx >= w || sy < 0 || sy >= h) continue;
                            double d = std::sqrt(dx * dx + dy * dy);
                            double w2 = polyart_internal::clamp01(1.0 - d / (radius + 0.5));
                            double blend = a * w2;
                            double* p = &image[(sy * w + sx) * 3];
                            p[0] = polyart_internal::lerp(p[0], cr, blend);
                            p[1] = polyart_internal::lerp(p[1], cg, blend);
                            p[2] = polyart_internal::lerp(p[2], cb, blend);
                        }
                    }
                }
            }
            prevPx = px; prevPy = py;
        }
    }

    // ── Render circle ───────────────────────────────────────────
    void renderCircle(std::vector<double>& image, int w, int h,
                      const PolyObject& obj)
    {
        uint32_t rgb = polyart_internal::hexToUint(obj.color);
        double cr = ((rgb >> 16) & 0xFF) / 255.0;
        double cg = ((rgb >>  8) & 0xFF) / 255.0;
        double cb = ((rgb      ) & 0xFF) / 255.0;
        double a = polyart_internal::clamp01(obj.alpha);

        int r = static_cast<int>(std::round(obj.r));
        int lw = std::max(1, static_cast<int>(std::round(obj.linewidth)));

        for (int dy = -r - lw; dy <= r + lw; ++dy) {
            for (int dx = -r - lw; dx <= r + lw; ++dx) {
                int sx = static_cast<int>(std::round(obj.cx)) + dx;
                int sy = static_cast<int>(std::round(obj.cy)) + dy;
                if (sx < 0 || sx >= w || sy < 0 || sy >= h) continue;

                double dist = std::sqrt(dx * dx + dy * dy);
                double diff = std::abs(dist - obj.r);
                double w2 = polyart_internal::clamp01(1.0 - diff / (lw * 0.5 + 0.5));
                double blend = a * w2;
                if (blend < 1e-6) continue;

                double* p = &image[(sy * w + sx) * 3];
                p[0] = polyart_internal::lerp(p[0], cr, blend);
                p[1] = polyart_internal::lerp(p[1], cg, blend);
                p[2] = polyart_internal::lerp(p[2], cb, blend);
            }
        }
    }

    // ── Decode frame ────────────────────────────────────────────
    std::vector<double> decodeFrame(const PolyFrame& frame, int w, int h) {
        // Parse background
        uint32_t bgHex = polyart_internal::hexToUint(frame.background);
        double br = ((bgHex >> 16) & 0xFF) / 255.0;
        double bg = ((bgHex >>  8) & 0xFF) / 255.0;
        double bb = ((bgHex      ) & 0xFF) / 255.0;

        std::vector<double> image(w * h * 3);
        for (int i = 0; i < w * h; ++i) {
            image[i * 3 + 0] = br;
            image[i * 3 + 1] = bg;
            image[i * 3 + 2] = bb;
        }

        for (auto& obj : frame.objects) {
            if (obj.kind == "circle") {
                renderCircle(image, w, h, obj);
            } else {
                renderPolyline(image, w, h, obj);
            }
        }
        return image;
    }

    // ── Reconstruct delta ───────────────────────────────────────
    PolyFrame reconstructDelta(const PolyFrame& keyframe,
                               const PolyFrame& delta)
    {
        PolyFrame result = keyframe;
        result.index = delta.index;

        std::map<std::string, size_t> objIndex;
        for (size_t i = 0; i < result.objects.size(); ++i)
            objIndex[result.objects[i].id] = i;

        // Remove
        for (auto& id : delta.removed) {
            auto it = objIndex.find(id);
            if (it != objIndex.end()) {
                result.objects.erase(result.objects.begin() + it->second);
            }
        }

        // Modified / added
        for (auto& obj : delta.objects) {
            auto it = objIndex.find(obj.id);
            if (it != objIndex.end()) {
                result.objects[it->second] = obj;
            } else {
                result.objects.push_back(obj);
            }
        }

        return result;
    }

    // ── Interpolate ─────────────────────────────────────────────
    PolyFrame interpolateFrame(const PolyFrame& f1,
                               const PolyFrame& f2, double t)
    {
        PolyFrame out = f1;
        out.index = static_cast<int>(std::round(
            polyart_internal::lerp(f1.index, f2.index, t)));

        // Build map from f2
        std::map<std::string, const PolyObject*> map2;
        for (auto& o : f2.objects) map2[o.id] = &o;

        for (auto& obj : out.objects) {
            auto it = map2.find(obj.id);
            if (it == map2.end()) continue;
            const PolyObject& o2 = *it->second;

            // Interpolate polynomial coeffs
            size_t mc = std::max(obj.xCoeff.size(), o2.xCoeff.size());
            obj.xCoeff.resize(mc, 0.0);
            obj.yCoeff.resize(mc, 0.0);

            std::vector<double> xc2(mc, 0.0), yc2(mc, 0.0);
            for (size_t i = 0; i < o2.xCoeff.size(); ++i) xc2[i] = o2.xCoeff[i];
            for (size_t i = 0; i < o2.yCoeff.size(); ++i) yc2[i] = o2.yCoeff[i];

            for (size_t i = 0; i < mc; ++i) {
                obj.xCoeff[i] = polyart_internal::lerp(obj.xCoeff[i], xc2[i], t);
                obj.yCoeff[i] = polyart_internal::lerp(obj.yCoeff[i], yc2[i], t);
            }

            obj.cx = polyart_internal::lerp(obj.cx, o2.cx, t);
            obj.cy = polyart_internal::lerp(obj.cy, o2.cy, t);
            obj.r  = polyart_internal::lerp(obj.r,  o2.r,  t);
        }
        return out;
    }
};

// ═══════════════════════════════════════════════════════════════
//  Codec  (compress / decompress / serialise)
// ═══════════════════════════════════════════════════════════════

class PolyVideoCodec {
public:
    int degree = 6;
    int quantBits = 8;
    int keyframeInterval = 10;

    PolyVideoEncoder   encoder;
    PolyVideoDecoder   decoder;

    // ── compress ────────────────────────────────────────────────
    PolyVideo compress(const std::vector<std::vector<double>>& frames,
                       int w, int h, int fps)
    {
        PolyVideo vid;
        vid.width = w;
        vid.height = h;
        vid.fps = fps;
        vid.totalFrames = static_cast<int>(frames.size());
        vid.keyframeInterval = keyframeInterval;
        vid.polynomialDegree = degree;
        vid.quantBits = quantBits;

        encoder.degree = degree;

        PolyFrame prevKF;
        bool hasPrev = false;

        for (int i = 0; i < static_cast<int>(frames.size()); ++i) {
            PolyFrame frame = encoder.encodeFrame(frames[i], w, h);
            frame.index = i;
            frame.width = w;
            frame.height = h;

            if (i % keyframeInterval == 0) {
                // Keyframe
                frame.type = "keyframe";
                frame.deltaFrom = -1;
                prevKF = frame;
                hasPrev = true;
            } else if (hasPrev) {
                // Delta
                frame = encoder.encodeDelta(prevKF, frame);
                frame.index = i;
                frame.width = w;
                frame.height = h;
            } else {
                frame.type = "keyframe";
                prevKF = frame;
                hasPrev = true;
            }

            vid.frames.push_back(std::move(frame));
        }
        return vid;
    }

    // ── decompress ──────────────────────────────────────────────
    std::vector<std::vector<double>>
    decompress(const PolyVideo& video)
    {
        std::vector<std::vector<double>> frames;
        frames.reserve(video.totalFrames);

        PolyFrame currentKF;
        bool hasKF = false;

        for (auto& f : video.frames) {
            if (f.type == "keyframe") {
                currentKF = f;
                hasKF = true;
            } else if (hasKF) {
                currentKF = decoder.reconstructDelta(currentKF, f);
            }

            auto img = decoder.decodeFrame(currentKF, video.width, video.height);
            frames.push_back(std::move(img));
        }
        return frames;
    }

    // ── serialise helpers ───────────────────────────────────────
    static void writeStr(std::ostream& os, const std::string& s) {
        os << '"' << polyart_internal::escapeStr(s) << '"';
    }

    static void writeInt(std::ostream& os, int v) { os << v; }

    static void writeDouble(std::ostream& os, double v) {
        if (std::abs(v) < 1e-12) { os << "0"; return; }
        os << std::setprecision(10) << v;
    }

    static void writeCoeffs(std::ostream& os,
                            const std::vector<double>& c) {
        os << "[";
        for (size_t i = 0; i < c.size(); ++i) {
            if (i) os << ",";
            writeDouble(os, c[i]);
        }
        os << "]";
    }

    static void writeObject(std::ostream& os, const PolyObject& o,
                            bool indent) {
        std::string pad = indent ? "    " : "";
        std::string pad2 = indent ? "        " : "";
        os << pad << "{\n";
        os << pad2 << "\"id\": ";        writeStr(os, o.id);      os << ",\n";
        os << pad2 << "\"kind\": ";      writeStr(os, o.kind);    os << ",\n";
        os << pad2 << "\"xCoeff\": ";    writeCoeffs(os, o.xCoeff); os << ",\n";
        os << pad2 << "\"yCoeff\": ";    writeCoeffs(os, o.yCoeff); os << ",\n";
        os << pad2 << "\"tMin\": ";      writeDouble(os, o.tMin);  os << ",\n";
        os << pad2 << "\"tMax\": ";      writeDouble(os, o.tMax);  os << ",\n";
        os << pad2 << "\"cx\": ";        writeDouble(os, o.cx);    os << ",\n";
        os << pad2 << "\"cy\": ";        writeDouble(os, o.cy);    os << ",\n";
        os << pad2 << "\"r\": ";         writeDouble(os, o.r);     os << ",\n";
        os << pad2 << "\"color\": ";     writeStr(os, o.color);    os << ",\n";
        os << pad2 << "\"linewidth\": "; writeDouble(os, o.linewidth); os << ",\n";
        os << pad2 << "\"alpha\": ";     writeDouble(os, o.alpha); os << "\n";
        os << pad << "}";
    }

    static void writeFrame(std::ostream& os, const PolyFrame& f,
                           bool last) {
        std::string p1 = "    ";
        std::string p2 = "        ";
        os << "    {\n";
        os << p2 << "\"index\": ";       writeInt(os, f.index);    os << ",\n";
        os << p2 << "\"type\": ";        writeStr(os, f.type);     os << ",\n";
        os << p2 << "\"width\": ";       writeInt(os, f.width);    os << ",\n";
        os << p2 << "\"height\": ";      writeInt(os, f.height);   os << ",\n";
        os << p2 << "\"background\": ";  writeStr(os, f.background); os << ",\n";

        os << p2 << "\"objects\": [\n";
        for (size_t i = 0; i < f.objects.size(); ++i) {
            writeObject(os, f.objects[i], true);
            if (i + 1 < f.objects.size()) os << ",";
            os << "\n";
        }
        os << p2 << "],\n";

        os << p2 << "\"deltaFrom\": " << f.deltaFrom << ",\n";

        os << p2 << "\"added\": [\n";
        for (size_t i = 0; i < f.added.size(); ++i) {
            writeObject(os, f.added[i], true);
            if (i + 1 < f.added.size()) os << ",";
            os << "\n";
        }
        os << p2 << "],\n";

        os << p2 << "\"removed\": [";
        for (size_t i = 0; i < f.removed.size(); ++i) {
            if (i) os << ",";
            writeStr(os, f.removed[i]);
        }
        os << "],\n";

        os << p2 << "\"modified\": [\n";
        for (size_t i = 0; i < f.modified.size(); ++i) {
            writeObject(os, f.modified[i], true);
            if (i + 1 < f.modified.size()) os << ",";
            os << "\n";
        }
        os << p2 << "]\n";

        os << "    }";
        if (!last) os << ",";
        os << "\n";
    }

    // ── save ────────────────────────────────────────────────────
    void save(const PolyVideo& video, const std::string& path) {
        std::ofstream os(path);
        if (!os.is_open()) {
            std::cerr << "Cannot open " << path << " for writing\n";
            return;
        }
        os << "{\n";
        os << "  \"format\": ";       writeStr(os, video.format);   os << ",\n";
        os << "  \"width\": ";        writeInt(os, video.width);    os << ",\n";
        os << "  \"height\": ";       writeInt(os, video.height);   os << ",\n";
        os << "  \"fps\": ";          writeInt(os, video.fps);      os << ",\n";
        os << "  \"totalFrames\": ";  writeInt(os, video.totalFrames); os << ",\n";
        os << "  \"keyframeInterval\": "; writeInt(os, video.keyframeInterval); os << ",\n";
        os << "  \"polynomialDegree\": "; writeInt(os, video.polynomialDegree); os << ",\n";
        os << "  \"quantBits\": ";    writeInt(os, video.quantBits); os << ",\n";
        os << "  \"frames\": [\n";
        for (size_t i = 0; i < video.frames.size(); ++i) {
            writeFrame(os, video.frames[i], i + 1 == video.frames.size());
        }
        os << "  ]\n";
        os << "}\n";
    }

    // ── minimal JSON parser ─────────────────────────────────────
    static std::string readToken(const std::string& json, size_t& pos) {
        while (pos < json.size() && std::isspace(static_cast<unsigned char>(json[pos])))
            ++pos;
        if (pos >= json.size()) return "";
        char c = json[pos];

        // string
        if (c == '"') {
            ++pos;
            std::string s;
            while (pos < json.size() && json[pos] != '"') {
                if (json[pos] == '\\') { s += json[pos]; ++pos; }
                s += json[pos]; ++pos;
            }
            if (pos < json.size()) ++pos;
            return polyart_internal::unescapeStr(s);
        }
        // number
        if (c == '-' || c == '.' || (c >= '0' && c <= '9')) {
            size_t start = pos;
            while (pos < json.size() && (json[pos] == '-' || json[pos] == '+' ||
                   json[pos] == '.' || json[pos] == 'e' || json[pos] == 'E' ||
                   (json[pos] >= '0' && json[pos] <= '9')))
                ++pos;
            return json.substr(start, pos - start);
        }
        // punctuation
        std::string tok(1, c);
        ++pos;
        return tok;
    }

    static double readNumber(const std::string& json, size_t& pos) {
        std::string tok = readToken(json, pos);
        return std::stod(tok);
    }

    static std::vector<double> readCoeffArray(const std::string& json,
                                              size_t& pos) {
        std::vector<double> v;
        std::string tok = readToken(json, pos); // consume '['
        while (pos < json.size()) {
            tok = readToken(json, pos);
            if (tok == "]" || tok.empty()) break;
            if (tok == ",") continue;
            v.push_back(std::stod(tok));
        }
        return v;
    }

    static std::vector<std::string> readStringArray(const std::string& json,
                                                     size_t& pos) {
        std::vector<std::string> v;
        std::string tok = readToken(json, pos); // consume '['
        while (pos < json.size()) {
            tok = readToken(json, pos);
            if (tok == "]" || tok.empty()) break;
            if (tok == ",") continue;
            v.push_back(tok);
        }
        return v;
    }

    // ── load ────────────────────────────────────────────────────
    PolyVideo load(const std::string& path) {
        PolyVideo vid;
        std::ifstream ifs(path);
        if (!ifs.is_open()) {
            std::cerr << "Cannot open " << path << "\n";
            return vid;
        }
        std::string json((std::istreambuf_iterator<char>(ifs)),
                          std::istreambuf_iterator<char>());

        size_t pos = 0;
        auto readKey = [&]() -> std::string {
            std::string k = readToken(json, pos);
            readToken(json, pos); // colon
            return k;
        };

        while (pos < json.size()) {
            std::string tok = readToken(json, pos);
            if (tok == "}" || tok.empty()) break;
            if (tok == "," || tok == "{" || tok == "[") continue;

            // tok is a key; next token is the colon — skip it
            // (the value is then read inline below)

            if (tok == "format")        { readToken(json, pos); vid.format = readToken(json, pos); }
            else if (tok == "width")        { readToken(json, pos); vid.width = static_cast<int>(readNumber(json, pos)); }
            else if (tok == "height")       { readToken(json, pos); vid.height = static_cast<int>(readNumber(json, pos)); }
            else if (tok == "fps")          { readToken(json, pos); vid.fps = static_cast<int>(readNumber(json, pos)); }
            else if (tok == "totalFrames")  { readToken(json, pos); vid.totalFrames = static_cast<int>(readNumber(json, pos)); }
            else if (tok == "keyframeInterval") { readToken(json, pos); vid.keyframeInterval = static_cast<int>(readNumber(json, pos)); }
            else if (tok == "polynomialDegree") { readToken(json, pos); vid.polynomialDegree = static_cast<int>(readNumber(json, pos)); }
            else if (tok == "quantBits")    { readToken(json, pos); vid.quantBits = static_cast<int>(readNumber(json, pos)); }
            else if (tok == "frames") {
                readToken(json, pos); // colon
                readToken(json, pos); // [
                while (pos < json.size()) {
                    std::string ftok = readToken(json, pos);
                    if (ftok == "]" || ftok.empty()) break;
                    if (ftok == ",") continue;

                    PolyFrame frame;
                    // Parse frame object
                    while (pos < json.size()) {
                        std::string key = readToken(json, pos);
                        if (key == "}" || key.empty()) break;
                        if (key == ",") continue;
                        readToken(json, pos); // colon

                        if (key == "index") {
                            frame.index = static_cast<int>(readNumber(json, pos));
                        } else if (key == "type") {
                            frame.type = readToken(json, pos);
                        } else if (key == "width") {
                            frame.width = static_cast<int>(readNumber(json, pos));
                        } else if (key == "height") {
                            frame.height = static_cast<int>(readNumber(json, pos));
                        } else if (key == "background") {
                            frame.background = readToken(json, pos);
                        } else if (key == "deltaFrom") {
                            frame.deltaFrom = static_cast<int>(readNumber(json, pos));
                        } else if (key == "objects") {
                            readToken(json, pos); // [
                            while (pos < json.size()) {
                                std::string otok = readToken(json, pos);
                                if (otok == "]" || otok.empty()) break;
                                if (otok == ",") continue;
                                PolyObject obj;
                                while (pos < json.size()) {
                                    std::string ok = readToken(json, pos);
                                    if (ok == "}" || ok.empty()) break;
                                    if (ok == ",") continue;
                                    readToken(json, pos); // colon
                                    if (ok == "id")          obj.id = readToken(json, pos);
                                    else if (ok == "kind")       obj.kind = readToken(json, pos);
                                    else if (ok == "xCoeff")     obj.xCoeff = readCoeffArray(json, pos);
                                    else if (ok == "yCoeff")     obj.yCoeff = readCoeffArray(json, pos);
                                    else if (ok == "tMin")       obj.tMin = readNumber(json, pos);
                                    else if (ok == "tMax")       obj.tMax = readNumber(json, pos);
                                    else if (ok == "cx")         obj.cx = readNumber(json, pos);
                                    else if (ok == "cy")         obj.cy = readNumber(json, pos);
                                    else if (ok == "r")          obj.r = readNumber(json, pos);
                                    else if (ok == "color")      obj.color = readToken(json, pos);
                                    else if (ok == "linewidth")  obj.linewidth = readNumber(json, pos);
                                    else if (ok == "alpha")      obj.alpha = readNumber(json, pos);
                                    else { /* skip unknown */ readToken(json, pos); }
                                }
                                frame.objects.push_back(std::move(obj));
                            }
                        } else if (key == "added") {
                            readToken(json, pos); // [
                            while (pos < json.size()) {
                                std::string otok = readToken(json, pos);
                                if (otok == "]" || otok.empty()) break;
                                if (otok == ",") continue;
                                PolyObject obj;
                                while (pos < json.size()) {
                                    std::string ok = readToken(json, pos);
                                    if (ok == "}" || ok.empty()) break;
                                    if (ok == ",") continue;
                                    readToken(json, pos);
                                    if (ok == "id")          obj.id = readToken(json, pos);
                                    else if (ok == "kind")       obj.kind = readToken(json, pos);
                                    else if (ok == "xCoeff")     obj.xCoeff = readCoeffArray(json, pos);
                                    else if (ok == "yCoeff")     obj.yCoeff = readCoeffArray(json, pos);
                                    else if (ok == "tMin")       obj.tMin = readNumber(json, pos);
                                    else if (ok == "tMax")       obj.tMax = readNumber(json, pos);
                                    else if (ok == "cx")         obj.cx = readNumber(json, pos);
                                    else if (ok == "cy")         obj.cy = readNumber(json, pos);
                                    else if (ok == "r")          obj.r = readNumber(json, pos);
                                    else if (ok == "color")      obj.color = readToken(json, pos);
                                    else if (ok == "linewidth")  obj.linewidth = readNumber(json, pos);
                                    else if (ok == "alpha")      obj.alpha = readNumber(json, pos);
                                    else { readToken(json, pos); }
                                }
                                frame.added.push_back(std::move(obj));
                            }
                        } else if (key == "removed") {
                            frame.removed = readStringArray(json, pos);
                        } else if (key == "modified") {
                            readToken(json, pos); // [
                            while (pos < json.size()) {
                                std::string otok = readToken(json, pos);
                                if (otok == "]" || otok.empty()) break;
                                if (otok == ",") continue;
                                PolyObject obj;
                                while (pos < json.size()) {
                                    std::string ok = readToken(json, pos);
                                    if (ok == "}" || ok.empty()) break;
                                    if (ok == ",") continue;
                                    readToken(json, pos);
                                    if (ok == "id")          obj.id = readToken(json, pos);
                                    else if (ok == "kind")       obj.kind = readToken(json, pos);
                                    else if (ok == "xCoeff")     obj.xCoeff = readCoeffArray(json, pos);
                                    else if (ok == "yCoeff")     obj.yCoeff = readCoeffArray(json, pos);
                                    else if (ok == "tMin")       obj.tMin = readNumber(json, pos);
                                    else if (ok == "tMax")       obj.tMax = readNumber(json, pos);
                                    else if (ok == "cx")         obj.cx = readNumber(json, pos);
                                    else if (ok == "cy")         obj.cy = readNumber(json, pos);
                                    else if (ok == "r")          obj.r = readNumber(json, pos);
                                    else if (ok == "color")      obj.color = readToken(json, pos);
                                    else if (ok == "linewidth")  obj.linewidth = readNumber(json, pos);
                                    else if (ok == "alpha")      obj.alpha = readNumber(json, pos);
                                    else { readToken(json, pos); }
                                }
                                frame.modified.push_back(std::move(obj));
                            }
                        } else {
                            // skip unknown key's value
                            readToken(json, pos);
                        }
                    }
                    vid.frames.push_back(std::move(frame));
                }
            } else {
                readToken(json, pos); // colon
                readToken(json, pos); // skip unknown value
            }
        }
        return vid;
    }

    // ── stats ───────────────────────────────────────────────────
    void printStats(const PolyVideo& video) {
        std::cout << "===== PolyArt Video Stats =====\n";
        std::cout << "Format:        " << video.format << "\n";
        std::cout << "Resolution:    " << video.width << "x" << video.height << "\n";
        std::cout << "FPS:           " << video.fps << "\n";
        std::cout << "Total frames:  " << video.totalFrames << "\n";
        std::cout << "Key interval:  " << video.keyframeInterval << "\n";
        std::cout << "Poly degree:   " << video.polynomialDegree << "\n";
        std::cout << "Quant bits:    " << video.quantBits << "\n";
        std::cout << "\n";

        int keyframes = 0, deltas = 0;
        int totalObjs = 0, totalAdded = 0, totalRemoved = 0, totalModified = 0;
        size_t totalCoeffs = 0;

        for (auto& f : video.frames) {
            if (f.type == "keyframe") ++keyframes; else ++deltas;
            totalObjs += static_cast<int>(f.objects.size());
            totalAdded += static_cast<int>(f.added.size());
            totalRemoved += static_cast<int>(f.removed.size());
            totalModified += static_cast<int>(f.modified.size());
            for (auto& o : f.objects)
                totalCoeffs += o.xCoeff.size() + o.yCoeff.size();
        }

        std::cout << "Keyframes:     " << keyframes << "\n";
        std::cout << "Deltas:        " << deltas << "\n";
        std::cout << "Total objects: " << totalObjs << "\n";
        std::cout << "  added:       " << totalAdded << "\n";
        std::cout << "  removed:     " << totalRemoved << "\n";
        std::cout << "  modified:    " << totalModified << "\n";
        std::cout << "Total coeffs:  " << totalCoeffs << "\n";

        // Rough size estimate (bytes) — each coefficient ~ 6 chars in text
        size_t estBytes = totalCoeffs * 6 + totalObjs * 80;
        std::cout << "Est. text size: ~" << estBytes << " bytes\n";

        // Compare to raw pixels
        size_t rawBytes = static_cast<size_t>(video.totalFrames) *
                          video.width * video.height * 3;
        double ratio = rawBytes > 0
            ? static_cast<double>(estBytes) / rawBytes * 100.0
            : 0.0;
        std::cout << "Raw pixel data: " << rawBytes << " bytes\n";
        std::cout << "Compression:    ~" << std::fixed << std::setprecision(2)
                  << ratio << "%\n";
        std::cout << "================================\n";
    }
};
