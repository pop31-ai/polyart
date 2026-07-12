# PolyArt Project Registry

> Complete catalog of all files, classes, methods, and resources in the PolyArt ecosystem.

**Version:** 2.1.0 | **Generated:** 2026-07-12 | **Total Files:** 269 | **Total Size:** 42.3 MB

---

## Table of Contents

1. [Python Modules](#1-python-modules)
2. [Format Specifications](#2-format-specifications)
3. [Codec Implementations](#3-codec-implementations)
4. [Articles & Documentation](#4-articles--documentation)
5. [Reference Documents](#5-reference-documents)
6. [Multilingual Articles](#6-multilingual-articles)
7. [Showcase Images & Media](#7-showcase-images--media)
8. [Video Content](#8-video-content)
9. [Demo Outputs](#9-demo-outputs)
10. [Configuration Files](#10-configuration-files)
11. [Project Statistics](#11-project-statistics)

---

## 1. Python Modules

### polyart_api.py — Core API
- **Lines:** 1,241 | **Size:** 56,786 bytes
- **Dependencies:** numpy, matplotlib
- **Description:** Core polynomial art engine. Canvas, PolyObj, GreekLines, RomanLines, GoldenRatio, SuperFormula, Templates.

| Class | Methods |
|-------|---------|
| **GreekLines** | `meander_segment`, `meander`, `meander_single_poly`, `volute`, `lotus`, `palmette`, `acanthus_leaf`, `column_flute`, `greek_key_border` |
| **RomanLines** | `arch`, `column`, `dome`, `vault`, `triumphal_arch` |
| **GoldenRatio** | `phi`, `fibonacci`, `golden_spiral_b`, `golden_spiral`, `golden_rectangle`, `golden_triad`, `face_proportions`, `body_proportions` |
| **PolyCoeffs** | `line`, `parabola`, `cubic`, `ellipse_poly`, `circle_poly`, `spiral_poly`, `wave`, `heart`, `lissajous`, `from_points`, `closed_polygon`, `scale`, `translate` |
| **SuperFormula** | `flower`, `star`, `circle`, `square`, `cross`, `blob`, `custom` |
| **PolyObj** | `to_dict` |
| **Layer** | `add`, `to_dict` |
| **Canvas** | `add_layer`, `layer`, `add_formula`, `add`, `line`, `polyline`, `ellipse`, `circle`, `spiral`, `wave`, `heart`, `lissajous`, `star`, `flower`, `blob`, `superformula`, `polygon`, `meander`, `arch`, `golden_spiral`, `golden_rectangle`, `volute`, `save`, `load`, `from_file`, `render`, `info` |
| **Templates** | `apollo_face`, `rose`, `greek_vase`, `parthenon`, `roman_arch`, `golden_composition`, `geometric_tile` |

---

### polyart_format.py — File Format
- **Lines:** 427 | **Size:** 17,452 bytes
- **Dependencies:** json (stdlib)
- **Description:** .polyart JSON format save/load/render.

| Function | Purpose |
|----------|---------|
| `make_object` | Create a polynomial object |
| `make_fill_object` | Create a filled polygon object |
| `make_circle` | Create a circle object |
| `make_ellipse` | Create an ellipse object |
| `make_spiral` | Create a spiral object |
| `make_superformula` | Create a superformula object |
| `make_polygon_poly` | Create a polygon from vertices |
| `save_polyart` | Write .polyart file |
| `load_polyart` | Read .polyart file |
| `render_polyart` | Render to matplotlib |
| `demo_create_polyart` | Demo function |

---

### polyart_editor.py — Visual Editor
- **Lines:** 767 | **Size:** 37,306 bytes
- **Dependencies:** tkinter, matplotlib, numpy
- **Description:** tkinter-based visual editor with layers, presets, undo/redo.

| Class | Methods |
|-------|---------|
| **PolyartEditor** | `_build_ui`, `_push_undo`, `new_file`, `open_file`, `save_file`, `save_as`, `undo`, `redo`, `add_layer`, `del_layer`, `add_object`, `del_object`, `dup_object`, `obj_up`, `obj_down`, `add_preset`, `_apply_prop`, `_current_obj`, `_load_obj_to_props`, `_update_all`, `_update_layer_list`, `_update_obj_list`, `_update_meta_fields`, `_apply_meta`, `_on_layer_select`, `_on_obj_select`, `_pick_color`, `_pick_fill_color`, `_bind_keys`, `render`, `_draw_object` |

---

### polyart_viewer.py — Viewer
- **Lines:** 288 | **Size:** 14,176 bytes
- **Dependencies:** tkinter, matplotlib
- **Description:** Lightweight .polyart file viewer with layer tree and export.

| Class | Methods |
|-------|---------|
| **PolyartViewer** | `_build_ui`, `_bind_keys`, `open_file`, `_update_info`, `_update_tree`, `_update_formulas`, `_on_select`, `render`, `_draw_object`, `export_png`, `refresh` |

---

### polyart_emotions.py — Emotion Templates
- **Lines:** 592 | **Size:** 30,271 bytes
- **Dependencies:** numpy, matplotlib
- **Description:** 10 emotion expressions + 4 physical states rendered in polynomial style.

| Class | Methods |
|-------|---------|
| **EmotionTemplates** | `joy`, `sorrow`, `anger`, `fear`, `love`, `surprise`, `calm`, `pride`, `exhaustion`, `determination` |
| **StateTemplates** | `sleeping`, `running`, `thinking`, `dancing` |
| **MockCanvas** | `add`, `line`, `circle`, `text` |

---

### polyart_animals.py — Animal Templates
- **Lines:** 468 | **Size:** 23,355 bytes
- **Dependencies:** numpy, matplotlib
- **Description:** 9 animal forms rendered as polynomial curves.

| Class | Methods |
|-------|---------|
| **AnimalTemplates** | `lion`, `eagle`, `wolf`, `horse`, `snake`, `bear`, `dolphin`, `owl`, `dragon` |
| **MockCanvas** | `add`, `line`, `circle` |

---

### polyart_biology.py — Biological Patterns
- **Lines:** 755 | **Size:** 35,499 bytes
- **Dependencies:** numpy, matplotlib
- **Description:** Growth curves, phyllotaxis, biomechanics, Turing patterns, variant generation.

| Class | Methods |
|-------|---------|
| **GrowthCurves** | `logistic`, `logistic_poly`, `von_bertalanffy`, `von_bertalanffy_poly`, `power_allometry`, `allometric_poly`, `gompertz`, `gompertz_poly`, `diffuse_growth` |
| **Phyllotaxis** | `golden_points`, `fibonacci_spiral`, `leaf_shape`, `petal_shape`, `flower_radial`, `branching_tree`, `vein_network` |
| **Biomechanics** | `joint_envelope`, `bone_profile`, `tendon_line`, `muscle_force_vector`, `spine_curve`, `rib_profile`, `pelvis_profile`, `scapula_outline`, `wolff_bone_adapt` |
| **TuringPatterns** | `spot_pattern`, `stripe_pattern`, `spiral_pattern`, `voronoi_cells`, `hexagonal_packing` |
| **VariantGenerator** | `vary_params`, `generate_leaf_variants`, `generate_flower_variants`, `generate_tree_variants`, `generate_bone_variants`, `generate_skin_texture` |
| **BioScenes** | `growth_study`, `anatomy_biomech`, `turing_study`, `variant_showcase` |

---

### polyart_sculpture.py — Sculpture & Architecture
- **Lines:** 737 | **Size:** 37,346 bytes
- **Dependencies:** numpy, matplotlib
- **Description:** Lathe body generation, muscle relief, Piranesi architecture, Roman symbols, game assets.

| Class | Methods |
|-------|---------|
| **LatheBody** | `amphora`, `column_fluted`, `human_torso`, `greek_krater`, `oinochoe`, `render_lathe` |
| **MuscleRelief** | `torso_front`, `arm_relief`, `leg_relief`, `render_muscles` |
| **PiranesiArch** | `arch`, `staircase`, `colonnade`, `vault`, `impossible_stairs`, `render_piranesi` |
| **RomanSymbols** | `eagle`, `laurel_wreath`, `spqr_banner`, `gladius`, `shield` |
| **GameAssets** | `character_sprite`, `tilemap`, `health_bar`, `minimap`, `compass_rose`, `tree`, `render_game_assets` |
| **SculptureScenes** | `roman_gallery`, `piranesi_scene`, `anatomy_study`, `game_demo` |

---

### polyart_3d.py — 3D Rendering
- **Lines:** 418 | **Size:** 17,902 bytes
- **Dependencies:** numpy, matplotlib
- **Description:** 3D wireframe and surface rendering with rotation, lighting, projection.

| Class | Methods |
|-------|---------|
| **Rotations** | `rotate_x`, `rotate_y`, `rotate_z`, `rotate_all` |
| **Wireframe3D** | `sphere`, `cube`, `cylinder`, `torus`, `icosahedron`, `dodecahedron`, `heightfield`, `parametric_surface`, `moebius_strip`, `klein_bottle` |
| **Surface3D** | (inherits wireframe rendering) |
| **Scene3D** | `add_wireframe`, `add_surface`, `add_light`, `_compute_alpha`, `render_to_canvas` |
| **Demo3D** | `geometric_primitives`, `mathematical_surfaces`, `spqr_3d` |

---

### polyart_cv_test.py — Computer Vision
- **Lines:** 539 | **Size:** 23,338 bytes
- **Dependencies:** numpy, matplotlib
- **Description:** Art vs nature classification, rarity scoring, feature extraction.

| Class | Methods |
|-------|---------|
| **ImageFeatureExtractor** | `color_histogram`, `edge_density`, `symmetry_score`, `fractal_dimension`, `texture_complexity`, `color_diversity`, `golden_ratio_score`, `polynomial_smoothness`, `curvature_energy`, `extract_all` |
| **RarityScorer** | `compute_rarity`, `classify`, `generate_report` |
| **PolyArtCVTest** | `analyze_image`, `batch_analyze`, `generate_synthetic_test`, `draw_tri`, `run_demo` |

---

### polyart_lang.py — Meta-Language DSL
- **Lines:** 899 | **Size:** 40,821 bytes
- **Dependencies:** numpy, matplotlib
- **Description:** Complete DSL with tokenizer, parser, interpreter. 50+ built-in commands for drawing, emotions, animals, states.

| Class | Methods |
|-------|---------|
| **Token** | `__init__`, `__repr__` |
| **ASTNode** | (base) |
| **CommandNode** | (AST: command with args) |
| **AssignNode** | (AST: variable assignment) |
| **BinOpNode** | (AST: binary operation) |
| **UnaryOpNode** | (AST: unary operation) |
| **NumberNode** | (AST: numeric literal) |
| **StringNode** | (AST: string literal) |
| **VarNode** | (AST: variable reference) |
| **LoopNode** | (AST: repeat loop) |
| **IfNode** | (AST: conditional) |
| **FuncDefNode** | (AST: function definition) |
| **FuncCallNode** | (AST: function call) |
| **ListNode** | (AST: list literal) |
| **Parser** | `peek`, `advance`, `expect`, `parse`, `parse_statement`, `parse_loop`, `parse_if`, `parse_func_def`, `parse_assign`, `parse_command`, `parse_condition`, `parse_expr`, `parse_additive`, `parse_multiplicative`, `parse_unary`, `parse_primary` |
| **Interpreter** | `run`, `exec_node`, `exec_node_list`, `eval_expr`, `eval_condition`, `call_func`, `exec_command`, `builtin`, `_draw_emotion`, `_emotion_joy`, `_emotion_sorrow`, `_emotion_anger`, `_emotion_fear`, `_emotion_love`, `_emotion_surprise`, `_emotion_calm`, `_emotion_pride`, `_draw_animal`, `_animal_lion`, `_animal_eagle`, `_animal_wolf`, `_animal_horse`, `_animal_snake`, `_animal_bear`, `_animal_dolphin`, `_animal_owl`, `_animal_dragon`, `_draw_state` |

| Standalone | Purpose |
|------------|---------|
| `tokenize` | Lexical tokenizer |
| `run_source` | Execute DSL source string |
| `run_file` | Execute DSL file |

---

### polyart_curves.py — Body System Curves
- **Lines:** 600 | **Size:** 29,912 bytes
- **Dependencies:** numpy, matplotlib
- **Description:** Complete atlas of polynomial curves for all human body systems.

| Class | Methods |
|-------|---------|
| **SkeletalCurves** | `skull`, `spine`, `ribcage`, `pelvis`, `long_bone`, `hand_skeleton`, `foot_skeleton` |
| **MuscleCurves** | `bicep`, `quadricep`, `pectoral`, `deltoid`, `abdominal`, `calf`, `gluteus` |
| **SkinCurves** | `face_contour`, `wrinkle_lines`, `skin_texture_stipple`, `neck_skin`, `ear_contour` |
| **VeinCurves** | `arm_veins`, `leg_veins`, `heart_vessels`, `capillary_network` |
| **NerveCurves** | `nerve_fiber`, `brain_network`, `spinal_nerve`, `dendrite` |
| **LimbCurves** | `arm_contour`, `leg_contour`, `hand_contour`, `foot_contour`, `shoulder` |
| **HeadCurves** | `head_shape`, `eye`, `nose`, `mouth`, `eyebrow`, `hair_strands` |
| **FigureCurves** | `full_body_front`, `full_body_side`, `seated_figure` |
| **NeckCurves** | `_draw_neck` |

---

### polyart_flowers.py — Botanical Art
- **Lines:** 813 | **Size:** 41,479 bytes
- **Dependencies:** numpy, matplotlib
- **Description:** Flower renderers, plant curves, full compositions. 17 flower species + plants + scenes.

| Class | Methods |
|-------|---------|
| **FlowerCurves** | `rose`, `lily`, `daisy`, `tulip`, `sunflower`, `orchid`, `lotus`, `chrysanthemum`, `peony`, `hibiscus`, `lavender`, `forget_me_not`, `cherry_blossom`, `cactus_flower`, `camellia`, `pansy`, `snowdrop` |
| **PlantCurves** | `vine`, `branch`, `fern`, `grass`, `tree_canopy`, `cactus`, `bonsai`, `succulent`, `mushroom`, `seaweed` |
| **CompositionCurves** | `bouquet`, `garden_scene`, `wreath`, `floral_border`, `terrarium`, `ikebana`, `flower_crown`, `vertical_garden`, `forest_floor` |

---

### polyart_spqr.py — Roman Architecture & Piranesi
- **Lines:** 836 | **Size:** 45,976 bytes
- **Dependencies:** numpy, matplotlib
- **Description:** SPQR Roman architecture: classical orders, arches, Piranesi impossible geometry, Roman forum, Colosseum.

| Class | Methods |
|-------|---------|
| **RomanOrders** | `doric_column`, `ionic_column`, `corinthian_column` |
| **RomanArch** | `semicircular_arch`, `pointed_arch`, `aqueduct_segment`, `triumphal_arch` |
| **PiranesiArchitecture** | `infinite_staircase`, `impossible_corridor`, `spiral_tower`, `nested_arches` |
| **SPQRForum** | `temple`, `colosseum_wall`, `pantheon_dome`, `forum_pillars` |
| **SPQRComposition** | `piranesi_prison`, `roman_city`, `spqr_glory` |

---

### polyart_converter.py — Format Converter
- **Lines:** 760 | **Size:** 34,745 bytes
- **Dependencies:** numpy, matplotlib, PIL
- **Description:** Bidirectional converter: images ↔ .polyart, videos ↔ .polyvid.

| Class | Methods |
|-------|---------|
| **ImageToPolyart** | `load_image`, `extract_edges`, `extract_contours`, `fit_polynomials`, `extract_colors`, `image_to_polyart`, `convert` |
| **PolyartToImage** | `load_polyart`, `render_polyobject`, `render_frame`, `convert` |
| **VideoToPolyvid** | `load_video_frames`, `encode_frames`, `convert` |
| **PolyvidToVideo** | `load_polyvid`, `decode_frames`, `save_gif`, `save_frames`, `convert` |
| **FormatConverter** | `get_format`, `convert`, `batch_convert`, `info` |

---

### polyart_video_codec.py — Video Codec
- **Lines:** 685 | **Size:** 29,520 bytes
- **Dependencies:** numpy, matplotlib
- **Description:** Video encoding/decoding with polynomial compression, delta frames, interpolation.

| Class | Methods |
|-------|---------|
| **PolyObject** | `to_dict`, `from_dict` |
| **PolyFrame** | `add_object`, `to_dict`, `from_dict` |
| **PolyVideoEncoder** | `detect_edges`, `extract_contours`, `fit_polynomial`, `quantize_curve`, `dequantize_curve`, `sample_color`, `encode_frame`, `encode_delta`, `read_image`, `create_demo_frames`, `encode_video` |
| **PolyVideoDecoder** | `render_polyobject`, `decode_frame`, `decode_video`, `interpolate_frame` |
| **PolyVideoCodec** | `compress`, `decompress`, `get_stats` |
| **PolyVideoPlayer** | `play`, `preview` |

---

### polyart_videos.py — Video Generation
- **Lines:** 541 | **Size:** 21,405 bytes
- **Dependencies:** numpy, matplotlib
- **Description:** 20 animated GIF generators: golden spiral, flower bloom, Turing patterns, DNA helix, fractal trees, etc.

| Function | Description |
|----------|-------------|
| `video_golden_spiral` | Golden spiral animation |
| `video_flower_bloom` | Flower blooming sequence |
| `video_column_build` | Roman column construction |
| `video_piranesi_stairs` | Impossible staircase loop |
| `video_turing_pattern` | Reaction-diffusion evolution |
| `video_dna_helix` | DNA double helix rotation |
| `video_fractal_tree` | Fractal branching growth |
| `video_mandala_spin` | Rotating mandala |
| `video_wave_interference` | Wave interference pattern |
| `video_particle_burst` | Particle burst animation |
| `video_sorting` | Sorting algorithm visualization |
| `video_cell_divide` | Cell division animation |
| `video_morph_polygon` | Polygon morphing |
| `video_constellation` | Star constellation drawing |
| `video_heartbeat` | ECG heartbeat trace |
| `video_ecosystem` | Ecosystem simulation |
| `video_neural_pulse` | Neural pulse propagation |
| `video_orbits` | Orbital mechanics |
| `video_crystal_grow` | Crystal growth animation |
| `video_title_sequence` | Title sequence animation |

---

### Standalone Python Scripts (non-module)

| File | Lines | Description |
|------|-------|-------------|
| `amphora_art.py` | 436 | Greek amphora art with meander bands and palmettes |
| `ancient_art.py` | 155 | Ancient Greek architectural art (columns, olive branches) |
| `apollonian_faces.py` | 474 | Apollonian gasket faces and profiles |
| `caricature.py` | 340 | Polynomial caricature generator |
| `cv_check_emperor.py` | 11 | Quick CV check on emperor image |
| `cv_verify_all.py` | 135 | Batch CV verification of all showcase images |
| `cv_verify_new.py` | 37 | CV verification of new images |
| `emperor_caricature.py` | 383 | Roman emperor caricature generator |
| `emperor_portrait.py` | 475 | Roman emperor polynomial portrait |
| `lines_composition.py` | 65 | Line composition demo |
| `porcelain_art.py` | 324 | Chinese porcelain art style |
| `vitruvian_da_vinci.py` | 397 | Vitruvian Man polynomial recreation |
| `weary_emperor.py` | 428 | Weary Roman emperor portrait |

---

## 2. Format Specifications

### .polyart — Image Format
- **Extension:** `.polyart`
- **Structure:** JSON
- **Files in project:** 16

```
{
  "format": "polyart/1.0",
  "canvas": {
    "name": string,        // Project name
    "width": float,        // Width in inches
    "height": float,       // Height in inches
    "background": string   // Hex color
  },
  "layers": [{
    "name": string,
    "visible": boolean,
    "objects": [{
      "kind": string,      // "polyline"|"circle"|"polygon"|"fill"
      "id": string,
      "params": {
        "x": [float],     // Polynomial coefficients for x(t)
        "y": [float],     // Polynomial coefficients for y(t)
        "t_min": float,
        "t_max": float,
        "cx": float,       // For circles
        "cy": float,
        "r": float
      },
      "style": {
        "color": string,   // Hex color
        "linewidth": float,
        "alpha": float,
        "fill": boolean,
        "fill_color": string,
        "fill_alpha": float
      }
    }]
  }],
  "formulas": [string]     // Optional LaTeX formulas
}
```

### .polyvid — Video Format
- **Extension:** `.polyvid`
- **Structure:** JSON
- **Files in project:** 3

```
{
  "format": "polyvid/1.0",
  "width": int,             // Frame width in pixels
  "height": int,            // Frame height in pixels
  "fps": float,             // Frames per second
  "frame_count": int,
  "background": string,     // Hex color
  "frames": [{
    "index": int,
    "type": "keyframe"|"delta",
    "objects": [{            // Same object structure as .polyart
      "kind": string,
      "params": {},
      "style": {}
    }]
  }]
}
```

---

## 3. Codec Implementations

| Language | File | Lines | Size | Dependencies |
|----------|------|-------|------|--------------|
| **C++** | `codec_cpp/polyart_codec.h` | 1,113 | 53,923 B | `<vector>`, `<string>`, `<map>`, `<fstream>`, `<cmath>` (stdlib only) |
| **C++** | `codec_cpp/main.cpp` | 152 | 6,686 B | `polyart_codec.h` |
| **Go** | `codec_go/main.go` | 683 | 18,090 B | `encoding/json`, `math`, `os`, `sort` (stdlib only) |
| **Java** | `codec_java/PolyArtCodec.java` | 445 | 19,548 B | `java.io`, `java.util` (JDK only) |
| **JavaScript** | `codec_javascript/polyart_codec.js` | 742 | 29,230 B | `fs`, `path` (Node.js stdlib only) |
| **Python** | `polyart_video_codec.py` | 685 | 29,520 B | numpy, matplotlib |

- **C++ compiled binary:** `codec_cpp/polyart_codec.exe` (16.7 MB)
- **C++ test output:** `codec_cpp/output.polyvid` (14,544 bytes)

All codec implementations are self-contained with zero external dependencies beyond their language's standard library (Python codec additionally uses numpy/matplotlib).

---

## 4. Articles & Documentation

### Technical Articles (articles/)

| # | File | Topic | Words |
|---|------|-------|-------|
| 13 | `13_flowers_in_math.txt` | Mathematical beauty of flowers | 1,151 |
| 14 | `14_meta_language_design.txt` | Designing a DSL for mathematical art | 858 |
| 15 | `15_curves_of_the_body.txt` | Polynomial curves of the human body | 1,140 |
| 16 | `16_piranesi_impossible.txt` | Impossible architecture through polynomials | 1,065 |
| 17 | `17_emotion_mathematics.txt` | Mathematics of emotion | 1,126 |
| 18 | `18_animal_polynomials.txt` | Animal forms through polynomial lenses | 1,129 |
| 19 | `19_cv_art_classification.txt` | Computer vision for mathematical art | 1,115 |
| 20 | `20_3d_polynomialRendering.txt` | 3D polynomial rendering | 884 |
| 21 | `21_biological_patterns.txt` | Turing patterns to polynomial forms | 1,031 |
| 22 | `22_sculpture_lathe.txt` | Polynomial lathe sculpture | 1,067 |
| 23 | `23_golden_ratio_everywhere.txt` | Golden ratio as universal aesthetic principle | 1,949 |
| 24 | `24_color_theory_polynomials.txt` | Polynomial color harmonies | 2,073 |
| 25 | `25_spqr_architecture.txt` | SPQR Roman architectural orders | 2,075 |
| 26 | `26_parametric_polynomial_hybrid.txt` | Hybrid parametric-polynomial curves | 1,943 |
| 27 | `27_procedural_game_worlds.txt` | Procedural world generation | 1,799 |
| 28 | `28_neural_art_bridge.txt` | Neural-symbolic bridge for art | 1,861 |
| 29 | `29_symmetry_groups_polynomials.txt` | Symmetry groups and polynomial art | 2,087 |
| 30 | `30_medieval_manuscript_polyart.txt` | Medieval manuscript illumination | 2,083 |
| 31 | `31_kinetic_mathematical_art.txt` | Kinetic mathematical art | 2,022 |
| 32 | `32_future_polyart.txt` | The future of polynomial art | 2,314 |

### Codec Articles (articles/)

| File | Topic | Words |
|------|-------|-------|
| `codec_algorithms.txt` | Codec encoding/decoding algorithms | 1,869 |
| `codec_applications.txt` | Real-world codec applications | 1,966 |
| `codec_comparison.txt` | Codec comparison with existing formats | 2,552 |
| `codec_compression.txt` | Compression techniques analysis | 1,875 |
| `codec_specification.txt` | PolyArt video codec specification | 1,527 |

### Foundational Articles (articles/*.md)

| File | Topic | Words |
|------|-------|-------|
| `ancient_greek_geometry.md` | Ancient Greek geometry in modern art | 865 |
| `art_classification_cv.md` | Computer vision for art classification | 1,187 |
| `biological_patterns.md` | Biological pattern generation | 778 |
| `color_theory_mathematical.md` | Mathematical color theory | 887 |
| `format_specification.md` | .polyart format specification | 793 |
| `game_asset_generation.md` | Procedural game asset generation | 1,040 |
| `golden_ratio_in_art.md` | Golden ratio as generative principle | 656 |
| `neural_symbolic_hybrid.md` | Neural-symbolic hybrid classification | 894 |
| `parametric_vs_polynomial.md` | Parametric vs polynomial curves | 921 |
| `piranesi_architecture.md` | Impossible architecture through curves | 785 |
| `polynomial_approximation_theory.md` | Polynomial approximation theory | 739 |
| `procedural_texture_synthesis.md` | Procedural texture synthesis | 1,083 |

**Total articles: 37 | Total words: ~51,189**

---

## 5. Reference Documents

| Ref | File | Title | Topics Covered |
|-----|------|-------|----------------|
| 01 | `docs/REF01_Core_API.txt` | Core API | Canvas constructor, PolyObj, rendering, save/load |
| 02 | `docs/REF02_File_Format.txt` | File Format | .polyart JSON structure, fields, object kinds |
| 03 | `docs/REF03_Editor.txt` | Visual Editor | Interface layout, keyboard shortcuts, presets |
| 04 | `docs/REF04_Viewer.txt` | Viewer | Launch, navigation, layer tree, export |
| 05 | `docs/REF05_Emotions.txt` | Emotions & States | EmotionTemplates methods, StateTemplates, parameters |
| 06 | `docs/REF06_Animals.txt` | Animal Templates | AnimalTemplates methods, all 9 animals, parameters |
| 07 | `docs/REF07_Biology.txt` | Biology & Growth | GrowthCurves, Phyllotaxis, Biomechanics, TuringPatterns |
| 08 | `docs/REF08_Curves_Library.txt` | Curves Library | SkeletalCurves, MuscleCurves, SkinCurves, all body systems |
| 09 | `docs/REF09_Botanical.txt` | Botanical & Flower Art | FlowerCurves (17 species), PlantCurves, CompositionCurves |
| 10 | `docs/REF10_SPQR_Architecture.txt` | SPQR Architecture | RomanOrders, RomanArch, PiranesiArchitecture, SPQRForum |

---

## 6. Multilingual Articles

### Article 01: Mathematical Beauty of Flowers

| Language | File | Words |
|----------|------|-------|
| English | `articles/multilang/01_flowers_en.txt` | 1,197 |
| German | `articles/multilang/01_flowers_de.txt` | 1,181 |
| Spanish | `articles/multilang/01_flowers_es.txt` | 1,328 |
| Russian | `articles/multilang/01_flowers_ru.txt` | 1,112 |
| Chinese | `articles/multilang/01_flowers_zh.txt` | 1,144 |

### Article 02: SPQR Roman Architecture

| Language | File | Words |
|----------|------|-------|
| English | `articles/multilang/02_spqr_architecture_en.txt` | 2,088 |
| German | `articles/multilang/02_spqr_architecture_de.txt` | 1,943 |
| Spanish | `articles/multilang/02_spqr_architecture_es.txt` | 2,284 |
| Russian | `articles/multilang/02_spqr_architecture_ru.txt` | 1,852 |
| Chinese | `articles/multilang/02_spqr_architecture_zh.txt` | 745 |

**Languages: 5 (EN, DE, ES, RU, ZH) | Total multilingual words: ~14,774**

---

## 7. Showcase Images & Media

### Generated PNG Images (root level)

| File | Size | Content |
|------|------|---------|
| `amphora_art.png` | 460 KB | Greek amphora with meander and palmette decoration |
| `animals_showcase.png` | 225 KB | 9 polynomial animal forms showcase |
| `apollonian_faces.png` | 755 KB | Apollonian gasket face renderings |
| `apollo_polyart_render.png` | 383 KB | Apollo face polynomial render |
| `bio_biomech.png` | 127 KB | Biomechanical atlas (bones, joints, tendons) |
| `bio_growth.png` | 83 KB | Biological growth curves and phyllotaxis |
| `bio_turing.png` | 634 KB | Turing pattern generation (spots, stripes) |
| `bio_variants.png` | 273 KB | Biological variant showcase |
| `caricature.png` | 271 KB | Polynomial caricature |
| `comparison.png` | 31 KB | Format comparison image |
| `curves_library_showcase.png` | 292 KB | Body curves library showcase |
| `demo_composition.png` | 140 KB | Composition demo |
| `demo_emotions_lang.png` | 52 KB | Emotions via meta-language |
| `demo_geometric_primitives.png` | 335 KB | 3D geometric primitives |
| `demo_mandala_lang.png` | 397 KB | Mandala via meta-language |
| `demo_mathematical_surfaces.png` | 148 KB | Mathematical surface rendering |
| `demo_mythology_lang.png` | 157 KB | Mythology via meta-language |
| `demo_rose.png` | 224 KB | Rose polynomial render |
| `demo_spqr_3d.png` | 355 KB | SPQR 3D architectural scene |
| `emotions_showcase.png` | 94 KB | 10 emotion expressions showcase |
| `emperor_mathematicus.png` | 1.1 MB | Roman emperor mathematical portrait |
| `emperor_portrait.png` | 264 KB | Roman emperor polynomial portrait |
| `flowers_showcase.png` | 286 KB | 17 flower species showcase |
| `flowers_v2_compositions.png` | 166 KB | Floral composition variants |
| `flowers_v2_flowers.png` | 308 KB | Flower variant renders |
| `flowers_v2_plants.png` | 302 KB | Plant variant renders |
| `lines_composition.png` | 1.8 MB | Lines composition artwork |
| `parthenon_art.png` | 420 KB | Parthenon polynomial art |
| `porcelain_figurines.png` | 233 KB | Chinese porcelain style art |
| `scene_anatomy.png` | 181 KB | Anatomy study scene |
| `scene_game.png` | 554 KB | RPG game mockup scene |
| `scene_piranesi.png` | 682 KB | Piranesi impossible architecture scene |
| `scene_roman.png` | 193 KB | Roman forum scene |
| `spqr_piranesi_showcase.png` | 646 KB | SPQR + Piranesi combined showcase |
| `states_showcase.png` | 78 KB | Physical states showcase |
| `vitruvian_da_vinci.png` | 491 KB | Vitruvian Man polynomial recreation |
| `weary_emperor.png` | 281 KB | Weary Roman emperor portrait |

### Example PNGs (examples/)

| File | Size | Content |
|------|------|---------|
| `01_golden_mandala.png` | 759 KB | Golden ratio mandala (799 objects) |
| `02_piranesi_carcere.png` | 1.6 MB | Piranesi Carceri impossible prison (303 objects) |
| `03_roman_legion.png` | 352 KB | Roman legion formation (165 objects) |
| `04_anatomy_da_vinci.png` | 222 KB | Da Vinci anatomy study (93 objects) |
| `05_procedural_forest.png` | 845 KB | Procedural fractal forest (790 objects) |
| `06_turing_savanna.png` | 989 KB | Turing savanna patterns (219 objects) |
| `07_game_rpg.png` | 687 KB | RPG game mockup (628 objects) |
| `08_greek_amphora_gallery.png` | 77 KB | 5 lathe-rendered Greek vessels (121 objects) |
| `09_flower_variants.png` | 69 KB | 8 parametric flower forms (78 objects) |
| `10_biomech_atlas.png` | 246 KB | Biomechanical atlas (57 objects) |

### Demo PNGs (root)

| File | Size | Content |
|------|------|---------|
| `demo_rose.polyart` | 3.5 KB | Rose demo data |

### Classification Results (from CV test)

| Image | Classification | Rarity Score |
|-------|----------------|-------------|
| `emotions_showcase.png` | ART | 56/100 |
| `states_showcase.png` | ART | 55/100 |
| `animals_showcase.png` | ART | 63/100 |
| `curves_library_showcase.png` | ART | 59/100 |
| `flowers_showcase.png` | ART | 63/100 |

---

## 8. Video Content

### GIF Animations (videos_output/)

| # | File | Size | ~Frames | Description |
|---|------|------|---------|-------------|
| 01 | `01_golden_spiral.gif` | 15 KB | 87 | Golden spiral growth animation |
| 02 | `02_flower_bloom.gif` | 164 KB | 559 | Flower blooming sequence |
| 03 | `03_column_build.gif` | 7 KB | 57 | Roman column construction |
| 04 | `04_piranesi_stairs.gif` | 98 KB | 274 | Piranesi impossible staircase loop |
| 05 | `05_turing_pattern.gif` | 1.1 MB | 4,652 | Reaction-diffusion pattern evolution |
| 06 | `06_dna_helix.gif` | 312 KB | 1,055 | DNA double helix rotation |
| 07 | `07_fractal_tree.gif` | 110 KB | 352 | Fractal branching tree growth |
| 08 | `08_mandala_spin.gif` | 598 KB | 2,304 | Rotating mandala animation |
| 09 | `09_wave_interference.gif` | 43 KB | 169 | Wave interference pattern |
| 10 | `10_particle_burst.gif` | 72 KB | 294 | Particle burst animation |
| 11 | `11_sorting.gif` | 19 KB | 106 | Sorting algorithm visualization |
| 12 | `12_cell_divide.gif` | 128 KB | 489 | Cell division animation |
| 13 | `13_morph_polygon.gif` | 187 KB | 638 | Polygon morphing |
| 14 | `14_constellation.gif` | 26 KB | 53 | Star constellation drawing |
| 15 | `15_heartbeat.gif` | 232 KB | 797 | ECG heartbeat trace |
| 16 | `16_ecosystem.gif` | 70 KB | 376 | Ecosystem simulation |
| 17 | `17_neural_pulse.gif` | 208 KB | 790 | Neural pulse propagation |
| 18 | `18_orbits.gif` | 65 KB | 119 | Orbital mechanics |
| 19 | `19_crystal_grow.gif` | 450 KB | 1,527 | Crystal growth animation |
| 20 | `20_title_sequence.gif` | 68 KB | 164 | Title sequence animation |

**Total GIFs: 20 | Total size: 3.9 MB | Total frames: ~14,047**

---

## 9. Demo Outputs

### polyart_demo/

| File | Size | Description |
|------|------|-------------|
| `test_input.png` | 36 KB | Test input image for conversion |
| `test_output.polyart` | 8.3 KB | Converted .polyart output |
| `test_output.polyvid` | 112 KB | Converted .polyvid video output |
| `test_restored.gif` | 45 KB | Restored GIF from .polyvid |
| `test_restored.png` | 9.1 KB | Restored PNG from .polyart |

### polyart_demo/test_frames/ (24 frames)

- Source frames: `frame_000.png` through `frame_023.png` (664-708 bytes each)
- Tiny input frames for video codec testing

### polyart_demo/test_decoded_frames/ (24 frames)

- Decoded frames: `frame_00000.png` through `frame_00023.png` (4,359-4,702 bytes each)
- Higher-resolution decoded output from codec

### decoded_frames/ (root level, 10 frames)

- `frame_0000.png` through `frame_0009.png` (~2.4 KB each)
- Decoded frames from root-level codec test

---

## 10. Configuration Files

| File | Size | Lines | Description |
|------|------|-------|-------------|
| `.gitignore` | 235 B | 27 | Ignores `__pycache__/`, `*.pyc`, venv, IDE files |
| `README.md` | 7,589 B | 209 | Project overview, quick start, showcase table |
| `BIBLIOGRAPHY.md` | 17,755 B | 281 | 189 academic references across 15 categories |
| `CHARACTER_ENCODING.md` | 35,889 B | 618 | ASCII, CP1251, CP1252, Unicode math/Greek/shapes reference |
| `CHANGELOG.md` | 827 B | 20 | Version history: v1.0.0 → v2.0.0 → v2.1.0 |
| `CONTRIBUTORS.md` | 2,682 B | 68 | 30+ team members across 5 categories |
| `pyproject.toml` | 945 B | 39 | Build config, dependencies, entry points |
| `requirements.txt` | 39 B | 3 | numpy>=1.20, matplotlib>=3.4, scipy>=1.7 |
| `install_polyart.bat` | 2,387 B | 52 | Windows installer: file association + shortcut |

---

## 11. Project Statistics

### File Counts

| Category | Count |
|----------|-------|
| **Total files** | 269 |
| Python modules (polyart_*.py) | 16 |
| Standalone Python scripts | 13 |
| Articles & documentation | 37 |
| Multilingual articles | 10 |
| Reference documents | 10 |
| PNG images (root) | 37 |
| PNG images (examples/) | 10 |
| PNG images (other dirs) | 60 |
| GIF animations | 20 + 1 |
| .polyart data files | 16 |
| .polyvid video files | 3 |
| Codec implementations | 6 files (5 languages) |
| Demo frames | 58 |
| Configuration files | 9 |

### Code Statistics

| Metric | Value |
|--------|-------|
| **Total lines of Python** | 15,026 |
| **Total lines of Markdown** | 1,039 |
| **Total lines of articles** | 10,060 |
| **Total lines of codec (C++/Go/Java/JS)** | 3,135 |
| **Estimated total source lines** | ~29,260 |

### Content Statistics

| Metric | Value |
|--------|-------|
| **Total articles** | 37 |
| **Total article words** | ~51,189 |
| **Total multilingual articles** | 10 (5 languages × 2 topics) |
| **Total multilingual words** | ~14,774 |
| **Bibliography references** | 189 |
| **Contributors listed** | 30+ |
| **Unique Python classes** | 83 |
| **Unique Python public methods** | ~550+ |
| **GIF total frames** | ~14,047 |
| **Total PNG size** | 19.0 MB |
| **Total GIF size** | 3.9 MB |
| **Total project size** | 42.3 MB |

### Version History

| Version | Date | Highlights |
|---------|------|------------|
| v1.0.0 | 2026-07-12 | Initial: format, editor, viewer, basic API |
| v2.0.0 | 2026-07-12 | Complete API rewrite, fluent pattern, GreekLines/RomanLines/GoldenRatio |
| v2.1.0 | 2026-07-12 | Biology, sculpture, 10 examples, 5 articles |

---

*Registry generated from actual file contents. All class/method counts verified by source inspection.*
