"use strict";

const fs = require("fs");
const path = require("path");

// ============================================================
// PolyObject
// ============================================================
class PolyObject {
    constructor(kind, params, style) {
        this.id = null;
        this.kind = kind;       // "polyline", "circle", "polygon", "fill"
        this.params = params;   // {x:[], y:[]} or {cx, cy, r}
        this.style = style;     // {color, linewidth, alpha}
    }

    clone() {
        const o = new PolyObject(
            this.kind,
            JSON.parse(JSON.stringify(this.params)),
            JSON.parse(JSON.stringify(this.style))
        );
        o.id = this.id;
        return o;
    }

    toJSON() {
        return {
            id: this.id,
            kind: this.kind,
            params: this.params,
            style: this.style,
        };
    }

    static fromJSON(data) {
        const o = new PolyObject(data.kind, data.params, data.style);
        o.id = data.id;
        return o;
    }
}

// ============================================================
// PolyFrame
// ============================================================
class PolyFrame {
    constructor(width, height, background) {
        this.width = width || 640;
        this.height = height || 480;
        this.background = background || "#0d0a1a";
        this.objects = [];
        this.deltaFrom = -1;
        this.type = "keyframe"; // or "delta"
        this.added = [];
        this.removed = [];
        this.modified = [];
    }

    addObject(obj) {
        this.objects.push(obj);
    }

    toJSON() {
        return {
            width: this.width,
            height: this.height,
            background: this.background,
            objects: this.objects.map((o) => o.toJSON()),
            deltaFrom: this.deltaFrom,
            type: this.type,
            added: this.added.map((o) => o.toJSON()),
            removed: this.removed.map((o) => o.id),
            modified: this.modified.map((o) => o.toJSON()),
        };
    }

    static fromJSON(data) {
        const f = new PolyFrame(data.width, data.height, data.background);
        f.deltaFrom = data.deltaFrom !== undefined ? data.deltaFrom : -1;
        f.type = data.type || "keyframe";
        f.objects = (data.objects || []).map((o) => PolyObject.fromJSON(o));
        f.added = (data.added || []).map((o) => PolyObject.fromJSON(o));
        f.removed = data.removed || [];
        f.modified = (data.modified || []).map((o) => PolyObject.fromJSON(o));
        return f;
    }
}

// ============================================================
// PolyVideoEncoder
// ============================================================
class PolyVideoEncoder {
    constructor(degree, quantBits) {
        this.degree = degree || 6;
        this.quantBits = quantBits || 8;
        this.nextObjectId = 1;
        this.prevFrameObjects = [];
    }

    // ---------- polynomial helpers ----------

    polyfit(xs, ys, degree) {
        const n = xs.length;
        if (n === 0) return [];
        degree = Math.min(degree, n - 1);
        const m = degree + 1;

        // Build normal equations: (X^T X) c = X^T y
        const XtX = Array.from({ length: m }, () => new Float64Array(m));
        const Xty = new Float64Array(m);

        for (let i = 0; i < n; i++) {
            const x = xs[i];
            const y = ys[i];
            const powX = [];
            for (let p = 0; p < m; p++) powX.push(Math.pow(x, p));
            for (let r = 0; r < m; r++) {
                Xty[r] += powX[r] * y;
                for (let c = 0; c < m; c++) {
                    XtX[r][c] += powX[r] * powX[c];
                }
            }
        }

        // Gaussian elimination with partial pivoting
        const aug = Array.from({ length: m }, (_, i) => {
            const row = new Float64Array(m + 1);
            for (let c = 0; c < m; c++) row[c] = XtX[i][c];
            row[m] = Xty[i];
            return row;
        });

        for (let col = 0; col < m; col++) {
            let maxRow = col;
            let maxVal = Math.abs(aug[col][col]);
            for (let row = col + 1; row < m; row++) {
                if (Math.abs(aug[row][col]) > maxVal) {
                    maxVal = Math.abs(aug[row][col]);
                    maxRow = row;
                }
            }
            [aug[col], aug[maxRow]] = [aug[maxRow], aug[col]];
            const pivot = aug[col][col];
            if (Math.abs(pivot) < 1e-12) continue;
            for (let c = col; c <= m; c++) aug[col][c] /= pivot;
            for (let row = 0; row < m; row++) {
                if (row === col) continue;
                const factor = aug[row][col];
                for (let c = col; c <= m; c++) aug[row][c] -= factor * aug[col][c];
            }
        }

        return aug.map((row) => row[m]);
    }

    polyval(coeffs, t) {
        let result = 0;
        for (let i = 0; i < coeffs.length; i++) {
            result += coeffs[i] * Math.pow(t, i);
        }
        return result;
    }

    quantizeCoeffs(coeffs, bits) {
        if (!coeffs || coeffs.length === 0) return [];
        const maxVal = (1 << (bits - 1)) - 1;
        let maxAbs = 0;
        for (const c of coeffs) if (Math.abs(c) > maxAbs) maxAbs = Math.abs(c);
        if (maxAbs < 1e-12) return coeffs.map(() => 0);
        const scale = maxVal / maxAbs;
        return coeffs.map((c) => Math.round(c * scale));
    }

    dequantizeCoeffs(qcoeffs, bits) {
        if (!qcoeffs || qcoeffs.length === 0) return [];
        // We store raw quantized values; decoding uses the same coefficients directly
        return qcoeffs.map((c) => c);
    }

    // ---------- edge detection ----------

    detectEdges(imageData, width, height, threshold) {
        const gray = new Float64Array(width * height);
        for (let i = 0; i < width * height; i++) {
            const idx = i * 4;
            gray[i] = 0.299 * imageData[idx] + 0.587 * imageData[idx + 1] + 0.114 * imageData[idx + 2];
        }

        const edges = new Uint8Array(width * height);
        const gx = [-1, 0, 1, -2, 0, 2, -1, 0, 1];
        const gy = [-1, -2, -1, 0, 0, 0, 1, 2, 1];
        const th = threshold || 30;

        for (let y = 1; y < height - 1; y++) {
            for (let x = 1; x < width - 1; x++) {
                let sumX = 0, sumY = 0;
                for (let ky = -1; ky <= 1; ky++) {
                    for (let kx = -1; kx <= 1; kx++) {
                        const val = gray[(y + ky) * width + (x + kx)];
                        const ki = (ky + 1) * 3 + (kx + 1);
                        sumX += val * gx[ki];
                        sumY += val * gy[ki];
                    }
                }
                const mag = Math.sqrt(sumX * sumX + sumY * sumY);
                if (mag > th) edges[y * width + x] = 255;
            }
        }
        return edges;
    }

    // ---------- contour extraction ----------

    extractContours(edges, width, height) {
        const visited = new Uint8Array(width * height);
        const contours = [];

        for (let y = 1; y < height - 1; y++) {
            for (let x = 1; x < width - 1; x++) {
                const idx = y * width + x;
                if (edges[idx] === 0 || visited[idx]) continue;
                const contour = [];
                let cx = x, cy = y;
                visited[idx] = 1;
                contour.push({ x: cx, y: cy });

                const dirs = [
                    { dx: 1, dy: 0 }, { dx: 1, dy: 1 }, { dx: 0, dy: 1 }, { dx: -1, dy: 1 },
                    { dx: -1, dy: 0 }, { dx: -1, dy: -1 }, { dx: 0, dy: -1 }, { dx: 1, dy: -1 },
                ];

                let found = true;
                while (found) {
                    found = false;
                    for (const d of dirs) {
                        const nx = cx + d.dx;
                        const ny = cy + d.dy;
                        if (nx < 0 || nx >= width || ny < 0 || ny >= height) continue;
                        const ni = ny * width + nx;
                        if (edges[ni] !== 0 && !visited[ni]) {
                            visited[ni] = 1;
                            cx = nx;
                            cy = ny;
                            contour.push({ x: cx, y: cy });
                            found = true;
                            break;
                        }
                    }
                }
                if (contour.length >= 5) contours.push(contour);
            }
        }
        return contours;
    }

    simplifyContour(points, maxPoints) {
        if (points.length <= maxPoints) return points;
        const step = Math.max(1, Math.floor(points.length / maxPoints));
        const result = [];
        for (let i = 0; i < points.length; i += step) result.push(points[i]);
        if (result[result.length - 1] !== points[points.length - 1]) {
            result.push(points[points.length - 1]);
        }
        return result;
    }

    // ---------- color sampling ----------

    sampleColor(imageData, width, points) {
        let r = 0, g = 0, b = 0, count = 0;
        for (const p of points) {
            const px = Math.round(p.x);
            const py = Math.round(p.y);
            if (px < 0 || px >= width || py < 0) continue;
            const idx = (py * width + px) * 4;
            r += imageData[idx];
            g += imageData[idx + 1];
            b += imageData[idx + 2];
            count++;
        }
        if (count === 0) return "#ffffff";
        r = Math.round(r / count);
        g = Math.round(g / count);
        b = Math.round(b / count);
        return (
            "#" +
            r.toString(16).padStart(2, "0") +
            g.toString(16).padStart(2, "0") +
            b.toString(16).padStart(2, "0")
        );
    }

    // ---------- frame encoding ----------

    encodeFrame(imageData, width, height) {
        const threshold = 30;
        const edges = this.detectEdges(imageData, width, height, threshold);
        const contours = this.extractContours(edges, width, height);

        const frame = new PolyFrame(width, height, "#0d0a1a");
        let contourId = 0;

        for (const contour of contours) {
            const maxPolyPoints = Math.min(contour.length, Math.max(8, this.degree + 2));
            const sampled = this.simplifyContour(contour, maxPolyPoints);

            const xs = sampled.map((p) => p.x);
            const ys = sampled.map((p) => p.y);

            // Normalise t to [0, 1]
            const tVals = xs.map((_, i) => i / (xs.length - 1 || 1));

            const coeffsX = this.polyfit(tVals, xs, this.degree);
            const coeffsY = this.polyfit(tVals, ys, this.degree);

            const qCoeffsX = this.quantizeCoeffs(coeffsX, this.quantBits);
            const qCoeffsY = this.quantizeCoeffs(coeffsY, this.quantBits);

            const color = this.sampleColor(imageData, width, sampled);

            const obj = new PolyObject("polyline", {
                t: tVals,
                x: qCoeffsX,
                y: qCoeffsY,
                degree: this.degree,
            }, {
                color: color,
                linewidth: 2,
                alpha: 1.0,
            });
            obj.id = this.nextObjectId++;
            frame.addObject(obj);
            contourId++;
        }

        return frame;
    }

    encodeDelta(prevFrame, currFrame) {
        const prevIds = new Set(prevFrame.objects.map((o) => o.id));
        const currIds = new Set(currFrame.objects.map((o) => o.id));

        const delta = new PolyFrame(currFrame.width, currFrame.height, currFrame.background);
        delta.type = "delta";
        delta.objects = currFrame.objects.map((o) => o.clone());

        // Objects in current but not in previous -> added
        delta.added = currFrame.objects.filter((o) => !prevIds.has(o.id)).map((o) => o.clone());

        // Objects in previous but not in current -> removed
        delta.removed = prevFrame.objects.filter((o) => !currIds.has(o.id)).map((o) => o.id);

        // Objects in both but different -> modified
        delta.modified = [];
        for (const cObj of currFrame.objects) {
            if (!prevIds.has(cObj.id)) continue;
            const pObj = prevFrame.objects.find((p) => p.id === cObj.id);
            if (pObj && JSON.stringify(pObj.params) !== JSON.stringify(cObj.params)) {
                delta.modified.push(cObj.clone());
            }
        }

        delta.deltaFrom = 0;
        return delta;
    }

    encodeVideo(frames, width, height, fps, keyframeInterval, degree) {
        const ki = keyframeInterval || 10;
        const deg = degree || this.degree;
        const polyFrames = [];

        this.nextObjectId = 1;
        this.prevFrameObjects = [];

        for (let i = 0; i < frames.length; i++) {
            const frameData = frames[i];
            const polyFrame = this.encodeFrame(frameData, width, height);

            if (i % ki === 0) {
                polyFrame.type = "keyframe";
                polyFrame.deltaFrom = -1;
            } else {
                const lastKeyIdx = Math.floor(i / ki) * ki;
                if (lastKeyIdx < polyFrames.length) {
                    const delta = this.encodeDelta(polyFrames[lastKeyIdx], polyFrame);
                    polyFrames.push(delta);
                    continue;
                }
            }
            polyFrames.push(polyFrame);
        }

        return {
            version: "1.0",
            codec: "polyart",
            width: width,
            height: height,
            fps: fps || 24,
            frameCount: frames.length,
            degree: deg,
            quantBits: this.quantBits,
            frames: polyFrames.map((f) => f.toJSON()),
        };
    }
}

// ============================================================
// PolyVideoDecoder
// ============================================================
class PolyVideoDecoder {
    constructor() {}

    renderPolyObject(obj) {
        const commands = [];
        const kind = obj.kind;
        const params = obj.params;
        const style = obj.style;

        if (kind === "polyline" || kind === "polygon") {
            const numSamples = 40;
            const points = [];
            for (let i = 0; i <= numSamples; i++) {
                const t = i / numSamples;
                const x = this.evalPolyCoeffs(params.x, t, params.degree);
                const y = this.evalPolyCoeffs(params.y, t, params.degree);
                points.push({ x: Math.round(x), y: Math.round(y) });
            }
            commands.push({
                op: kind,
                points: points,
                color: style.color,
                linewidth: style.linewidth || 2,
                alpha: style.alpha !== undefined ? style.alpha : 1.0,
            });
        } else if (kind === "circle") {
            commands.push({
                op: "circle",
                cx: params.cx,
                cy: params.cy,
                r: params.r,
                color: style.color,
                linewidth: style.linewidth || 2,
                alpha: style.alpha !== undefined ? style.alpha : 1.0,
            });
        } else if (kind === "fill") {
            commands.push({
                op: "fill",
                points: params.points || [],
                color: style.color,
                alpha: style.alpha !== undefined ? style.alpha : 1.0,
            });
        }

        return commands;
    }

    evalPolyCoeffs(coeffs, t, degree) {
        let result = 0;
        const deg = degree || (coeffs.length - 1);
        for (let i = 0; i < coeffs.length; i++) {
            result += coeffs[i] * Math.pow(t, i);
        }
        return result;
    }

    decodeFrame(polyFrameData) {
        const frame = PolyFrame.fromJSON(polyFrameData);
        const renderCommands = {
            width: frame.width,
            height: frame.height,
            background: frame.background,
            objects: [],
            drawCommands: [],
        };

        for (const obj of frame.objects) {
            renderCommands.objects.push(obj);
            const cmds = this.renderPolyObject(obj);
            renderCommands.drawCommands.push(...cmds);
        }

        return renderCommands;
    }

    decodeDeltaFrame(keyframeData, deltaFrameData) {
        const keyFrame = PolyFrame.fromJSON(keyframeData);
        const deltaFrame = PolyFrame.fromJSON(deltaFrameData);

        const objectMap = new Map();
        for (const obj of keyFrame.objects) {
            objectMap.set(obj.id, obj.clone());
        }

        for (const obj of deltaFrame.added) {
            objectMap.set(obj.id, obj);
        }
        for (const rid of deltaFrame.removed) {
            objectMap.delete(rid);
        }
        for (const obj of deltaFrame.modified) {
            objectMap.set(obj.id, obj);
        }

        const merged = new PolyFrame(deltaFrame.width, deltaFrame.height, deltaFrame.background);
        merged.type = "keyframe";
        for (const obj of objectMap.values()) {
            merged.addObject(obj);
        }

        return this.decodeFrame(merged.toJSON());
    }

    decodeVideo(polyvid) {
        const decoded = [];
        let lastKeyframe = null;

        for (let i = 0; i < polyvid.frames.length; i++) {
            const fData = polyvid.frames[i];
            if (fData.type === "keyframe") {
                const rendered = this.decodeFrame(fData);
                decoded.push(rendered);
                lastKeyframe = fData;
            } else {
                const rendered = this.decodeDeltaFrame(lastKeyframe, fData);
                decoded.push(rendered);
            }
        }

        return decoded;
    }

    interpolateFrame(frame1Data, frame2Data, t) {
        const f1 = PolyFrame.fromJSON(frame1Data);
        const f2 = PolyFrame.fromJSON(frame2Data);

        const interp = new PolyFrame(f1.width, f1.height, f1.background);

        const maxLen = Math.max(f1.objects.length, f2.objects.length);
        for (let i = 0; i < maxLen; i++) {
            const o1 = f1.objects[i];
            const o2 = f2.objects[i];
            if (!o1 && o2) { interp.addObject(o2.clone()); continue; }
            if (o1 && !o2) { interp.addObject(o1.clone()); continue; }
            if (!o1 || !o2) continue;

            const kind = o1.kind;
            const style = {
                color: o1.style.color,
                linewidth: o1.style.linewidth,
                alpha: o1.style.alpha,
            };

            if (kind === "polyline" || kind === "polygon") {
                const params = {};
                params.degree = o1.degree || o2.degree || 6;
                const len1 = (o1.params.x || []).length;
                const len2 = (o2.params.x || []).length;
                const maxC = Math.max(len1, len2);
                params.x = [];
                params.y = [];
                params.t = [];
                for (let c = 0; c < maxC; c++) {
                    const v1x = (o1.params.x || [])[c] || 0;
                    const v2x = (o2.params.x || [])[c] || 0;
                    const v1y = (o1.params.y || [])[c] || 0;
                    const v2y = (o2.params.y || [])[c] || 0;
                    params.x.push(Math.round(v1x * (1 - t) + v2x * t));
                    params.y.push(Math.round(v1y * (1 - t) + v2y * t));
                    params.t.push(((o1.params.t || [])[c] || c / (maxC - 1 || 1)));
                }
                const obj = new PolyObject(kind, params, style);
                obj.id = o1.id;
                interp.addObject(obj);
            } else {
                interp.addObject(o1.clone());
            }
        }

        return this.decodeFrame(interp.toJSON());
    }
}

// ============================================================
// PolyVideoCodec
// ============================================================
class PolyVideoCodec {
    constructor(options) {
        const opts = options || {};
        this.quality = opts.quality || "medium";
        this.degree = opts.degree || 6;
        this.quantBits = opts.quantBits || 8;
        this.keyframeInterval = opts.keyframeInterval || 10;

        if (this.quality === "low") {
            this.degree = Math.min(this.degree, 4);
            this.quantBits = Math.min(this.quantBits, 6);
        } else if (this.quality === "high") {
            this.degree = Math.max(this.degree, 8);
            this.quantBits = Math.max(this.quantBits, 10);
        }
    }

    compress(inputFrames, width, height, fps) {
        const encoder = new PolyVideoEncoder(this.degree, this.quantBits);
        const polyvid = encoder.encodeVideo(
            inputFrames,
            width,
            height,
            fps,
            this.keyframeInterval,
            this.degree
        );
        return polyvid;
    }

    decompress(polyvid) {
        const decoder = new PolyVideoDecoder();
        return decoder.decodeVideo(polyvid);
    }

    getStats(polyvid) {
        const rawSize = JSON.stringify(polyvid).length;
        let totalObjects = 0;
        let keyframes = 0;
        let deltas = 0;

        for (const f of polyvid.frames) {
            totalObjects += (f.objects || []).length;
            if (f.type === "keyframe") keyframes++;
            else deltas++;
        }

        return {
            format: "polyart-v1",
            width: polyvid.width,
            height: polyvid.height,
            fps: polyvid.fps,
            frameCount: polyvid.frameCount,
            degree: polyvid.degree,
            quantBits: polyvid.quantBits,
            totalObjects: totalObjects,
            keyframes: keyframes,
            deltaFrames: deltas,
            encodedSizeBytes: rawSize,
            estimatedRawSizeBytes: polyvid.width * polyvid.height * 4 * polyvid.frameCount,
            compressionRatio: 0, // will set below
        };
    }

    save(polyvid, filepath) {
        const json = JSON.stringify(polyvid);
        fs.writeFileSync(filepath, json, "utf8");
        return json.length;
    }

    load(filepath) {
        const raw = fs.readFileSync(filepath, "utf8");
        return JSON.parse(raw);
    }
}

// ============================================================
// Helper: generate test frame (RGBA image data)
// ============================================================
function generateTestFrame(width, height, frameIndex, totalFrames) {
    const data = Buffer.alloc(width * height * 4);

    // Dark background
    for (let i = 0; i < width * height; i++) {
        data[i * 4] = 13;
        data[i * 4 + 1] = 10;
        data[i * 4 + 2] = 26;
        data[i * 4 + 3] = 255;
    }

    const t = frameIndex / totalFrames;

    // Circle 1: moving horizontally
    const cx1 = Math.round(width * 0.3 + Math.sin(t * Math.PI * 2) * width * 0.15);
    const cy1 = Math.round(height * 0.4);
    const r1 = 40;
    drawCircleFilled(data, width, height, cx1, cy1, r1, 220, 60, 60);

    // Circle 2: moving vertically
    const cx2 = Math.round(width * 0.6);
    const cy2 = Math.round(height * 0.5 + Math.cos(t * Math.PI * 2) * height * 0.2);
    const r2 = 30;
    drawCircleFilled(data, width, height, cx2, cy2, r2, 60, 180, 120);

    // Rectangle (moving diagonal)
    const rx = Math.round(width * 0.15 + t * width * 0.4);
    const ry = Math.round(height * 0.1 + t * height * 0.3);
    const rw = 60;
    const rh = 40;
    drawRectFilled(data, width, height, rx, ry, rw, rh, 60, 100, 220);

    // Triangle outline
    const tx = Math.round(width * 0.7);
    const ty = Math.round(height * 0.15 + Math.sin(t * Math.PI * 3) * 20);
    drawTriangleOutline(data, width, height, tx, ty, 50, 240, 200, 60);

    // Star / polygon
    const sx = Math.round(width * 0.5 + Math.cos(t * Math.PI * 2) * 30);
    const sy = Math.round(height * 0.8);
    drawPolygonStar(data, width, height, sx, sy, 25, 12, 5, 240, 120, 240);

    return data;
}

function drawCircleFilled(data, w, h, cx, cy, r, cr, cg, cb) {
    for (let y = cy - r; y <= cy + r; y++) {
        for (let x = cx - r; x <= cx + r; x++) {
            if (x < 0 || x >= w || y < 0 || y >= h) continue;
            if ((x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r) {
                const idx = (y * w + x) * 4;
                data[idx] = cr;
                data[idx + 1] = cg;
                data[idx + 2] = cb;
            }
        }
    }
}

function drawRectFilled(data, w, h, rx, ry, rw, rh, cr, cg, cb) {
    for (let y = ry; y < ry + rh; y++) {
        for (let x = rx; x < rx + rw; x++) {
            if (x < 0 || x >= w || y < 0 || y >= h) continue;
            const idx = (y * w + x) * 4;
            data[idx] = cr;
            data[idx + 1] = cg;
            data[idx + 2] = cb;
        }
    }
}

function drawLine(data, w, h, x0, y0, x1, y1, cr, cg, cb) {
    const dx = Math.abs(x1 - x0);
    const dy = Math.abs(y1 - y0);
    const sx = x0 < x1 ? 1 : -1;
    const sy = y0 < y1 ? 1 : -1;
    let err = dx - dy;
    let cx = x0, cy = y0;
    while (true) {
        if (cx >= 0 && cx < w && cy >= 0 && cy < h) {
            const idx = (cy * w + cx) * 4;
            data[idx] = cr;
            data[idx + 1] = cg;
            data[idx + 2] = cb;
        }
        if (cx === x1 && cy === y1) break;
        const e2 = 2 * err;
        if (e2 > -dy) { err -= dy; cx += sx; }
        if (e2 < dx) { err += dx; cy += sy; }
    }
}

function drawTriangleOutline(data, w, h, cx, cy, size, cr, cg, cb) {
    const pts = [];
    for (let i = 0; i < 3; i++) {
        const a = (i * 2 * Math.PI) / 3 - Math.PI / 2;
        pts.push({ x: Math.round(cx + size * Math.cos(a)), y: Math.round(cy + size * Math.sin(a)) });
    }
    drawLine(data, w, h, pts[0].x, pts[0].y, pts[1].x, pts[1].y, cr, cg, cb);
    drawLine(data, w, h, pts[1].x, pts[1].y, pts[2].x, pts[2].y, cr, cg, cb);
    drawLine(data, w, h, pts[2].x, pts[2].y, pts[0].x, pts[0].y, cr, cg, cb);
}

function drawPolygonStar(data, w, h, cx, cy, outerR, innerR, points, cr, cg, cb) {
    const pts = [];
    for (let i = 0; i < points * 2; i++) {
        const a = (i * Math.PI) / points - Math.PI / 2;
        const r = i % 2 === 0 ? outerR : innerR;
        pts.push({ x: Math.round(cx + r * Math.cos(a)), y: Math.round(cy + r * Math.sin(a)) });
    }
    for (let i = 0; i < pts.length; i++) {
        const next = (i + 1) % pts.length;
        drawLine(data, w, h, pts[i].x, pts[i].y, pts[next].x, pts[next].y, cr, cg, cb);
    }
}

// ============================================================
// Demo
// ============================================================
function main() {
    const width = 320;
    const height = 240;
    const fps = 10;
    const numFrames = 10;

    console.log("=== PolyArt Video Codec (Node.js) ===");
    console.log("Generating " + numFrames + " test frames (" + width + "x" + height + ")...");

    const frames = [];
    for (let i = 0; i < numFrames; i++) {
        frames.push(generateTestFrame(width, height, i, numFrames));
    }

    console.log("Encoding frames...");

    const codec = new PolyVideoCodec({
        quality: "medium",
        degree: 6,
        quantBits: 8,
        keyframeInterval: 5,
    });

    const polyvid = codec.compress(frames, width, height, fps);

    const filepath = path.join(__dirname, "demo.polyvid");
    const size = codec.save(polyvid, filepath);
    console.log("Saved: " + filepath);
    console.log("File size: " + size + " bytes");

    const stats = codec.getStats(polyvid);
    const ratio = stats.estimatedRawSizeBytes / (stats.encodedSizeBytes || 1);
    stats.compressionRatio = Math.round(ratio * 100) / 100;

    console.log("");
    console.log("--- Compression Stats ---");
    console.log("Format:          " + stats.format);
    console.log("Resolution:      " + stats.width + "x" + stats.height);
    console.log("FPS:             " + stats.fps);
    console.log("Frame count:     " + stats.frameCount);
    console.log("Polynomial deg:  " + stats.degree);
    console.log("Quant bits:      " + stats.quantBits);
    console.log("Total objects:   " + stats.totalObjects);
    console.log("Keyframes:       " + stats.keyframes);
    console.log("Delta frames:    " + stats.deltaFrames);
    console.log("Encoded size:    " + stats.encodedSizeBytes + " bytes");
    console.log("Raw size:        " + stats.estimatedRawSizeBytes + " bytes");
    console.log("Compression:     " + stats.compressionRatio + "x");

    console.log("");
    console.log("Decoding...");

    const decoded = codec.decompress(polyvid);
    console.log("Decoded " + decoded.length + " frames.");

    console.log("");
    console.log("--- Interpolation Demo ---");
    if (decoded.length >= 2) {
        const interp = new PolyVideoDecoder().interpolateFrame(
            polyvid.frames[0],
            polyvid.frames[1],
            0.5
        );
        console.log("Interpolated frame 0.5 -> " + interp.drawCommands.length + " draw commands");
    }

    console.log("");
    console.log("Done.");
}

main();

module.exports = { PolyObject, PolyFrame, PolyVideoEncoder, PolyVideoDecoder, PolyVideoCodec };
