package main

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
	"sort"
	"strconv"
)

type PolyObject struct {
	ID    string                 `json:"id"`
	Kind  string                 `json:"kind"`
	XCoeff []float64             `json:"x_coeff,omitempty"`
	YCoeff []float64             `json:"y_coeff,omitempty"`
	TMin  float64                `json:"t_min"`
	TMax  float64                `json:"t_max"`
	CX    float64                `json:"cx,omitempty"`
	CY    float64                `json:"cy,omitempty"`
	R     float64                `json:"r,omitempty"`
	Style map[string]interface{} `json:"style"`
}

type PolyFrame struct {
	Index    int          `json:"index"`
	Type     string       `json:"type"`
	Width    int          `json:"width"`
	Height   int          `json:"height"`
	Background string     `json:"background"`
	Objects  []PolyObject `json:"objects,omitempty"`
	DeltaFrom int         `json:"delta_from,omitempty"`
	Added    []PolyObject `json:"added,omitempty"`
	Removed  []string     `json:"removed,omitempty"`
	Modified []PolyObject `json:"modified,omitempty"`
}

type PolyVideo struct {
	Format           string     `json:"format"`
	Width            int        `json:"width"`
	Height           int        `json:"height"`
	FPS              int        `json:"fps"`
	TotalFrames      int        `json:"total_frames"`
	KeyframeInterval int        `json:"keyframe_interval"`
	PolynomialDegree int        `json:"polynomial_degree"`
	QuantBits        int        `json:"quant_bits"`
	Frames           []PolyFrame `json:"frames"`
}

func detectEdges(image []float64, w, h int, threshold float64) []bool {
	edges := make([]bool, w*h)
	gx := []float64{-1, 0, 1, -2, 0, 2, -1, 0, 1}
	gy := []float64{-1, -2, -1, 0, 0, 0, 1, 2, 1}
	for y := 1; y < h-1; y++ {
		for x := 1; x < w-1; x++ {
			var sumX, sumY float64
			k := 0
			for dy := -1; dy <= 1; dy++ {
				for dx := -1; dx <= 1; dx++ {
					val := image[(y+dy)*w+(x+dx)]
					sumX += val * gx[k]
					sumY += val * gy[k]
					k++
				}
			}
			mag := math.Sqrt(sumX*sumX + sumY*sumY)
			if mag > threshold {
				edges[y*w+x] = true
			}
		}
	}
	return edges
}

func extractContours(edges []bool, w, h int) [][2]float64 {
	var points [][2]float64
	visited := make([]bool, w*h)
	dirs := [][2]int{{1, 0}, {1, 1}, {0, 1}, {-1, 1}, {-1, 0}, {-1, -1}, {0, -1}, {1, -1}}
	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			if edges[y*w+x] && !visited[y*w+x] {
				cx, cy := x, y
				for {
					visited[cy*w+cx] = true
					points = append(points, [2]float64{float64(cx), float64(cy)})
					found := false
					for _, d := range dirs {
						nx, ny := cx+d[0], cy+d[1]
						if nx >= 0 && nx < w && ny >= 0 && ny < h && edges[ny*w+nx] && !visited[ny*w+nx] {
							cx, cy = nx, ny
							found = true
							break
						}
					}
					if !found {
						break
					}
				}
			}
		}
	}
	return points
}

func polyfit(x, y []float64, degree int) []float64 {
	n := len(x)
	if n == 0 {
		return make([]float64, degree+1)
	}
	if degree >= n {
		degree = n - 1
	}
	m := degree + 1
	xtx := make([][]float64, m)
	xty := make([]float64, m)
	for i := range xtx {
		xtx[i] = make([]float64, m)
	}
	for i := 0; i < n; i++ {
		for p := 0; p < m; p++ {
			for q := 0; q < m; q++ {
				xtx[p][q] += math.Pow(x[i], float64(p+q))
			}
			xty[p] += y[i] * math.Pow(x[i], float64(p))
		}
	}
	coeffs := make([]float64, m)
	aug := make([][]float64, m)
	for i := range aug {
		aug[i] = make([]float64, m+1)
		copy(aug[i], xtx[i])
		aug[i][m] = xty[i]
	}
	for col := 0; col < m; col++ {
		maxRow := col
		for row := col + 1; row < m; row++ {
			if math.Abs(aug[row][col]) > math.Abs(aug[maxRow][col]) {
				maxRow = row
			}
		}
		aug[col], aug[maxRow] = aug[maxRow], aug[col]
		if math.Abs(aug[col][col]) < 1e-12 {
			continue
		}
		pivot := aug[col][col]
		for j := col; j <= m; j++ {
			aug[col][j] /= pivot
		}
		for row := 0; row < m; row++ {
			if row == col {
				continue
			}
			factor := aug[row][col]
			for j := col; j <= m; j++ {
				aug[row][j] -= factor * aug[col][j]
			}
		}
	}
	for i := 0; i < m; i++ {
		coeffs[i] = aug[i][m]
	}
	return coeffs
}

func polyval(coeffs []float64, t float64) float64 {
	result := 0.0
	for i, c := range coeffs {
		result += c * math.Pow(t, float64(i))
	}
	return result
}

func quantize(coeffs []float64, bits int) []int {
	if bits <= 0 {
		bits = 8
	}
	maxVal := float64((1 << uint(bits)) - 1)
	if len(coeffs) == 0 {
		return nil
	}
	absMax := 0.0
	for _, c := range coeffs {
		if math.Abs(c) > absMax {
			absMax = math.Abs(c)
		}
	}
	if absMax < 1e-12 {
		absMax = 1.0
	}
	result := make([]int, len(coeffs))
	for i, c := range coeffs {
		v := (c/absMax + 1.0) / 2.0 * maxVal
		if v < 0 {
			v = 0
		}
		if v > maxVal {
			v = maxVal
		}
		result[i] = int(math.Round(v))
	}
	return result
}

func unquantize(q []int, bits int) []float64 {
	if bits <= 0 {
		bits = 8
	}
	maxVal := float64((1 << uint(bits)) - 1)
	if maxVal == 0 {
		maxVal = 1.0
	}
	result := make([]float64, len(q))
	for i, v := range q {
		result[i] = (float64(v)/maxVal*2.0 - 1.0)
	}
	return result
}

func objectSignature(obj PolyObject) string {
	return obj.ID + ":" + obj.Kind
}

func objectsEqual(a, b PolyObject) bool {
	if a.ID != b.ID || a.Kind != b.Kind {
		return false
	}
	if len(a.XCoeff) != len(b.XCoeff) || len(a.YCoeff) != len(b.YCoeff) {
		return false
	}
	for i := range a.XCoeff {
		if math.Abs(a.XCoeff[i]-b.XCoeff[i]) > 0.01 {
			return false
		}
	}
	for i := range a.YCoeff {
		if math.Abs(a.YCoeff[i]-b.YCoeff[i]) > 0.01 {
			return false
		}
	}
	if math.Abs(a.CX-b.CX) > 0.01 || math.Abs(a.CY-b.CY) > 0.01 || math.Abs(a.R-b.R) > 0.01 {
		return false
	}
	return true
}

func encodeFrame(image []float64, w, h int) PolyFrame {
	frame := PolyFrame{
		Type:  "keyframe",
		Width: w,
		Height: h,
		Background: "black",
	}
	edges := detectEdges(image, w, h, 30.0)
	contours := extractContours(edges, w, h)
	if len(contours) > 10 {
		step := len(contours) / 10
		sampled := [][2]float64{}
		for i := 0; i < len(contours); i += step {
			sampled = append(sampled, contours[i])
		}
		contours = sampled
	}
	objID := 0
	if len(contours) >= 3 {
		xs := make([]float64, len(contours))
		ys := make([]float64, len(contours))
		for i, p := range contours {
			xs[i] = p[0]
			ys[i] = p[1]
		}
		xmin, xmax := xs[0], xs[0]
		for _, v := range xs {
			if v < xmin {
				xmin = v
			}
			if v > xmax {
				xmax = v
			}
		}
		n := len(contours)
		ts := make([]float64, n)
		for i := range ts {
			ts[i] = float64(i) / float64(n-1)
		}
		deg := 3
		if deg >= n {
			deg = n - 1
		}
		xc := polyfit(ts, xs, deg)
		yc := polyfit(ts, ys, deg)
		obj := PolyObject{
			ID:     "contour_" + strconv.Itoa(objID),
			Kind:   "polyline",
			XCoeff: xc,
			YCoeff: yc,
			TMin:   0,
			TMax:   1,
			Style: map[string]interface{}{
				"fill": "none",
				"stroke": "white",
				"stroke_width": 1,
			},
		}
		frame.Objects = append(frame.Objects, obj)
		objID++
	}
	cx := float64(w) / 2.0
	cy := float64(h) / 2.0
	bestR := 0.0
	bestCount := 0
	for r := 10.0; r < float64(w)/2.0; r += 5.0 {
		count := 0
		for y := 0; y < h; y++ {
			for x := 0; x < w; x++ {
				if edges[y*w+x] {
					d := math.Sqrt((float64(x)-cx)*(float64(x)-cx) + (float64(y)-cy)*(float64(y)-cy))
					if math.Abs(d-r) < 3.0 {
						count++
					}
				}
			}
		}
		if count > bestCount {
			bestCount = count
			bestR = r
		}
	}
	if bestCount > 5 {
		obj := PolyObject{
			ID:     "circle_" + strconv.Itoa(objID),
			Kind:   "circle",
			CX:     cx,
			CY:     cy,
			R:      bestR,
			TMin:   0,
			TMax:   1,
			Style: map[string]interface{}{
				"fill":         "none",
				"stroke":       "cyan",
				"stroke_width": 1,
			},
		}
		frame.Objects = append(frame.Objects, obj)
		objID++
	}
	sum := 0.0
	for _, v := range image {
		sum += v
	}
	avg := sum / float64(len(image))
	if avg > 128.0 {
		frame.Background = "white"
	}
	return frame
}

func encodeDelta(prev, curr PolyFrame) PolyFrame {
	delta := PolyFrame{
		Index:     curr.Index,
		Type:      "delta",
		Width:     curr.Width,
		Height:    curr.Height,
		Background: curr.Background,
		DeltaFrom: prev.Index,
	}
	prevSigs := make(map[string]PolyObject)
	for _, obj := range prev.Objects {
		prevSigs[objectSignature(obj)] = obj
	}
	currSigs := make(map[string]PolyObject)
	for _, obj := range curr.Objects {
		currSigs[objectSignature(obj)] = obj
	}
	for _, obj := range curr.Objects {
		sig := objectSignature(obj)
		if prevObj, found := prevSigs[sig]; found {
			if !objectsEqual(obj, prevObj) {
				delta.Modified = append(delta.Modified, obj)
			}
		} else {
			delta.Added = append(delta.Added, obj)
		}
	}
	for _, obj := range prev.Objects {
		sig := objectSignature(obj)
		if _, found := currSigs[sig]; !found {
			delta.Removed = append(delta.Removed, obj.ID)
		}
	}
	if len(delta.Added) == 0 && len(delta.Removed) == 0 && len(delta.Modified) == 0 && delta.Background == prev.Background {
		delta.Background = ""
	}
	return delta
}

func decodeFrame(frame PolyFrame, w, h int) []float64 {
	image := make([]float64, w*h)
	for _, obj := range frame.Objects {
		if obj.Kind == "circle" {
			for y := 0; y < h; y++ {
				for x := 0; x < w; x++ {
					d := math.Sqrt((float64(x)-obj.CX)*(float64(x)-obj.CX) + (float64(y)-obj.CY)*(float64(y)-obj.CY))
					if math.Abs(d-obj.R) < 2.0 {
						idx := y*w + x
						if idx >= 0 && idx < len(image) {
							image[idx] = 255.0
						}
					}
				}
			}
		} else if obj.Kind == "polyline" && len(obj.XCoeff) > 0 && len(obj.YCoeff) > 0 {
			steps := 200
			for i := 0; i < steps; i++ {
				t := obj.TMin + (obj.TMax-obj.TMin)*float64(i)/float64(steps-1)
				px := int(math.Round(polyval(obj.XCoeff, t)))
				py := int(math.Round(polyval(obj.YCoeff, t)))
				if px >= 0 && px < w && py >= 0 && py < h {
					image[py*w+px] = 255.0
				}
				for dx := -1; dx <= 1; dx++ {
					for dy := -1; dy <= 1; dy++ {
						nx, ny := px+dx, py+dy
						if nx >= 0 && nx < w && ny >= 0 && ny < h {
							image[ny*w+nx] = 200.0
						}
					}
				}
			}
		}
	}
	if frame.Background == "white" {
		for i := range image {
			if image[i] == 0 {
				image[i] = 20.0
			}
		}
	}
	return image
}

func reconstructDelta(keyframe, delta PolyFrame) PolyFrame {
	result := PolyFrame{
		Index:     delta.Index,
		Type:      "keyframe",
		Width:     delta.Width,
		Height:    delta.Height,
		Background: delta.Background,
	}
	if result.Background == "" {
		result.Background = keyframe.Background
	}
	existing := make(map[string]PolyObject)
	for _, obj := range keyframe.Objects {
		existing[objectSignature(obj)] = obj
	}
	removedSet := make(map[string]bool)
	for _, id := range delta.Removed {
		removedSet[id] = true
	}
	for _, obj := range delta.Added {
		existing[objectSignature(obj)] = obj
	}
	for _, obj := range delta.Modified {
		existing[objectSignature(obj)] = obj
	}
	for sig, obj := range existing {
		id := obj.ID
		prefix := ""
		if len(id) > 0 {
			underscoreIdx := -1
			for i := len(id) - 1; i >= 0; i-- {
				if id[i] == '_' {
					underscoreIdx = i
					break
				}
			}
			if underscoreIdx >= 0 {
				prefix = id[:underscoreIdx]
			}
		}
		if removedSet[id] || removedSet[prefix] {
			continue
		}
		_ = sig
		result.Objects = append(result.Objects, obj)
	}
	sort.Slice(result.Objects, func(i, j int) bool {
		return result.Objects[i].ID < result.Objects[j].ID
	})
	return result
}

func compress(frames [][]float64, w, h, fps, keyframeInterval, degree int) PolyVideo {
	video := PolyVideo{
		Format:           "polyart/1.0",
		Width:            w,
		Height:           h,
		FPS:              fps,
		TotalFrames:      len(frames),
		KeyframeInterval: keyframeInterval,
		PolynomialDegree: degree,
		QuantBits:        8,
	}
	var prevFrame *PolyFrame
	for i, frameData := range frames {
		kf := encodeFrame(frameData, w, h)
		kf.Index = i
		if prevFrame != nil && i%keyframeInterval != 0 {
			delta := encodeDelta(*prevFrame, kf)
			if len(delta.Added) > 0 || len(delta.Removed) > 0 || len(delta.Modified) > 0 {
				video.Frames = append(video.Frames, delta)
			} else {
				kf.Type = "delta"
				kf.DeltaFrom = prevFrame.Index
				video.Frames = append(video.Frames, kf)
			}
		} else {
			video.Frames = append(video.Frames, kf)
		}
	prevFrame = &video.Frames[len(video.Frames)-1]
		if prevFrame.Type == "delta" {
			recon := reconstructDelta(video.Frames[prevFrame.DeltaFrom], *prevFrame)
			prevFrameCopy := recon
			prevFrame = &prevFrameCopy
		}
	}
	return video
}

func decompress(video PolyVideo) [][]float64 {
	var result [][]float64
	reconstructed := make(map[int]PolyFrame)
	for _, frame := range video.Frames {
		if frame.Type == "keyframe" {
			reconstructed[frame.Index] = frame
			img := decodeFrame(frame, video.Width, video.Height)
			for len(result) <= frame.Index {
				result = append(result, nil)
			}
			result[frame.Index] = img
		}
	}
	for _, frame := range video.Frames {
		if frame.Type == "delta" {
			if kf, ok := reconstructed[frame.DeltaFrom]; ok {
				full := reconstructDelta(kf, frame)
				reconstructed[frame.Index] = full
				img := decodeFrame(full, video.Width, video.Height)
				for len(result) <= frame.Index {
					result = append(result, nil)
				}
				result[frame.Index] = img
			}
		}
	}
	for i := range result {
		if result[i] == nil {
			result[i] = make([]float64, video.Width*video.Height)
		}
	}
	return result
}

func save(video PolyVideo, path string) error {
	data, err := json.MarshalIndent(video, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, data, 0644)
}

func load(path string) (PolyVideo, error) {
	var video PolyVideo
	data, err := os.ReadFile(path)
	if err != nil {
		return video, err
	}
	err = json.Unmarshal(data, &video)
	return video, err
}

func printStats(video PolyVideo) {
	fmt.Println("=== PolyArt Video Codec Stats ===")
	fmt.Println("Format: " + video.Format)
	fmt.Println("Resolution: " + strconv.Itoa(video.Width) + "x" + strconv.Itoa(video.Height))
	fmt.Println("FPS: " + strconv.Itoa(video.FPS))
	fmt.Println("Total Frames: " + strconv.Itoa(video.TotalFrames))
	fmt.Println("Keyframe Interval: " + strconv.Itoa(video.KeyframeInterval))
	fmt.Println("Polynomial Degree: " + strconv.Itoa(video.PolynomialDegree))
	fmt.Println("Quantization Bits: " + strconv.Itoa(video.QuantBits))
	keyframes := 0
	deltas := 0
	totalObjects := 0
	totalAdded := 0
	totalRemoved := 0
	totalModified := 0
	for _, f := range video.Frames {
		if f.Type == "keyframe" {
			keyframes++
			totalObjects += len(f.Objects)
		} else {
			deltas++
			totalAdded += len(f.Added)
			totalRemoved += len(f.Removed)
			totalModified += len(f.Modified)
		}
	}
	fmt.Println("Keyframes: " + strconv.Itoa(keyframes))
	fmt.Println("Delta Frames: " + strconv.Itoa(deltas))
	fmt.Println("Total Objects (keyframes): " + strconv.Itoa(totalObjects))
	fmt.Println("Delta Additions: " + strconv.Itoa(totalAdded))
	fmt.Println("Delta Removals: " + strconv.Itoa(totalRemoved))
	fmt.Println("Delta Modifications: " + strconv.Itoa(totalModified))
	flatSize := video.Width * video.Height * video.TotalFrames * 8
	fmt.Println("Raw flat size (approx): " + strconv.Itoa(flatSize) + " bytes")
	data, _ := json.Marshal(video)
	compressedSize := len(data)
	fmt.Println("Compressed size: " + strconv.Itoa(compressedSize) + " bytes")
	if flatSize > 0 {
		ratio := float64(compressedSize) / float64(flatSize) * 100.0
		fmt.Println("Compression ratio: " + fmt.Sprintf("%.2f", ratio) + "%")
	}
}

func main() {
	fmt.Println("PolyArt Video Codec v1.0")
	fmt.Println("========================")
	fmt.Println("Generating test frames...")
	const w = 120
	const h = 90
	const fps = 10
	const numFrames = 10
	const keyframeInterval = 3
	const degree = 3
	frames := make([][]float64, numFrames)
	for i := 0; i < numFrames; i++ {
		frames[i] = make([]float64, w*h)
		t := float64(i) / float64(numFrames-1)
		circleX := 30.0 + t*60.0
		circleY := 45.0 + math.Sin(t*math.Pi*2)*20.0
		circleR := 8.0
		for y := 0; y < h; y++ {
			for x := 0; x < w; x++ {
				d := math.Sqrt((float64(x)-circleX)*(float64(x)-circleX) + (float64(y)-circleY)*(float64(y)-circleY))
				if math.Abs(d-circleR) < 1.5 {
					frames[i][y*w+x] = 255.0
				}
			}
		}
		lineAngle := t * math.Pi * 2
		lineLen := 20.0
		for s := 0.0; s <= 1.0; s += 0.02 {
			lx := 60.0 + math.Cos(lineAngle)*lineLen*s
			ly := 45.0 + math.Sin(lineAngle)*lineLen*s
			ix, iy := int(math.Round(lx)), int(math.Round(ly))
			if ix >= 0 && ix < w && iy >= 0 && iy < h {
				frames[i][iy*w+ix] = 200.0
			}
			ix2, iy2 := int(math.Round(60.0-math.Cos(lineAngle)*lineLen*s)), int(math.Round(45.0-math.Sin(lineAngle)*lineLen*s))
			if ix2 >= 0 && ix2 < w && iy2 >= 0 && iy2 < h {
				frames[i][iy2*w+ix2] = 200.0
			}
		}
		rectCX := 60.0 + math.Sin(t*math.Pi*4)*15.0
		rectCY := 45.0
		rectW := 12.0
		rectH := 8.0 + math.Sin(t*math.Pi*3)*4.0
		for y := int(rectCY - rectH/2); y <= int(rectCY+rectH/2); y++ {
			for x := int(rectCX - rectW/2); x <= int(rectCX+rectW/2); x++ {
				if x >= 0 && x < w && y >= 0 && y < h {
					edge := (x == int(rectCX-rectW/2) || x == int(rectCX+rectW/2) || y == int(rectCY-rectH/2) || y == int(rectCY+rectH/2))
					if edge {
						frames[i][y*w+x] = 180.0
					}
				}
			}
		}
	}
	fmt.Println("Generated " + strconv.Itoa(numFrames) + " test frames (" + strconv.Itoa(w) + "x" + strconv.Itoa(h) + ")")
	fmt.Println("Encoding video...")
	video := compress(frames, w, h, fps, keyframeInterval, degree)
	fmt.Println("Encoded " + strconv.Itoa(len(video.Frames)) + " compressed frames")
	fmt.Println("Decoding video...")
	decoded := decompress(video)
	fmt.Println("Decoded " + strconv.Itoa(len(decoded)) + " frames")
	printStats(video)
	fmt.Println("")
	fmt.Println("Saving to demo.polyvid...")
	err := save(video, "demo.polyvid")
	if err != nil {
		fmt.Println("Error saving: " + err.Error())
	} else {
		fmt.Println("Saved demo.polyvid successfully")
	}
	fmt.Println("")
	fmt.Println("Reloading and verifying...")
	loaded, err := load("demo.polyvid")
	if err != nil {
		fmt.Println("Error loading: " + err.Error())
	} else {
		fmt.Println("Loaded " + strconv.Itoa(len(loaded.Frames)) + " frames from file")
	}
	fmt.Println("")
	fmt.Println("PolyArt codec demo complete!")
}
