import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import os
import uuid
import time
import struct


class PolyObject:
    def __init__(self, kind, params, style):
        self.kind = kind
        self.params = params
        self.style = style
        self.id = str(uuid.uuid4())[:8]

    def to_dict(self):
        d = {"id": self.id, "kind": self.kind, "style": self.style}
        if self.kind == "polyline":
            d["x_coeff"] = [float(c) for c in self.params.get("x_coeff", [])]
            d["y_coeff"] = [float(c) for c in self.params.get("y_coeff", [])]
            d["t_range"] = self.params.get("t_range", [0.0, 1.0])
        elif self.kind == "circle":
            d["cx"] = float(self.params.get("cx", 0))
            d["cy"] = float(self.params.get("cy", 0))
            d["r"] = float(self.params.get("r", 0))
        elif self.kind == "polygon":
            d["x"] = [float(v) for v in self.params.get("x", [])]
            d["y"] = [float(v) for v in self.params.get("y", [])]
        elif self.kind == "fill":
            d["x"] = [float(v) for v in self.params.get("x", [])]
            d["y"] = [float(v) for v in self.params.get("y", [])]
        elif self.kind == "text":
            d["x"] = float(self.params.get("x", 0))
            d["y"] = float(self.params.get("y", 0))
            d["text"] = self.params.get("text", "")
        return d

    @staticmethod
    def from_dict(d):
        kind = d["kind"]
        style = d.get("style", {"color": "#ffffff", "linewidth": 1.0, "alpha": 1.0})
        if kind == "polyline":
            params = {
                "x_coeff": d.get("x_coeff", []),
                "y_coeff": d.get("y_coeff", []),
                "t_range": d.get("t_range", [0.0, 1.0]),
            }
        elif kind == "circle":
            params = {"cx": d.get("cx", 0), "cy": d.get("cy", 0), "r": d.get("r", 0)}
        elif kind in ("polygon", "fill"):
            params = {"x": d.get("x", []), "y": d.get("y", [])}
        elif kind == "text":
            params = {"x": d.get("x", 0), "y": d.get("y", 0), "text": d.get("text", "")}
        else:
            params = {}
        obj = PolyObject(kind, params, style)
        obj.id = d.get("id", obj.id)
        return obj


class PolyFrame:
    def __init__(self, width=640, height=480, background="#0d0a1a"):
        self.width = width
        self.height = height
        self.background = background
        self.objects = []
        self.delta_from = -1
        self.changes = []

    def add_object(self, obj):
        self.objects.append(obj)

    def to_dict(self):
        return {
            "width": self.width,
            "height": self.height,
            "background": self.background,
            "objects": [o.to_dict() for o in self.objects],
            "delta_from": self.delta_from,
            "changes": self.changes,
        }

    @staticmethod
    def from_dict(d):
        f = PolyFrame(d.get("width", 640), d.get("height", 480), d.get("background", "#0d0a1a"))
        f.delta_from = d.get("delta_from", -1)
        f.changes = d.get("changes", [])
        for od in d.get("objects", []):
            f.add_object(PolyObject.from_dict(od))
        return f


class PolyVideoEncoder:
    def __init__(self, degree=6, quantization_bits=8, keyframe_interval=10):
        self.degree = degree
        self.quant_bits = quantization_bits
        self.keyframe_interval = keyframe_interval

    def detect_edges(self, image, threshold=0.3):
        if image.ndim == 3:
            gray = np.mean(image[:, :, :3], axis=2)
        else:
            gray = image.astype(float)
        if gray.max() > 1.0:
            gray = gray / 255.0
        gy = np.zeros_like(gray)
        gx = np.zeros_like(gray)
        gy[1:-1, :] = gray[2:, :] - gray[:-2, :]
        gx[:, 1:-1] = gray[:, 2:] - gray[:, :-2]
        mag = np.sqrt(gx ** 2 + gy ** 2)
        edges = (mag > threshold).astype(np.uint8)
        return edges

    def extract_contours(self, edges):
        h, w = edges.shape
        visited = np.zeros_like(edges, dtype=bool)
        contours = []
        for r in range(1, h - 1):
            for c in range(1, w - 1):
                if edges[r, c] == 1 and not visited[r, c]:
                    contour = []
                    cr, cc = r, c
                    while True:
                        if visited[cr, cc]:
                            break
                        visited[cr, cc] = True
                        contour.append((cc, cr))
                        found = False
                        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0),
                                        (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < h and 0 <= nc < w and edges[nr, nc] == 1 and not visited[nr, nc]:
                                cr, cc = nr, nc
                                found = True
                                break
                        if not found:
                            break
                    if len(contour) >= 4:
                        contours.append(contour)
        return contours

    def fit_polynomial(self, points, degree=None):
        if degree is None:
            degree = self.degree
        if len(points) < 2:
            return np.zeros(degree + 1), np.zeros(degree + 1)
        pts = np.array(points, dtype=float)
        t = np.linspace(0, 1, len(pts))
        deg = min(degree, len(pts) - 1)
        x_coeff = np.polyfit(t, pts[:, 0], deg)
        y_coeff = np.polyfit(t, pts[:, 1], deg)
        return x_coeff, y_coeff

    def quantize_curve(self, coeffs, bits=None):
        if bits is None:
            bits = self.quant_bits
        if len(coeffs) == 0:
            return []
        c = np.array(coeffs, dtype=float)
        mx = np.max(np.abs(c))
        if mx < 1e-10:
            return [0] * len(c)
        scale = (2 ** (bits - 1) - 1) / mx
        quantized = np.round(c * scale).astype(int)
        return quantized.tolist()

    def dequantize_curve(self, quantized, original_max=None, bits=None):
        if bits is None:
            bits = self.quant_bits
        if len(quantized) == 0:
            return np.array([])
        c = np.array(quantized, dtype=float)
        if original_max is not None and original_max > 0:
            scale = original_max / (2 ** (bits - 1) - 1)
        else:
            scale = 1.0
        return c * scale

    def sample_color(self, image, point):
        h, w = image.shape[:2]
        x, y = int(round(point[0])), int(round(point[1]))
        x = max(0, min(w - 1, x))
        y = max(0, min(h - 1, y))
        if image.ndim == 3:
            r = int(image[y, x, 0] * 255) if image[y, x, 0] <= 1.0 else int(image[y, x, 0])
            g = int(image[y, x, 1] * 255) if image[y, x, 1] <= 1.0 else int(image[y, x, 1])
            b = int(image[y, x, 2] * 255) if image[y, x, 2] <= 1.0 else int(image[y, x, 2])
            return f"#{min(r,255):02x}{min(g,255):02x}{min(b,255):02x}"
        else:
            v = int(image[y, x] * 255) if image[y, x] <= 1.0 else int(image[y, x])
            v = min(v, 255)
            return f"#{v:02x}{v:02x}{v:02x}"

    def encode_frame(self, image_array):
        h, w = image_array.shape[:2]
        if image_array.ndim == 3:
            bg_sample = image_array[h // 2, w // 2]
        else:
            bg_sample = image_array[h // 2, w // 2]
        bg = self.sample_color(image_array, (w // 2, 0))

        frame = PolyFrame(w, h, bg)
        edges = self.detect_edges(image_array)
        contours = self.extract_contours(edges)

        for contour in contours:
            if len(contour) < 4:
                continue
            pts = contour[::max(1, len(contour) // 200)]
            if len(pts) < 4:
                continue
            x_coeff, y_coeff = self.fit_polynomial(pts)
            color = self.sample_color(image_array, pts[len(pts) // 2])
            style = {"color": color, "linewidth": 1.2, "alpha": 0.85}
            obj = PolyObject("polyline", {
                "x_coeff": self.quantize_curve(x_coeff),
                "y_coeff": self.quantize_curve(y_coeff),
                "t_range": [0.0, 1.0],
                "x_max": float(np.max(np.abs(x_coeff))),
                "y_max": float(np.max(np.abs(y_coeff))),
            }, style)
            frame.add_object(obj)

        if len(frame.objects) == 0:
            cx, cy = w // 2, h // 2
            obj = PolyObject("circle", {"cx": cx, "cy": cy, "r": 10},
                             {"color": "#ffffff", "linewidth": 1, "alpha": 1.0})
            frame.add_object(obj)

        return frame

    def encode_delta(self, prev_frame, curr_frame):
        delta = PolyFrame(curr_frame.width, curr_frame.height, curr_frame.background)
        delta.delta_from = 0

        prev_ids = {o.id: o for o in prev_frame.objects}
        curr_ids = {o.id: o for o in curr_frame.objects}

        added = []
        removed = []
        modified = []

        for obj in curr_frame.objects:
            if obj.id not in prev_ids:
                added.append(obj.to_dict())
            else:
                prev_obj = prev_ids[obj.id]
                if obj.params != prev_obj.params or obj.style != prev_obj.style:
                    modified.append(obj.to_dict())

        for obj in prev_frame.objects:
            if obj.id not in curr_ids:
                removed.append(obj.id)

        delta.changes = [{"type": "added", "objects": added},
                         {"type": "removed", "ids": removed},
                         {"type": "modified", "objects": modified}]
        return delta

    def read_image(self, path):
        try:
            img = plt.imread(path)
            if img.dtype == np.uint8:
                img = img.astype(float) / 255.0
            return img
        except Exception:
            return None

    def create_demo_frames(self, n_frames=10, width=640, height=480):
        frames = []
        for i in range(n_frames):
            fig, ax = plt.subplots(1, 1, figsize=(width / 100, height / 100), dpi=100)
            fig.patch.set_facecolor("#0d0a1a")
            ax.set_xlim(0, width)
            ax.set_ylim(0, height)
            ax.set_facecolor("#0d0a1a")
            ax.set_aspect("equal")
            ax.axis("off")
            fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

            t = i / max(n_frames - 1, 1)
            cx = 100 + t * (width - 200)
            cy = height // 2
            circle = plt.Circle((cx, cy), 30, fill=False, edgecolor="#c8a040", linewidth=2)
            ax.add_patch(circle)

            angle = t * np.pi * 2
            lx1 = width // 2 + 80 * np.cos(angle)
            ly1 = height // 2 + 80 * np.sin(angle)
            lx2 = width // 2 + 80 * np.cos(angle + np.pi)
            ly2 = height // 2 + 80 * np.sin(angle + np.pi)
            ax.plot([lx1, lx2], [ly1, ly2], color="#40a0c8", linewidth=2)

            bx = 100 + t * 200
            by = 80 + 40 * np.sin(t * np.pi * 3)
            rect = plt.Rectangle((bx, by), 50, 30, fill=False, edgecolor="#a0c840", linewidth=1.5)
            ax.add_patch(rect)

            fig.canvas.draw()
            buf = fig.canvas.buffer_rgba()
            arr = np.asarray(buf)[:, :, :3].copy()
            plt.close(fig)
            frames.append(arr)
        return frames

    def encode_video(self, video_path, output_path):
        frames = []
        if video_path == "__demo__":
            frames = self.create_demo_frames()
        else:
            img = self.read_image(video_path)
            if img is not None:
                frames = [img]

        if not frames:
            print("[ERROR] No frames to encode")
            return

        width = frames[0].shape[1]
        height = frames[0].shape[0]
        fps = 24

        polyvid = {
            "format": "polyvid/1.0",
            "codec": "polyart-video-v1",
            "width": width,
            "height": height,
            "fps": fps,
            "total_frames": len(frames),
            "keyframe_interval": self.keyframe_interval,
            "polynomial_degree": self.degree,
            "quantization_bits": self.quant_bits,
            "frames": [],
        }

        prev_poly = None
        for i, frame_arr in enumerate(frames):
            poly = self.encode_frame(frame_arr)
            if i % self.keyframe_interval == 0 or prev_poly is None:
                frame_entry = {
                    "index": i,
                    "type": "keyframe",
                    "background": poly.background,
                    "objects": [o.to_dict() for o in poly.objects],
                }
                polyvid["frames"].append(frame_entry)
            else:
                delta = self.encode_delta(prev_poly, poly)
                frame_entry = {
                    "index": i,
                    "type": "delta",
                    "delta_from": delta.delta_from,
                    "background": poly.background,
                    "changes": delta.changes,
                }
                polyvid["frames"].append(frame_entry)
            prev_poly = poly
            if (i + 1) % 5 == 0 or i == len(frames) - 1:
                print(f"  Encoded frame {i+1}/{len(frames)}")

        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(polyvid, f)
        print(f"  Saved to {output_path}")
        return polyvid


class PolyVideoDecoder:
    def __init__(self):
        self.last_keyframe = None

    def render_polyobject(self, ax, obj_dict):
        kind = obj_dict.get("kind", "polyline")
        style = obj_dict.get("style", {})
        color = style.get("color", "#ffffff")
        linewidth = style.get("linewidth", 1.0)
        alpha = style.get("alpha", 1.0)

        if kind == "polyline":
            x_coeff = obj_dict.get("x_coeff", [])
            y_coeff = obj_dict.get("y_coeff", [])
            if len(x_coeff) == 0 or len(y_coeff) == 0:
                return
            x_max = obj_dict.get("x_max", 1.0)
            y_max = obj_dict.get("y_max", 1.0)
            if x_max < 1e-6:
                x_max = 1.0
            if y_max < 1e-6:
                y_max = 1.0
            bits = 7
            scale_x = x_max / (2 ** (bits - 1) - 1)
            scale_y = y_max / (2 ** (bits - 1) - 1)
            xc = np.array(x_coeff, dtype=float) * scale_x
            yc = np.array(y_coeff, dtype=float) * scale_y
            t = np.linspace(0, 1, 200)
            x = np.polyval(xc, t)
            y = np.polyval(yc, t)
            ax.plot(x, y, color=color, linewidth=linewidth, alpha=alpha, solid_capstyle="round")
        elif kind == "circle":
            cx = obj_dict.get("cx", 0)
            cy = obj_dict.get("cy", 0)
            r = obj_dict.get("r", 10)
            circle = plt.Circle((cx, cy), r, fill=False, edgecolor=color,
                                linewidth=linewidth, alpha=alpha)
            ax.add_patch(circle)
        elif kind == "polygon":
            x = obj_dict.get("x", [])
            y = obj_dict.get("y", [])
            if len(x) >= 3 and len(y) >= 3:
                ax.fill(x, y, facecolor=color, edgecolor=color,
                        linewidth=linewidth, alpha=alpha)
        elif kind == "fill":
            x = obj_dict.get("x", [])
            y = obj_dict.get("y", [])
            if len(x) >= 2 and len(y) >= 2:
                ax.fill_between(x, y, color=color, alpha=alpha)
        elif kind == "text":
            x = obj_dict.get("x", 0)
            y = obj_dict.get("y", 0)
            txt = obj_dict.get("text", "")
            ax.text(x, y, txt, color=color, fontsize=10, alpha=alpha)

    def decode_frame(self, poly_frame_dict):
        width = poly_frame_dict.get("width", 640)
        height = poly_frame_dict.get("height", 480)
        bg = poly_frame_dict.get("background", "#0d0a1a")

        fig, ax = plt.subplots(1, 1, figsize=(width / 100, height / 100), dpi=100)
        fig.patch.set_facecolor(bg)
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.set_facecolor(bg)
        ax.set_aspect("equal")
        ax.axis("off")
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        objects = poly_frame_dict.get("objects", [])
        for obj in objects:
            self.render_polyobject(ax, obj)

        fig.canvas.draw()
        buf = fig.canvas.buffer_rgba()
        arr = np.asarray(buf)[:, :, :3].copy()
        plt.close(fig)
        return arr

    def decode_video(self, polyvid_path, output_dir):
        with open(polyvid_path, "r", encoding="utf-8") as f:
            polyvid = json.load(f)

        os.makedirs(output_dir, exist_ok=True)
        width = polyvid.get("width", 640)
        height = polyvid.get("height", 480)
        bg = polyvid.get("background", "#0d0a1a")

        frames_data = polyvid.get("frames", [])
        self.last_keyframe = None
        decoded_frames = []

        for entry in frames_data:
            ftype = entry.get("type", "keyframe")
            if ftype == "keyframe":
                frame_dict = {
                    "width": width,
                    "height": height,
                    "background": entry.get("background", bg),
                    "objects": entry.get("objects", []),
                }
                self.last_keyframe = frame_dict
            elif ftype == "delta" and self.last_keyframe is not None:
                frame_dict = {
                    "width": width,
                    "height": height,
                    "background": entry.get("background", self.last_keyframe.get("background", bg)),
                    "objects": list(self.last_keyframe.get("objects", [])),
                }
                for change in entry.get("changes", []):
                    ctype = change.get("type", "")
                    if ctype == "added":
                        frame_dict["objects"].extend(change.get("objects", []))
                    elif ctype == "removed":
                        removed_ids = set(change.get("ids", []))
                        frame_dict["objects"] = [
                            o for o in frame_dict["objects"] if o.get("id", "") not in removed_ids
                        ]
                    elif ctype == "modified":
                        mod_map = {o.get("id", ""): o for o in change.get("objects", [])}
                        new_objs = []
                        for o in frame_dict["objects"]:
                            oid = o.get("id", "")
                            if oid in mod_map:
                                new_objs.append(mod_map[oid])
                            else:
                                new_objs.append(o)
                        frame_dict["objects"] = new_objs
                self.last_keyframe = frame_dict
            else:
                continue

            img = self.decode_frame(frame_dict)
            decoded_frames.append(img)
            idx = entry.get("index", len(decoded_frames) - 1)
            out_path = os.path.join(output_dir, f"frame_{idx:04d}.png")
            plt.imsave(out_path, img)
            print(f"  Decoded frame {idx+1}/{len(frames_data)}")

        return decoded_frames

    def interpolate_frame(self, frame1_dict, frame2_dict, t):
        width = frame1_dict.get("width", 640)
        height = frame1_dict.get("height", 480)
        bg1 = frame1_dict.get("background", "#0d0a1a")
        bg2 = frame2_dict.get("background", bg1)

        result = {
            "width": width,
            "height": height,
            "background": bg1,
            "objects": [],
        }

        objs1 = frame1_dict.get("objects", [])
        objs2 = frame2_dict.get("objects", [])

        max_len = max(len(objs1), len(objs2))
        for i in range(max_len):
            if i < len(objs1) and i < len(objs2):
                o1, o2 = objs1[i], objs2[i]
                if o1.get("kind") == "polyline" and o2.get("kind") == "polyline":
                    c1 = np.array(o1.get("x_coeff", []), dtype=float)
                    c2 = np.array(o2.get("x_coeff", []), dtype=float)
                    ml = min(len(c1), len(c2))
                    if ml > 0:
                        xc = c1[:ml] * (1 - t) + c2[:ml] * t
                    else:
                        xc = c1
                    c1y = np.array(o1.get("y_coeff", []), dtype=float)
                    c2y = np.array(o2.get("y_coeff", []), dtype=float)
                    mly = min(len(c1y), len(c2y))
                    if mly > 0:
                        yc = c1y[:mly] * (1 - t) + c2y[:mly] * t
                    else:
                        yc = c1y
                    style1 = o1.get("style", {})
                    style2 = o2.get("style", {})
                    result["objects"].append({
                        "id": o1.get("id", f"interp_{i}"),
                        "kind": "polyline",
                        "x_coeff": xc.tolist(),
                        "y_coeff": yc.tolist(),
                        "x_max": o1.get("x_max", 1.0),
                        "y_max": o1.get("y_max", 1.0),
                        "t_range": [0.0, 1.0],
                        "style": style1,
                    })
                elif o1.get("kind") == "circle" and o2.get("kind") == "circle":
                    cx = o1.get("cx", 0) * (1 - t) + o2.get("cx", 0) * t
                    cy = o1.get("cy", 0) * (1 - t) + o2.get("cy", 0) * t
                    r = o1.get("r", 10) * (1 - t) + o2.get("r", 10) * t
                    result["objects"].append({
                        "id": o1.get("id", f"interp_{i}"),
                        "kind": "circle",
                        "cx": cx, "cy": cy, "r": r,
                        "style": o1.get("style", {}),
                    })
                else:
                    result["objects"].append(o1 if t < 0.5 else o2)
            elif i < len(objs1):
                result["objects"].append(objs1[i])
            else:
                result["objects"].append(objs2[i])

        return result


class PolyVideoCodec:
    def __init__(self):
        self.encoder = PolyVideoEncoder()
        self.decoder = PolyVideoDecoder()

    def compress(self, input_video, output_polyvid, quality="medium"):
        quality_map = {"low": 3, "medium": 6, "high": 10}
        degree = quality_map.get(quality, 6)
        self.encoder.degree = degree

        print(f"[ENCODE] Quality: {quality}, Degree: {degree}")
        t0 = time.time()
        polyvid = self.encoder.encode_video(input_video, output_polyvid)
        elapsed = time.time() - t0

        if polyvid is None:
            return None

        total_frames = polyvid.get("total_frames", 0)
        keyframes = sum(1 for f in polyvid["frames"] if f.get("type") == "keyframe")
        delta_frames = total_frames - keyframes

        orig_size = 0
        if input_video != "__demo__":
            try:
                orig_size = os.path.getsize(input_video)
            except OSError:
                orig_size = 0

        comp_size = os.path.getsize(output_polyvid)

        stats = {
            "total_frames": total_frames,
            "keyframes": keyframes,
            "delta_frames": delta_frames,
            "original_bytes": orig_size,
            "compressed_bytes": comp_size,
            "compression_ratio": orig_size / comp_size if comp_size > 0 else 0,
            "encode_time_sec": elapsed,
            "polynomial_degree": degree,
        }
        return stats

    def decompress(self, input_polyvid, output_dir):
        print("[DECODE] Decoding polyvid...")
        t0 = time.time()
        frames = self.decoder.decode_video(input_polyvid, output_dir)
        elapsed = time.time() - t0

        with open(input_polyvid, "r", encoding="utf-8") as f:
            polyvid = json.load(f)

        return {
            "frame_count": len(frames),
            "fps": polyvid.get("fps", 24),
            "decode_time_sec": elapsed,
        }

    def get_stats(self, polyvid_path):
        with open(polyvid_path, "r", encoding="utf-8") as f:
            polyvid = json.load(f)

        total_frames = polyvid.get("total_frames", 0)
        keyframes = sum(1 for f in polyvid["frames"] if f.get("type") == "keyframe")
        delta_frames = total_frames - keyframes
        comp_size = os.path.getsize(polyvid_path)
        total_objects = sum(
            len(f.get("objects", [])) + sum(
                len(c.get("objects", [])) for c in f.get("changes", [])
            )
            for f in polyvid["frames"]
        )

        return {
            "total_frames": total_frames,
            "keyframes": keyframes,
            "delta_frames": delta_frames,
            "compressed_bytes": comp_size,
            "total_objects": total_objects,
            "width": polyvid.get("width", 0),
            "height": polyvid.get("height", 0),
            "polynomial_degree": polyvid.get("polynomial_degree", 6),
            "quantization_bits": polyvid.get("quantization_bits", 8),
        }


class PolyVideoPlayer:
    def __init__(self):
        self.decoder = PolyVideoDecoder()

    def play(self, polyvid_path, output_dir):
        print(f"[PLAYER] Rendering frames to {output_dir}")
        return self.decoder.decode_video(polyvid_path, output_dir)

    def preview(self, polyvid_path, n_frames=5):
        with open(polyvid_path, "r", encoding="utf-8") as f:
            polyvid = json.load(f)

        frames_data = polyvid.get("frames", [])
        width = polyvid.get("width", 640)
        height = polyvid.get("height", 480)
        bg = polyvid.get("background", "#0d0a1a")

        step = max(1, len(frames_data) // n_frames)
        selected = frames_data[::step][:n_frames]

        images = []
        last_kf = None
        for entry in selected:
            ftype = entry.get("type", "keyframe")
            if ftype == "keyframe":
                fd = {"width": width, "height": height,
                      "background": entry.get("background", bg),
                      "objects": entry.get("objects", [])}
                last_kf = fd
            elif last_kf is not None:
                fd = {"width": width, "height": height,
                      "background": entry.get("background", bg),
                      "objects": list(last_kf.get("objects", []))}
                for ch in entry.get("changes", []):
                    ct = ch.get("type", "")
                    if ct == "added":
                        fd["objects"].extend(ch.get("objects", []))
                    elif ct == "removed":
                        rids = set(ch.get("ids", []))
                        fd["objects"] = [o for o in fd["objects"] if o.get("id", "") not in rids]
            else:
                continue
            img = self.decoder.decode_frame(fd)
            images.append(img)

        return images


def create_comparison(original_frames, decoded_frames, output_path):
    n = min(len(original_frames), len(decoded_frames), 4)
    if n == 0:
        print("[WARN] No frames for comparison")
        return

    fig, axes = plt.subplots(n, 2, figsize=(12, 3 * n))
    if n == 1:
        axes = np.array([axes])
    axes = np.array(axes).reshape(n, 2)

    for i in range(n):
        axes[i, 0].imshow(original_frames[i])
        axes[i, 0].set_title(f"Original Frame {i}", fontsize=9)
        axes[i, 0].axis("off")
        axes[i, 1].imshow(decoded_frames[i])
        axes[i, 1].set_title(f"Decoded Frame {i}", fontsize=9)
        axes[i, 1].axis("off")

    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close()
    print(f"[INFO] Comparison saved to {output_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("  POLYART VIDEO CODEC - Demo")
    print("=" * 60)

    work_dir = os.path.dirname(os.path.abspath(__file__))
    polyvid_path = os.path.join(work_dir, "demo.polyvid")
    decoded_dir = os.path.join(work_dir, "decoded_frames")
    comparison_path = os.path.join(work_dir, "comparison.png")

    codec = PolyVideoCodec()

    print("\n[1] Encoding demo video to polyvid...")
    stats = codec.compress("__demo__", polyvid_path, quality="medium")

    print("\n[2] Compression stats:")
    for k, v in stats.items():
        print(f"    {k}: {v}")

    print("\n[3] Decoding polyvid to frames...")
    decode_info = codec.decompress(polyvid_path, decoded_dir)

    print(f"\n[4] Decoded {decode_info['frame_count']} frames at {decode_info['fps']} fps")
    print(f"    Decode time: {decode_info['decode_time_sec']:.2f}s")

    print("\n[5] Polyvid file stats:")
    pv_stats = codec.get_stats(polyvid_path)
    for k, v in pv_stats.items():
        print(f"    {k}: {v}")

    print("\n[6] Generating comparison figure...")
    encoder = PolyVideoEncoder()
    original_frames = encoder.create_demo_frames(n_frames=10)
    decoded_frames = []
    if os.path.isdir(decoded_dir):
        for fn in sorted(os.listdir(decoded_dir)):
            if fn.endswith(".png"):
                img = plt.imread(os.path.join(decoded_dir, fn))
                decoded_frames.append(img)

    create_comparison(original_frames, decoded_frames, comparison_path)

    print("\n[DONE] All files created:")
    print(f"    {polyvid_path}")
    print(f"    {decoded_dir}/")
    print(f"    {comparison_path}")
