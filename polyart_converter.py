import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
from matplotlib.path import Path
import numpy as np
import json
import os
import sys
import struct
import base64
import math
import glob as globmod
import re
from io import BytesIO
from pathlib import Path as Pathlib

# =============================================================================
# ImageToPolyart - Convert raster images to polyart polynomial format
# =============================================================================

class ImageToPolyart:
    def load_image(self, path):
        img = plt.imread(path)
        if img.dtype == np.float64 or img.dtype == np.float32:
            if img.max() <= 1.0:
                img = (img * 255).astype(np.uint8)
        if img.ndim == 2:
            img = np.stack([img, img, img], axis=-1)
        if img.shape[2] == 4:
            rgb = img[:, :, :3].astype(np.float64)
            alpha = img[:, :, 3:4].astype(np.float64) / 255.0 if img[:, :, 3].max() > 1 else img[:, :, 3:4].astype(np.float64)
            bg = np.ones_like(rgb) * 255.0
            img = (rgb * alpha + bg * (1.0 - alpha)).astype(np.uint8)
        return img[:, :, :3]

    def extract_edges(self, img, threshold=0.3):
        gray = np.mean(img[:, :, :3].astype(np.float64), axis=2)
        gray = gray / 255.0
        h, w = gray.shape
        padded = np.zeros((h + 2, w + 2))
        padded[1:-1, 1:-1] = gray
        sobel_x = np.zeros_like(gray)
        sobel_y = np.zeros_like(gray)
        for i in range(h):
            for j in range(w):
                patch = padded[i:i + 3, j:j + 3]
                gx = (-patch[0, 0] + patch[0, 2]
                       - 2 * patch[1, 0] + 2 * patch[1, 2]
                       - patch[2, 0] + patch[2, 2])
                gy = (-patch[0, 0] - 2 * patch[0, 1] - patch[0, 2]
                       + patch[2, 0] + 2 * patch[2, 1] + patch[2, 2])
                sobel_x[i, j] = gx
                sobel_y[i, j] = gy
        magnitude = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
        mag_max = magnitude.max()
        if mag_max > 0:
            magnitude = magnitude / mag_max
        edges = magnitude > threshold
        return edges

    def extract_contours(self, edges):
        h, w = edges.shape
        visited = np.zeros_like(edges, dtype=bool)
        contours = []
        for i in range(h):
            for j in range(w):
                if edges[i, j] and not visited[i, j]:
                    contour = []
                    ci, cj = i, j
                    while True:
                        if visited[ci, cj]:
                            break
                        visited[ci, cj] = True
                        contour.append((cj, ci))
                        found = False
                        for di in [-1, 0, 1]:
                            for dj in [-1, 0, 1]:
                                if di == 0 and dj == 0:
                                    continue
                                ni, nj = ci + di, cj + dj
                                if 0 <= ni < h and 0 <= nj < w:
                                    if edges[ni, nj] and not visited[ni, nj]:
                                        ci, cj = ni, nj
                                        found = True
                                        break
                            if found:
                                break
                        if not found:
                            break
                    if len(contour) >= 4:
                        contours.append(np.array(contour, dtype=np.float64))
        return contours

    def fit_polynomials(self, points, degree=6):
        n = len(points)
        if n < 2:
            return None, None
        t = np.linspace(0, 1, n)
        degree = min(degree, n - 1)
        try:
            x_coeffs = np.polyfit(t, points[:, 0], degree)
            y_coeffs = np.polyfit(t, points[:, 1], degree)
        except (np.linalg.LinAlgError, ValueError):
            return None, None
        return x_coeffs.tolist(), y_coeffs.tolist()

    def extract_colors(self, img, points, sample_radius=2):
        h, w = img.shape[:2]
        colors = []
        for pt in points:
            px, py = int(round(pt[0])), int(round(pt[1]))
            px = max(0, min(w - 1, px))
            py = max(0, min(h - 1, py))
            r, g, b = img[py, px, 0], img[py, px, 1], img[py, px, 2]
            colors.append("#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b)))
        if colors:
            return [colors[len(colors) // 2]]
        return ["#000000"]

    def image_to_polyart(self, img, degree=6, threshold=0.3):
        edges = self.extract_edges(img, threshold)
        contours = self.extract_contours(edges)
        poly_objects = []
        for contour in contours:
            if len(contour) < 4:
                continue
            step = max(1, len(contour) // 50)
            sampled = contour[::step]
            x_coeffs, y_coeffs = self.fit_polynomials(sampled, degree)
            if x_coeffs is None:
                continue
            colors = self.extract_colors(img, sampled)
            color = colors[0] if colors else "#000000"
            poly_objects.append({
                "kind": "polyline",
                "x_coeff": x_coeffs,
                "y_coeff": y_coeffs,
                "color": color,
                "style": {"linewidth": 1.0, "linestyle": "-"}
            })
        return poly_objects

    def convert(self, input_path, output_path, degree=6, threshold=0.3):
        img = self.load_image(input_path)
        objects = self.image_to_polyart(img, degree, threshold)
        h, w = img.shape[:2]
        polyart_data = {
            "version": "1.0",
            "format": "polyart",
            "width": int(w),
            "height": int(h),
            "objects": objects,
            "metadata": {
                "source": input_path,
                "degree": degree,
                "threshold": threshold,
                "object_count": len(objects)
            }
        }
        with open(output_path, "w") as f:
            json.dump(polyart_data, f, indent=2)
        return polyart_data


# =============================================================================
# PolyartToImage - Convert polyart polynomial format back to raster images
# =============================================================================

class PolyartToImage:
    def load_polyart(self, path):
        with open(path) as f:
            data = json.load(f)
        return data

    def render_polyobject(self, ax, obj):
        kind = obj.get("kind", "polyline")
        x_coeffs = obj.get("x_coeff", [])
        y_coeffs = obj.get("y_coeff", [])
        color = obj.get("color", "#000000")
        style = obj.get("style", {})
        lw = style.get("linewidth", 1.0)
        ls = style.get("linestyle", "-")
        fill = style.get("fill", None)
        if not x_coeffs or not y_coeffs:
            return
        t = np.linspace(0, 1, 200)
        x_vals = np.polyval(x_coeffs, t)
        y_vals = np.polyval(y_coeffs, t)
        if kind == "circle":
            cx = np.mean(x_vals)
            cy = np.mean(y_vals)
            rx = (np.max(x_vals) - np.min(x_vals)) / 2.0
            ry = (np.max(y_vals) - np.min(y_vals)) / 2.0
            theta = np.linspace(0, 2 * np.pi, 200)
            cx_arr = cx + rx * np.cos(theta)
            cy_arr = cy + ry * np.sin(theta)
            if fill:
                ax.fill(cx_arr, cy_arr, color=fill, alpha=0.7)
            ax.plot(cx_arr, cy_arr, color=color, linewidth=lw, linestyle=ls)
        elif kind == "polygon":
            if fill:
                ax.fill(x_vals, y_vals, color=fill, alpha=0.7)
            verts = list(zip(x_vals, y_vals))
            verts.append((x_vals[0], y_vals[0]))
            codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 2) + [Path.CLOSEPOLY]
            path = Path(verts, codes)
            patch = mpatches.PathPatch(path, facecolor=fill or "none", edgecolor=color, linewidth=lw)
            ax.add_patch(patch)
        else:
            if fill:
                ax.fill(x_vals, y_vals, color=fill, alpha=0.7)
            ax.plot(x_vals, y_vals, color=color, linewidth=lw, linestyle=ls)

    def render_frame(self, poly_data, width=None, height=None):
        w = width or poly_data.get("width", 800)
        h = height or poly_data.get("height", 600)
        dpi = 100
        fig, ax = plt.subplots(figsize=(w / dpi, h / dpi), dpi=dpi)
        bg = poly_data.get("background", "#ffffff")
        ax.set_facecolor(bg)
        fig.patch.set_facecolor(bg)
        for obj in poly_data.get("objects", []):
            self.render_polyobject(ax, obj)
        ax.set_xlim(0, w)
        ax.set_ylim(h, 0)
        ax.set_aspect("equal")
        ax.axis("off")
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        fig.canvas.draw()
        buf = fig.canvas.buffer_rgba()
        img = np.asarray(buf)
        img = img[:, :, :3]
        plt.close(fig)
        return img

    def convert(self, input_path, output_path, dpi=150):
        poly_data = self.load_polyart(input_path)
        w = poly_data.get("width", 800)
        h = poly_data.get("height", 600)
        fig, ax = plt.subplots(figsize=(w / dpi, h / dpi), dpi=dpi)
        bg = poly_data.get("background", "#ffffff")
        ax.set_facecolor(bg)
        fig.patch.set_facecolor(bg)
        for obj in poly_data.get("objects", []):
            self.render_polyobject(ax, obj)
        ax.set_xlim(0, w)
        ax.set_ylim(h, 0)
        ax.set_aspect("equal")
        ax.axis("off")
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        plt.savefig(output_path, dpi=dpi, bbox_inches="tight", pad_inches=0)
        plt.close(fig)
        return output_path


# =============================================================================
# VideoToPolyvid - Convert video files to polyvid format
# =============================================================================

class VideoToPolyvid:
    def load_video_frames(self, path):
        try:
            anim = animation.FuncAnimation
        except Exception:
            pass
        ext = os.path.splitext(path)[1].lower()
        frames = []
        fps = 24
        if ext == ".gif":
            fig_tmp, ax_tmp = plt.subplots()
            patch = ax_tmp.imshow(plt.imread(path))
            n_frames = 100
            try:
                from PIL import Image as PILImage
                gif = PILImage.open(path)
                n_frames = gif.n_frames
                try:
                    fps = 1000.0 / gif.info.get("duration", 100)
                except Exception:
                    fps = 24
            except ImportError:
                pass
            fig, ax = plt.subplots()

            def update(frame_idx):
                try:
                    data = plt.imread(path)
                    patch.set_data(data)
                except Exception:
                    pass
                return [patch]

            ani = animation.FuncAnimation(fig, update, frames=min(n_frames, 300), interval=1000 / fps)
            buf = BytesIO()
            try:
                ani.save(buf, writer="pillow", fps=fps)
                buf.seek(0)
                gif_img = plt.imread(buf)
                if gif_img.ndim == 3 and gif_img.shape[2] == 4:
                    gif_img = gif_img[:, :, :3]
                frames.append(gif_img)
            except Exception:
                img = plt.imread(path)
                if img.ndim == 3:
                    if img.shape[2] == 4:
                        img = img[:, :, :3]
                    frames.append(img)
            plt.close(fig)
            plt.close(fig_tmp)
        else:
            try:
                img = plt.imread(path)
                if img.ndim == 3:
                    if img.shape[2] == 4:
                        img = img[:, :, :3]
                    frames.append(img)
            except Exception:
                img = np.zeros((240, 320, 3), dtype=np.uint8)
                frames.append(img)
        return frames, fps

    def encode_frames(self, frames, width, height, fps, degree=6, keyframe_interval=10):
        if not frames:
            return {"version": "1.0", "format": "polyvid", "frames": [], "fps": fps}
        poly_frames = []
        prev_objects = None
        for idx, frame in enumerate(frames):
            is_keyframe = (idx % keyframe_interval == 0) or prev_objects is None
            img_to = ImageToPolyart()
            if frame.shape[0] != height or frame.shape[1] != width:
                fig_tmp, ax_tmp = plt.subplots()
                ax_tmp.imshow(frame)
                ax_tmp.set_xlim(0, width)
                ax_tmp.set_ylim(height, 0)
                plt.close(fig_tmp)
            objects = img_to.image_to_polyart(frame, degree, threshold=0.35)
            frame_data = {
                "frame_index": idx,
                "is_keyframe": is_keyframe,
                "objects": objects
            }
            if not is_keyframe and prev_objects is not None:
                n_prev = len(prev_objects)
                n_curr = len(objects)
                frame_data["object_diff"] = {
                    "added": max(0, n_curr - n_prev),
                    "removed": max(0, n_prev - n_curr),
                    "total": n_curr
                }
            poly_frames.append(frame_data)
            prev_objects = objects
        poly_video = {
            "version": "1.0",
            "format": "polyvid",
            "width": width,
            "height": height,
            "fps": fps,
            "frame_count": len(frames),
            "keyframe_interval": keyframe_interval,
            "frames": poly_frames
        }
        return poly_video

    def convert(self, input_path, output_path, degree=6, fps_override=None, max_frames=120):
        frames, fps = self.load_video_frames(input_path)
        if fps_override:
            fps = fps_override
        if not frames:
            print("[WARN] No frames extracted from input.")
            return None
        frames = frames[:max_frames]
        h, w = frames[0].shape[:2]
        poly_video = self.encode_frames(frames, w, h, fps, degree)
        with open(output_path, "w") as f:
            json.dump(poly_video, f, indent=2)
        return poly_video


# =============================================================================
# PolyvidToVideo - Convert polyvid format back to video/GIF
# =============================================================================

class PolyvidToVideo:
    def load_polyvid(self, path):
        with open(path) as f:
            data = json.load(f)
        return data

    def decode_frames(self, poly_video):
        converter = PolyartToImage()
        frames = []
        w = poly_video.get("width", 800)
        h = poly_video.get("height", 600)
        current_objects = []
        for frame_data in poly_video.get("frames", []):
            if frame_data.get("is_keyframe", True):
                current_objects = frame_data.get("objects", [])
            else:
                diff = frame_data.get("object_diff", {})
                new_objs = frame_data.get("objects", [])
                if new_objs:
                    current_objects = new_objs
                elif diff.get("added", 0) > 0 or diff.get("removed", 0) > 0:
                    pass
            poly_frame = {
                "version": "1.0",
                "format": "polyart",
                "width": w,
                "height": h,
                "objects": current_objects if current_objects else frame_data.get("objects", []),
                "background": "#ffffff"
            }
            img = converter.render_frame(poly_frame, w, h)
            frames.append(img)
        return frames

    def save_gif(self, frames, output_path, fps=24):
        if not frames:
            print("[WARN] No frames to save.")
            return
        duration = 1000.0 / fps
        try:
            from PIL import Image as PILImage
            pil_frames = []
            for f in frames:
                arr = (f.astype(np.float64) / 255.0 * 255).astype(np.uint8) if f.max() <= 1.0 else f.astype(np.uint8)
                pil_frames.append(PILImage.fromarray(arr))
            pil_frames[0].save(
                output_path,
                save_all=True,
                append_images=pil_frames[1:],
                duration=int(duration),
                loop=0
            )
        except ImportError:
            fig, ax = plt.subplots()
            im = ax.imshow(frames[0])
            ax.axis("off")

            def update(i):
                im.set_data(frames[i])
                return [im]

            ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=duration, blit=True)
            ani.save(output_path, writer="pillow", fps=fps)
            plt.close(fig)

    def save_frames(self, frames, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        for i, frame in enumerate(frames):
            path = os.path.join(output_dir, "frame_{:05d}.png".format(i))
            arr = frame.astype(np.uint8) if frame.max() > 1.0 else (frame * 255).astype(np.uint8)
            plt.imsave(path, arr)

    def convert(self, input_path, output_path, fps=24):
        poly_video = self.load_polyvid(input_path)
        frames = self.decode_frames(poly_video)
        if not frames:
            print("[WARN] Decoded 0 frames.")
            return
        out_fps = fps or poly_video.get("fps", 24)
        ext = os.path.splitext(output_path)[1].lower()
        if ext == ".gif":
            self.save_gif(frames, output_path, out_fps)
        elif ext == ".png" or ext == ".jpg" or ext == ".jpeg":
            if len(frames) == 1:
                arr = frames[0].astype(np.uint8) if frames[0].max() > 1.0 else (frames[0] * 255).astype(np.uint8)
                plt.imsave(output_path, arr)
            else:
                out_dir = os.path.splitext(output_path)[0] + "_frames"
                self.save_frames(frames, out_dir)
                print("[INFO] Saved {} frames to {}".format(len(frames), out_dir))
        else:
            out_dir = os.path.splitext(output_path)[0] + "_frames"
            self.save_frames(frames, out_dir)
            print("[INFO] Saved {} frames to {}".format(len(frames), out_dir))
        return output_path


# =============================================================================
# FormatConverter - Main converter interface
# =============================================================================

class FormatConverter:
    def __init__(self):
        self.image_to_polyart = ImageToPolyart()
        self.polyart_to_image = PolyartToImage()
        self.video_to_polyvid = VideoToPolyvid()
        self.polyvid_to_video = PolyvidToVideo()
        self.IMAGE_IN = [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".tif", ".webp"]
        self.IMAGE_OUT = [".polyart"]
        self.VIDEO_IN = [".mp4", ".avi", ".mov", ".mkv", ".gif", ".webm", ".flv"]
        self.VIDEO_OUT = [".polyvid"]
        self.POLYART_IN = [".polyart"]
        self.POLYART_OUT = [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff"]
        self.POLYVID_IN = [".polyvid"]
        self.POLYVID_OUT = [".gif", ".png", ".jpg"]

    def get_format(self, path):
        ext = os.path.splitext(path)[1].lower()
        return ext

    def convert(self, input_path, output_path, **kwargs):
        in_fmt = self.get_format(input_path)
        out_fmt = self.get_format(output_path)
        print("[INFO] Converting {} ({}) -> {} ({})".format(
            os.path.basename(input_path), in_fmt,
            os.path.basename(output_path), out_fmt
        ))
        if in_fmt in self.IMAGE_IN and out_fmt in self.IMAGE_OUT:
            degree = kwargs.get("degree", 6)
            threshold = kwargs.get("threshold", 0.3)
            return self.image_to_polyart.convert(input_path, output_path, degree, threshold)
        elif in_fmt in self.POLYART_IN and out_fmt in self.POLYART_OUT:
            dpi = kwargs.get("dpi", 150)
            return self.polyart_to_image.convert(input_path, output_path, dpi)
        elif in_fmt in self.VIDEO_IN and out_fmt in self.VIDEO_OUT:
            degree = kwargs.get("degree", 6)
            fps = kwargs.get("fps", None)
            max_frames = kwargs.get("max_frames", 120)
            return self.video_to_polyvid.convert(input_path, output_path, degree, fps, max_frames)
        elif in_fmt in self.POLYVID_IN and out_fmt in self.POLYVID_OUT:
            fps = kwargs.get("fps", 24)
            return self.polyvid_to_video.convert(input_path, output_path, fps)
        elif in_fmt in self.IMAGE_IN and out_fmt in [".png", ".jpg", ".jpeg", ".bmp", ".gif"]:
            img = self.image_to_polyart.load_image(input_path)
            plt.imsave(output_path, img.astype(np.uint8) if img.max() > 1.0 else img)
            print("[INFO] Direct image copy saved.")
            return output_path
        elif in_fmt in self.POLYART_IN and out_fmt in self.IMAGE_OUT:
            return self.polyart_to_image.convert(input_path, output_path)
        else:
            print("[ERROR] Unsupported conversion: {} -> {}".format(in_fmt, out_fmt))
            return None

    def batch_convert(self, input_dir, output_dir, pattern="*"):
        os.makedirs(output_dir, exist_ok=True)
        files = globmod.glob(os.path.join(input_dir, pattern))
        converted = 0
        for fpath in files:
            if not os.path.isfile(fpath):
                continue
            ext = self.get_format(fpath)
            if ext in self.IMAGE_IN:
                out_name = os.path.splitext(os.path.basename(fpath))[0] + ".polyart"
            elif ext in self.POLYART_IN:
                out_name = os.path.splitext(os.path.basename(fpath))[0] + ".png"
            elif ext in self.VIDEO_IN:
                out_name = os.path.splitext(os.path.basename(fpath))[0] + ".polyvid"
            elif ext in self.POLYVID_IN:
                out_name = os.path.splitext(os.path.basename(fpath))[0] + ".gif"
            else:
                print("[SKIP] Unknown format: {}".format(os.path.basename(fpath)))
                continue
            out_path = os.path.join(output_dir, out_name)
            try:
                self.convert(fpath, out_path)
                converted += 1
            except Exception as e:
                print("[ERROR] Failed {}: {}".format(os.path.basename(fpath), str(e)))
        print("[INFO] Batch converted {}/{} files.".format(converted, len(files)))
        return converted

    def info(self, path):
        ext = self.get_format(path)
        print("[INFO] File: {}".format(os.path.basename(path)))
        print("[INFO] Extension: {}".format(ext))
        print("[INFO] Size: {} bytes".format(os.path.getsize(path) if os.path.exists(path) else "N/A"))
        if ext in self.POLYART_IN:
            with open(path) as f:
                data = json.load(f)
            print("[INFO] Format: polyart")
            print("[INFO] Version: {}".format(data.get("version", "unknown")))
            print("[INFO] Dimensions: {}x{}".format(data.get("width", "?"), data.get("height", "?")))
            print("[INFO] Objects: {}".format(len(data.get("objects", []))))
            kinds = {}
            for obj in data.get("objects", []):
                k = obj.get("kind", "unknown")
                kinds[k] = kinds.get(k, 0) + 1
            for k, v in kinds.items():
                print("[INFO]   {}: {}".format(k, v))
            meta = data.get("metadata", {})
            if meta:
                for mk, mv in meta.items():
                    print("[INFO]   {}: {}".format(mk, mv))
        elif ext in self.POLYVID_IN:
            with open(path) as f:
                data = json.load(f)
            print("[INFO] Format: polyvid")
            print("[INFO] Version: {}".format(data.get("version", "unknown")))
            print("[INFO] Dimensions: {}x{}".format(data.get("width", "?"), data.get("height", "?")))
            print("[INFO] FPS: {}".format(data.get("fps", "?")))
            print("[INFO] Frames: {}".format(data.get("frame_count", len(data.get("frames", [])))))
            print("[INFO] Keyframe interval: {}".format(data.get("keyframe_interval", "?")))
            total_objs = sum(len(f.get("objects", [])) for f in data.get("frames", []))
            print("[INFO] Total object references: {}".format(total_objs))
        elif ext in self.IMAGE_IN:
            img = plt.imread(path)
            print("[INFO] Format: raster image")
            print("[INFO] Shape: {}".format(img.shape))
            print("[INFO] Dtype: {}".format(img.dtype))
            print("[INFO] Min/Max: {} / {}".format(img.min(), img.max()))
        else:
            print("[INFO] Format: unknown / unsupported")
        return ext


# =============================================================================
# Utility: generate synthetic test images and video frames
# =============================================================================

def generate_test_image(width=320, height=240):
    img = np.zeros((height, width, 3), dtype=np.uint8)
    xs = np.linspace(0, 1, width)
    ys = np.linspace(0, 1, height)
    fx, fy = np.meshgrid(xs, ys)
    img[:, :, 0] = np.clip(128 + 127 * np.sin(2 * np.pi * fx + fy * 4), 0, 255).astype(np.uint8)
    img[:, :, 1] = np.clip(128 + 127 * np.sin(2 * np.pi * fy + fx * 2), 0, 255).astype(np.uint8)
    img[:, :, 2] = np.clip(128 + 127 * np.cos(2 * np.pi * (fx + fy)), 0, 255).astype(np.uint8)
    cx, cy = width // 2, height // 2
    radius = min(width, height) // 4
    for y in range(max(0, cy - radius), min(height, cy + radius)):
        for x in range(max(0, cx - radius), min(width, cx + radius)):
            if (x - cx) ** 2 + (y - cy) ** 2 < radius ** 2:
                img[y, x] = [255, 255, 255]
    x1, y1 = width // 6, height // 6
    x2, y2 = width * 5 // 6, height * 5 // 6
    for i in range(min(width, height) // 3):
        px = int(x1 + (x2 - x1) * i / max(min(width, height) // 3 - 1, 1))
        py = int(y1 + (y2 - y1) * i / max(min(width, height) // 3 - 1, 1))
        px = max(0, min(width - 1, px))
        py = max(0, min(height - 1, py))
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                ny, nx = py + dy, px + dx
                if 0 <= ny < height and 0 <= nx < width:
                    img[ny, nx] = [0, 200, 100]
    return img


def generate_test_frames(width=160, height=120, n_frames=24):
    frames = []
    for fi in range(n_frames):
        img = np.full((height, width, 3), 40, dtype=np.uint8)
        phase = fi / max(n_frames - 1, 1) * 2 * np.pi
        cx = int(width // 2 + (width // 4) * np.cos(phase))
        cy = int(height // 2 + (height // 4) * np.sin(phase))
        r = 15
        for y in range(max(0, cy - r), min(height, cy + r)):
            for x in range(max(0, cx - r), min(width, cx + r)):
                if (x - cx) ** 2 + (y - cy) ** 2 < r ** 2:
                    img[y, x] = [255, 80, 80]
        sx = int(width // 2 + (width // 6) * np.cos(phase + np.pi))
        sy = int(height // 2 + (height // 6) * np.sin(phase + np.pi))
        sr = 10
        for y in range(max(0, sy - sr), min(height, sy + sr)):
            for x in range(max(0, sx - sr), min(width, sx + sr)):
                if (x - sx) ** 2 + (y - sy) ** 2 < sr ** 2:
                    img[y, x] = [80, 80, 255]
        bx = int(width * (0.1 + 0.8 * (fi / max(n_frames - 1, 1))))
        by = int(height // 2 + 20 * np.sin(fi * 0.5))
        for dy in range(-3, 4):
            py = by + dy
            if 0 <= py < height:
                for dx in range(-5, 6):
                    px = bx + dx
                    if 0 <= px < width:
                        img[py, px] = [50, 255, 50]
        frames.append(img)
    return frames


# =============================================================================
# Main demo / self-test
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  PolyArt Converter - Demo and Self-Test")
    print("=" * 60)

    demo_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "polyart_demo")
    os.makedirs(demo_dir, exist_ok=True)

    # ---- 1. Create test image ----
    print("\n[1/8] Generating test image (320x240 gradient + shapes)...")
    test_img = generate_test_image(320, 240)
    test_img_path = os.path.join(demo_dir, "test_input.png")
    plt.imsave(test_img_path, test_img)
    print("  Saved: {}".format(test_img_path))
    print("  Shape: {}x{}x{}".format(*test_img.shape))

    # ---- 2. Convert to .polyart ----
    print("\n[2/8] Converting test image to .polyart format...")
    converter = FormatConverter()
    polyart_path = os.path.join(demo_dir, "test_output.polyart")
    converter.convert(test_img_path, polyart_path, degree=6, threshold=0.3)
    print("  Saved: {}".format(polyart_path))
    converter.info(polyart_path)

    # ---- 3. Convert .polyart back to PNG ----
    print("\n[3/8] Converting .polyart back to PNG...")
    restored_path = os.path.join(demo_dir, "test_restored.png")
    converter.convert(polyart_path, restored_path, dpi=100)
    print("  Saved: {}".format(restored_path))
    restored_img = plt.imread(restored_path)
    print("  Restored shape: {}".format(restored_img.shape))

    # ---- 4. Create test video frames ----
    print("\n[4/8] Generating test video frames (24 frames, moving shapes)...")
    test_frames = generate_test_frames(160, 120, 24)
    frames_dir = os.path.join(demo_dir, "test_frames")
    os.makedirs(frames_dir, exist_ok=True)
    for i, frame in enumerate(test_frames):
        plt.imsave(os.path.join(frames_dir, "frame_{:03d}.png".format(i)), frame)
    print("  Saved {} frames to {}".format(len(test_frames), frames_dir))

    # ---- 5. Create test .polyvid from frames ----
    print("\n[5/8] Encoding test frames to .polyvid format...")
    vid_converter = VideoToPolyvid()
    polyvid_path = os.path.join(demo_dir, "test_output.polyvid")
    poly_video = vid_converter.encode_frames(test_frames, 160, 120, 12, degree=4, keyframe_interval=6)
    with open(polyvid_path, "w") as f:
        json.dump(poly_video, f, indent=2)
    print("  Saved: {}".format(polyvid_path))
    print("  Frames encoded: {}".format(poly_video["frame_count"]))
    print("  FPS: {}".format(poly_video["fps"]))
    print("  Keyframe interval: {}".format(poly_video["keyframe_interval"]))

    # ---- 6. Convert .polyvid back to GIF ----
    print("\n[6/8] Decoding .polyvid back to GIF...")
    vid_decoder = PolyvidToVideo()
    gif_path = os.path.join(demo_dir, "test_restored.gif")
    vid_decoder.convert(polyvid_path, gif_path, fps=12)
    print("  Saved: {}".format(gif_path))
    if os.path.exists(gif_path):
        print("  GIF size: {} bytes".format(os.path.getsize(gif_path)))

    # ---- 7. Also save decoded frames as individual PNGs ----
    print("\n[7/8] Decoding .polyvid frames to individual PNGs...")
    decoded_frames = vid_decoder.decode_frames(poly_video)
    decoded_dir = os.path.join(demo_dir, "test_decoded_frames")
    vid_decoder.save_frames(decoded_frames, decoded_dir)
    print("  Saved {} decoded frames to {}".format(len(decoded_frames), decoded_dir))

    # ---- 8. Print comparison stats ----
    print("\n[8/8] Comparison Stats:")
    print("-" * 50)

    orig_size = os.path.getsize(test_img_path)
    polyart_size = os.path.getsize(polyart_path)
    restored_size = os.path.getsize(restored_path)
    print("  IMAGE CONVERSION:")
    print("    Original PNG:    {:>10} bytes".format(orig_size))
    print("    PolyArt file:    {:>10} bytes".format(polyart_size))
    print("    Restored PNG:    {:>10} bytes".format(restored_size))
    ratio = polyart_size / max(orig_size, 1)
    print("    PolyArt ratio:   {:>10.2f}x".format(ratio))

    with open(polyart_path) as f:
        polyart_data = json.load(f)
    n_objects = len(polyart_data.get("objects", []))
    total_coeffs = sum(
        len(o.get("x_coeff", [])) + len(o.get("y_coeff", []))
        for o in polyart_data.get("objects", [])
    )
    print("    Poly objects:    {:>10}".format(n_objects))
    print("    Total coeffs:    {:>10}".format(total_coeffs))
    print("")

    vid_orig_size = sum(
        os.path.getsize(os.path.join(frames_dir, "frame_{:03d}.png".format(i)))
        for i in range(len(test_frames))
    )
    polyvid_size = os.path.getsize(polyvid_path)
    gif_size = os.path.getsize(gif_path) if os.path.exists(gif_path) else 0
    print("  VIDEO CONVERSION:")
    print("    Original frames: {:>10} bytes (total PNGs)".format(vid_orig_size))
    print("    PolyVid file:    {:>10} bytes".format(polyvid_size))
    print("    Restored GIF:    {:>10} bytes".format(gif_size))
    v_ratio = polyvid_size / max(vid_orig_size, 1)
    print("    PolyVid ratio:   {:>10.2f}x".format(v_ratio))
    print("    Frames encoded:  {:>10}".format(poly_video["frame_count"]))
    total_frame_objs = sum(len(f.get("objects", [])) for f in poly_video.get("frames", []))
    print("    Total obj refs:  {:>10}".format(total_frame_objs))
    print("")

    # Demo with real file if provided
    if len(sys.argv) >= 2:
        real_input = sys.argv[1]
        if os.path.exists(real_input):
            ext = converter.get_format(real_input)
            print("-" * 50)
            print("  REAL FILE CONVERSION: {}".format(os.path.basename(real_input)))
            if ext in converter.IMAGE_IN:
                out = os.path.join(demo_dir, "converted.polyart")
                converter.convert(real_input, out, degree=6)
                converter.info(out)
                png_out = os.path.join(demo_dir, "reconverted.png")
                converter.convert(out, png_out, dpi=100)
                print("  Reconverted to: {}".format(png_out))
            elif ext in converter.VIDEO_IN:
                out = os.path.join(demo_dir, "converted.polyvid")
                converter.convert(real_input, out, degree=4, max_frames=60)
                converter.info(out)
                gif_out = os.path.join(demo_dir, "reconverted.gif")
                converter.convert(out, gif_out, fps=12)
                print("  Reconverted to: {}".format(gif_out))
            else:
                print("  Unsupported input format: {}".format(ext))
        else:
            print("[ERROR] File not found: {}".format(real_input))

    print("-" * 50)
    print("  All demo files saved to: {}".format(demo_dir))
    print("  Done.")
    print("=" * 60)
