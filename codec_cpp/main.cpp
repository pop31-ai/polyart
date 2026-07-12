#define _USE_MATH_DEFINES
#include "polyart_codec.h"
#include <cmath>
#include <iostream>
#include <vector>

// Generate a test frame: moving circle + rotating line on dark background
static std::vector<double> makeFrame(int frameIndex, int w, int h,
                                     int totalFrames)
{
    std::vector<double> img(w * h * 3);

    // Dark background  #0d0a1a
    for (int i = 0; i < w * h; ++i) {
        img[i * 3 + 0] = 0x0d / 255.0;
        img[i * 3 + 1] = 0x0a / 255.0;
        img[i * 3 + 2] = 0x1a / 255.0;
    }

    double t = static_cast<double>(frameIndex) / std::max(1, totalFrames - 1);

    // ── Moving circle ────────────────────────────────────────
    double circX = 160 + 120 * std::cos(2.0 * M_PI * t);
    double circY = h / 2.0 + 80 * std::sin(2.0 * M_PI * t);
    double circR = 30 + 10 * std::sin(4.0 * M_PI * t);

    uint32_t cHex = 0x40c0a0; // teal-ish
    double cr = ((cHex >> 16) & 0xFF) / 255.0;
    double cg = ((cHex >>  8) & 0xFF) / 255.0;
    double cb = ((cHex      ) & 0xFF) / 255.0;
    double ca = 0.75;

    int ri = static_cast<int>(std::round(circR));
    for (int dy = -ri - 2; dy <= ri + 2; ++dy) {
        for (int dx = -ri - 2; dx <= ri + 2; ++dx) {
            int sx = static_cast<int>(std::round(circX)) + dx;
            int sy = static_cast<int>(std::round(circY)) + dy;
            if (sx < 0 || sx >= w || sy < 0 || sy >= h) continue;
            double dist = std::sqrt(dx * dx + dy * dy);
            double diff = std::abs(dist - circR);
            double blend = ca * polyart_internal::clamp01(1.0 - diff / 2.0);
            double* p = &img[(sy * w + sx) * 3];
            p[0] = polyart_internal::lerp(p[0], cr, blend);
            p[1] = polyart_internal::lerp(p[1], cg, blend);
            p[2] = polyart_internal::lerp(p[2], cb, blend);
        }
    }

    // ── Rotating line ────────────────────────────────────────
    double angle = 2.0 * M_PI * t;
    double cx2 = w * 0.65;
    double cy2 = h * 0.5;
    double len = 100.0;
    double x1 = cx2 + len * std::cos(angle);
    double y1 = cy2 + len * std::sin(angle);
    double x2 = cx2 - len * std::cos(angle);
    double y2 = cy2 - len * std::sin(angle);

    uint32_t lHex = 0xc8a040; // gold
    double lr = ((lHex >> 16) & 0xFF) / 255.0;
    double lg = ((lHex >>  8) & 0xFF) / 255.0;
    double lb = ((lHex      ) & 0xFF) / 255.0;

    int steps = 200;
    for (int i = 0; i <= steps; ++i) {
        double frac = static_cast<double>(i) / steps;
        double lx = polyart_internal::lerp(x1, x2, frac);
        double ly = polyart_internal::lerp(y1, y2, frac);
        int ix = static_cast<int>(std::round(lx));
        int iy = static_cast<int>(std::round(ly));
        for (int dy = -1; dy <= 1; ++dy) {
            for (int dx = -1; dx <= 1; ++dx) {
                int sx = ix + dx, sy = iy + dy;
                if (sx < 0 || sx >= w || sy < 0 || sy >= h) continue;
                double d = std::sqrt(dx * dx + dy * dy);
                double blend = 0.8 * polyart_internal::clamp01(1.0 - d / 1.5);
                double* p = &img[(sy * w + sx) * 3];
                p[0] = polyart_internal::lerp(p[0], lr, blend);
                p[1] = polyart_internal::lerp(p[1], lg, blend);
                p[2] = polyart_internal::lerp(p[2], lb, blend);
            }
        }
    }

    return img;
}

static double computeMSE(const std::vector<double>& a,
                         const std::vector<double>& b)
{
    if (a.size() != b.size()) return -1;
    double sum = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        double d = a[i] - b[i];
        sum += d * d;
    }
    return sum / a.size();
}

int main()
{
    const int W = 320, H = 240, FPS = 24, NFRAMES = 10;

    std::cout << "PolyArt Codec Demo\n"
              << "==================\n\n";

    // 1. Generate test frames
    std::cout << "[1] Generating " << NFRAMES << " test frames ("
              << W << "x" << H << ") ...\n";
    std::vector<std::vector<double>> rawFrames;
    for (int i = 0; i < NFRAMES; ++i)
        rawFrames.push_back(makeFrame(i, W, H, NFRAMES));
    std::cout << "    Done. (" << rawFrames.size() << " frames)\n\n";

    // 2. Compress
    std::cout << "[2] Compressing ...\n";
    PolyVideoCodec codec;
    codec.degree = 6;
    codec.quantBits = 8;
    codec.keyframeInterval = 5;

    PolyVideo video = codec.compress(rawFrames, W, H, FPS);
    std::cout << "    Done.\n\n";

    // 3. Save to file
    std::cout << "[3] Saving to output.polyvid ...\n";
    codec.save(video, "output.polyvid");
    std::cout << "    Done.\n\n";

    // 4. Stats (before decompress)
    std::cout << "[4] Statistics:\n";
    codec.printStats(video);
    std::cout << "\n";

    // 5. Load back
    std::cout << "[5] Loading from output.polyvid ...\n";
    PolyVideo loaded = codec.load("output.polyvid");
    std::cout << "    Loaded " << loaded.frames.size() << " frames.\n\n";

    // 6. Decompress
    std::cout << "[6] Decompressing ...\n";
    std::vector<std::vector<double>> decodedFrames = codec.decompress(loaded);
    std::cout << "    Done. (" << decodedFrames.size() << " frames)\n\n";

    // 7. Compute error
    std::cout << "[7] Frame-by-frame MSE:\n";
    double totalMSE = 0;
    for (int i = 0; i < std::min(static_cast<int>(rawFrames.size()),
                                  static_cast<int>(decodedFrames.size())); ++i)
    {
        double mse = computeMSE(rawFrames[i], decodedFrames[i]);
        totalMSE += mse;
        std::cout << "    Frame " << i << ": MSE = " << std::fixed
                  << std::setprecision(6) << mse << "\n";
    }
    int nFrames = std::min(static_cast<int>(rawFrames.size()),
                           static_cast<int>(decodedFrames.size()));
    if (nFrames > 0) totalMSE /= nFrames;
    std::cout << "    Average MSE: " << totalMSE << "\n\n";

    // 8. Summary
    std::cout << "[8] Summary:\n";
    std::cout << "    Input:  " << NFRAMES << " frames, "
              << W << "x" << H << ", " << FPS << " fps\n";
    std::cout << "    Objects per frame: ";
    int totalObjs = 0;
    for (auto& f : video.frames) totalObjs += static_cast<int>(f.objects.size());
    std::cout << (video.totalFrames > 0 ? totalObjs / video.totalFrames : 0) << "\n";
    std::cout << "    Polynomial degree: " << video.polynomialDegree << "\n";
    std::cout << "    Keyframe interval: " << video.keyframeInterval << "\n";
    std::cout << "    Quantisation bits: " << video.quantBits << "\n";
    std::cout << "\nDone.\n";

    return 0;
}
