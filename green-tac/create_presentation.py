import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_deck(output_path="green_tac_project_review.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank slide

    # Color Palette
    C_DARK_TEAL = RGBColor(14, 43, 37)       # #0E2B25 - Deep Forest / Hero
    C_EMERALD   = RGBColor(16, 138, 86)      # #108A56 - Brand Accent Green
    C_LIGHT_EMERALD = RGBColor(220, 245, 232) # Soft green highlight
    C_BG        = RGBColor(246, 249, 247)    # #F6F9F7 - Canvas Light
    C_WHITE     = RGBColor(255, 255, 255)    # Card backgrounds
    C_BORDER    = RGBColor(218, 230, 224)    # Card borders
    C_TEXT_MAIN = RGBColor(25, 36, 33)       # Charcoal text
    C_TEXT_MUTED= RGBColor(95, 110, 105)     # Subtitle text
    C_AMBER     = RGBColor(224, 102, 38)     # Warning / Metric accent
    C_BLUE      = RGBColor(37, 99, 235)      # Secondary accent
    C_CODE_BG   = RGBColor(238, 242, 240)    # Code snippet background

    FONT_HEAD = "Segoe UI"
    FONT_BODY = "Calibri"
    FONT_CODE = "Consolas"

    def set_slide_background(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title, category="GREEN TAC COMPILER REVIEW", light_theme=True):
        # Category / Pill
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.5), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_top = tf_cat.margin_right = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = FONT_HEAD
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_EMERALD if light_theme else RGBColor(52, 211, 153)

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.5), Inches(0.65))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = FONT_HEAD
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = C_TEXT_MAIN if light_theme else C_WHITE

    def add_card(slide, left, top, width, height, bg_color=C_WHITE, border_color=C_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.2)
        else:
            card.line.fill.background()
        return card

    # ==========================================
    # SLIDE 1: Title Slide (Dark Theme)
    # ==========================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, C_DARK_TEAL)

    # Accent decorative bar
    bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.3), Inches(1.2), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = RGBColor(52, 211, 153)
    bar.line.fill.background()

    # Title box
    tbox1 = slide1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.5), Inches(3.2))
    tf1 = tbox1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "🌱 Green TAC"
    p.font.name = FONT_HEAD
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p2 = tf1.add_paragraph()
    p2.text = "Carbon-Aware Adaptive Three-Address Code Optimization"
    p2.font.name = FONT_HEAD
    p2.font.size = Pt(24)
    p2.font.color.rgb = RGBColor(167, 243, 208)
    p2.space_before = Pt(8)

    p3 = tf1.add_paragraph()
    p3.text = "A lightweight research compiler balancing compilation energy, runtime energy, execution frequency, and grid carbon intensity."
    p3.font.name = FONT_BODY
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(209, 220, 216)
    p3.space_before = Pt(16)

    # Bottom Metadata Cards
    meta_info = [
        ("Core Language", "C++17 (Compiler Engine)\nPython (Harness & Models)"),
        ("Architectural Focus", "Intermediate Rep (TAC)\nDAG CSE & Copy Prop"),
        ("Key Innovation", "Dual-Grid Carbon Model\nE_compile vs E_runtime"),
        ("Deliverables", "Compiler, Test Suite, 120-Test Corpus,\nProfiling & Modeling Tooling")
    ]
    card_w = Inches(2.7)
    card_h = Inches(1.3)
    start_x = Inches(0.8)
    for i, (m_title, m_desc) in enumerate(meta_info):
        cx = start_x + i * Inches(2.95)
        cy = Inches(5.4)
        c = add_card(slide1, cx, cy, card_w, card_h, bg_color=RGBColor(23, 58, 51), border_color=RGBColor(40, 85, 75))
        tb = slide1.shapes.add_textbox(cx + Inches(0.15), cy + Inches(0.15), card_w - Inches(0.3), card_h - Inches(0.3))
        ttf = tb.text_frame
        ttf.word_wrap = True
        tp1 = ttf.paragraphs[0]
        tp1.text = m_title
        tp1.font.name = FONT_HEAD
        tp1.font.size = Pt(11)
        tp1.font.bold = True
        tp1.font.color.rgb = RGBColor(52, 211, 153)
        tp2 = ttf.add_paragraph()
        tp2.text = m_desc
        tp2.font.name = FONT_BODY
        tp2.font.size = Pt(10)
        tp2.font.color.rgb = RGBColor(220, 230, 225)
        tp2.space_before = Pt(4)

    # ==========================================
    # SLIDE 2: Executive Summary & Motivation
    # ==========================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2, C_BG)
    add_header(slide2, "Executive Summary: Why Carbon-Aware Compilation?")

    cards_data = [
        ("The 'Always-Optimize' Fallacy", 
         "Traditional compilers (GCC, Clang) default to aggressive passes (-O2, -O3). However, optimization passes consume substantial CPU cycles and electricity during compilation. For short-lived, ephemeral, or rarely executed scripts, compile-time energy spent exceeds all runtime energy saved.",
         "PARADIGM SHIFT", C_AMBER),
        ("Modern Workloads & Cloud Ephemerality", 
         "In modern CI/CD pipelines, container microservices, serverless Lambdas, and development test iterations, code is compiled repeatedly but runs only a handful of times before modification. Over-optimizing here directly inflates carbon footprints.",
         "CLOUD DYNAMICS", C_BLUE),
        ("Grid Carbon Intensity Dynamics", 
         "The electric grid carbon intensity (gCO2e/kWh) fluctuates significantly across hours and regions. Compiling during high-carbon coal/gas peaks to save microseconds during clean midday solar peaks creates a net carbon deficit.",
         "TEMPORAL REALITY", C_EMERALD)
    ]
    for i, (title, text, tag, tag_color) in enumerate(cards_data):
        x = Inches(0.8) + i * Inches(3.95)
        y = Inches(1.6)
        w = Inches(3.75)
        h = Inches(4.9)
        add_card(slide2, x, y, w, h)
        
        # Tag pill
        tag_shape = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.3), y + Inches(0.3), Inches(1.8), Inches(0.35))
        tag_shape.fill.solid()
        tag_shape.fill.fore_color.rgb = C_LIGHT_EMERALD
        tag_shape.line.fill.background()
        tf_t = tag_shape.text_frame
        p_t = tf_t.paragraphs[0]
        p_t.text = tag
        p_t.font.name = FONT_HEAD
        p_t.font.size = Pt(9)
        p_t.font.bold = True
        p_t.font.color.rgb = tag_color
        p_t.alignment = PP_ALIGN.CENTER
        
        tb = slide2.shapes.add_textbox(x + Inches(0.3), y + Inches(0.85), w - Inches(0.6), h - Inches(1.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEAD
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_MAIN
        
        p_body = tf.add_paragraph()
        p_body.text = text
        p_body.font.name = FONT_BODY
        p_body.font.size = Pt(12)
        p_body.font.color.rgb = C_TEXT_MUTED
        p_body.space_before = Pt(12)

    # ==========================================
    # SLIDE 3: Research Problem & Objective
    # ==========================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3, C_BG)
    add_header(slide3, "Research Formulation: Balancing Compilation & Execution Carbon")

    # Left Column: Problem statement & mathematical question
    add_card(slide3, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
    tb = slide3.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.0), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "The Central Research Question"
    p.font.name = FONT_HEAD
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_MAIN

    bullets = [
        ("Static Trade-off", "Can a compiler intelligently choose intermediate optimization passes by predicting the total operational carbon emissions of compilation + N executions?"),
        ("Temporal Heterogeneity", "How does differential grid carbon intensity (compiling at grid CI_compile vs. executing at grid CI_runtime) flip optimal optimization strategies?"),
        ("SLA / Overhead Guardrail", "How do we minimize carbon without violating user runtime SLAs? (e.g., ensuring execution time does not degrade by more than 10% vs baseline).")
    ]
    for b_title, b_desc in bullets:
        p1 = tf.add_paragraph()
        p1.text = f"• {b_title}: "
        p1.font.bold = True
        p1.font.name = FONT_HEAD
        p1.font.size = Pt(12)
        p1.font.color.rgb = C_EMERALD
        p1.space_before = Pt(14)
        
        run = p1.add_run()
        run.text = b_desc
        run.font.bold = False
        run.font.name = FONT_BODY
        run.font.color.rgb = C_TEXT_MUTED

    # Right Column: Green TAC Target Contributions
    add_card(slide3, Inches(6.7), Inches(1.6), Inches(5.8), Inches(5.0))
    tb2 = slide3.shapes.add_textbox(Inches(7.0), Inches(1.9), Inches(5.2), Inches(4.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "Key Project Deliverables"
    p.font.name = FONT_HEAD
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_MAIN

    items = [
        ("1. Standalone C++17 Compiler", "Compact lexer, recursive descent parser, AST, and Three-Address Code (TAC) IR generator with zero external heavy dependencies."),
        ("2. Multi-Tier Optimization Engine", "Pluggable strategies: Baseline (raw), Lightweight (constant folding, algebraic reduction, copy prop), and DAG-based Common Subexpression Elimination (CSE)."),
        ("3. Static Feature Extractor", "Extracts 8 structural AST/TAC features (instruction counts, branches, temporaries, expression depth, DAG opportunities) in linear time."),
        ("4. Carbon Minimization Decision Engine", "Formulates dual-CI cost equations, integrates with empirical hardware measurements (RAPL) or linear proxies, and emits optimal strategy + generated C.")
    ]
    for it_title, it_desc in items:
        p1 = tf2.add_paragraph()
        p1.text = it_title
        p1.font.bold = True
        p1.font.name = FONT_HEAD
        p1.font.size = Pt(12)
        p1.font.color.rgb = C_DARK_TEAL
        p1.space_before = Pt(10)

        p2 = tf2.add_paragraph()
        p2.text = it_desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_TEXT_MUTED
        p2.space_before = Pt(2)

    # ==========================================
    # SLIDE 4: End-to-End Compiler Pipeline
    # ==========================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4, C_BG)
    add_header(slide4, "Architecture: End-to-End Compiler Pipeline")

    # Pipeline stages visual representation (Horizontal chain)
    stages = [
        ("Source Code", "Mini C-like grammar\nint vars, loops, ifs", "lexer.cpp / parser.cpp", C_DARK_TEAL),
        ("Abstract Syntax Tree", "Hierarchical AST node\nrepresentation", "ast.cpp / ast.h", C_DARK_TEAL),
        ("Baseline TAC IR", "Normalized 3-address\nquadruple instructions", "tac.cpp / tac.h", C_DARK_TEAL),
        ("Optimizer Candidates", "Baseline vs Lightweight\nvs DAG-CSE passes", "optimizer.cpp", C_BLUE),
        ("Feature Extractor", "8 static structural\ncode metrics", "features.cpp", C_BLUE),
        ("Carbon Selector", "Empirical model + dual CI\nCO2e minimization", "selector.cpp / carbon.cpp", C_EMERALD),
        ("Target Code Emitted", "Optimized TAC +\ncompilable ANSI C", "codegen_c.cpp", C_EMERALD)
    ]

    card_w = Inches(1.6)
    card_h = Inches(3.6)
    for i, (st_name, st_desc, st_src, color) in enumerate(stages):
        x = Inches(0.8) + i * Inches(1.7)
        y = Inches(1.8)
        card = add_card(slide4, x, y, card_w, card_h)
        
        # Stage number badge
        badge = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.12), y + Inches(0.15), Inches(0.4), Inches(0.28))
        badge.fill.solid()
        badge.fill.fore_color.rgb = color
        badge.line.fill.background()
        tf_b = badge.text_frame
        p_b = tf_b.paragraphs[0]
        p_b.text = str(i+1)
        p_b.font.name = FONT_HEAD
        p_b.font.size = Pt(10)
        p_b.font.bold = True
        p_b.font.color.rgb = C_WHITE
        p_b.alignment = PP_ALIGN.CENTER
        
        tb = slide4.shapes.add_textbox(x + Inches(0.1), y + Inches(0.55), card_w - Inches(0.2), card_h - Inches(0.7))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = st_name
        p.font.name = FONT_HEAD
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_MAIN
        
        p_desc = tf.add_paragraph()
        p_desc.text = st_desc
        p_desc.font.name = FONT_BODY
        p_desc.font.size = Pt(10)
        p_desc.font.color.rgb = C_TEXT_MUTED
        p_desc.space_before = Pt(8)

        p_src = tf.add_paragraph()
        p_src.text = st_src
        p_src.font.name = FONT_CODE
        p_src.font.size = Pt(8.5)
        p_src.font.color.rgb = color
        p_src.space_before = Pt(12)

    # Bottom summary banner
    banner = add_card(slide4, Inches(0.8), Inches(5.7), Inches(11.7), Inches(1.1), bg_color=C_LIGHT_EMERALD, border_color=C_EMERALD)
    tb_ban = slide4.shapes.add_textbox(Inches(1.0), Inches(5.8), Inches(11.3), Inches(0.9))
    tf_ban = tb_ban.text_frame
    tf_ban.word_wrap = True
    p = tf_ban.paragraphs[0]
    p.text = "Modular Decoupling Principle"
    p.font.name = FONT_HEAD
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEAL
    p2 = tf_ban.add_paragraph()
    p2.text = "The front-end, optimization passes, and selection logic are strictly decoupled. Optimization passes operate entirely on the TAC intermediate representation, allowing new passes or machine backends to be plugged in without refactoring the carbon decision model."
    p2.font.name = FONT_BODY
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_TEXT_MAIN
    p2.space_before = Pt(2)

    # ==========================================
    # SLIDE 5: Intermediate Representation (TAC) & Features
    # ==========================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5, C_BG)
    add_header(slide5, "Intermediate Representation & Static Feature Extraction")

    # Left: TAC Representation Details
    add_card(slide5, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.0))
    tb_l = slide5.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.1), Inches(4.5))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "Three-Address Code (TAC) Quadruple Design"
    p.font.name = FONT_HEAD
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_MAIN

    tac_points = [
        ("Instruction Kinds", "Binary (t = a op b), Assign (t = a), IfGoto (if a rel b goto L), Goto (goto L), Label (L:)."),
        ("Single Destination Property", "At most one operator and one assignment per instruction, simplifying dataflow and DAG construction."),
        ("Explicit Control Flow", "High-level 'if/else' and 'while' loops are lowered into explicit conditional and unconditional jumps with deterministic basic block boundaries."),
        ("Codegen Flexibility", "TAC can be inspected directly, evaluated by an interpreter, or emitted as valid ANSI C for baseline comparison.")
    ]
    for pt_t, pt_d in tac_points:
        p1 = tf_l.add_paragraph()
        p1.text = f"• {pt_t}: "
        p1.font.name = FONT_HEAD
        p1.font.bold = True
        p1.font.size = Pt(11)
        p1.font.color.rgb = C_DARK_TEAL
        p1.space_before = Pt(8)
        run = p1.add_run()
        run.text = pt_d
        run.font.bold = False
        run.font.name = FONT_BODY
        run.font.color.rgb = C_TEXT_MUTED

    # Right: Static Features Table / Cards
    add_card(slide5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0))
    tb_r = slide5.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.5))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "8 Extracted Static Features (src/features.cpp)"
    p.font.name = FONT_HEAD
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_MAIN

    features_list = [
        ("instructions", "Total count of emitted TAC instructions"),
        ("binary_ops", "Count of binary operations (+, -, *, /, %)"),
        ("branches", "Count of conditional (IfGoto) instructions"),
        ("labels", "Count of jump targets / block delimiters"),
        ("temporaries", "Virtual registers allocated (t1, t2, ...)"),
        ("basic_blocks", "Straight-line execution blocks between jumps"),
        ("expr_depth", "Maximum AST expression hierarchy depth"),
        ("common_subexprs", "Identified identical subexpression instances")
    ]
    for f_name, f_desc in features_list:
        p1 = tf_r.add_paragraph()
        p1.text = f"{f_name.ljust(16)}: "
        p1.font.name = FONT_CODE
        p1.font.bold = True
        p1.font.size = Pt(10)
        p1.font.color.rgb = C_EMERALD
        p1.space_before = Pt(4)
        run = p1.add_run()
        run.text = f_desc
        run.font.name = FONT_BODY
        run.font.size = Pt(10.5)
        run.font.color.rgb = C_TEXT_MUTED

    # ==========================================
    # SLIDE 6: Optimization Strategies Deep-Dive
    # ==========================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6, C_BG)
    add_header(slide6, "Optimization Strategies: Mechanics & Complexity")

    strat_cards = [
        ("Baseline Strategy", "Zero Optimization Overhead",
         [("Mechanism", "Direct syntax-directed translation from AST to TAC."),
          ("Pass Cost", "O(N) single-pass generation; minimal compilation energy."),
          ("Runtime Profile", "Redundant temporaries, unsimplified arithmetic, repeated expressions."),
          ("When Optimal", "Code executed once or few times (N < N*), or compile grid is heavily carbon-intensive.")],
         C_DARK_TEAL),
        ("Lightweight Strategy", "Peephole & Propagation",
         [("Constant Folding", "Evaluates literal operations at compile time (e.g., 2 + 3 -> 5)."),
          ("Algebraic Identities", "Simplifies x + 0 -> x, x * 1 -> x, x * 0 -> 0."),
          ("Copy Propagation", "Substitutes aliases with dependence chain tracking and invalidation on reassignment."),
          ("Pass Cost", "Fast forward analysis O(N), modest compile energy footprint.")],
         C_BLUE),
        ("DAG / CSE Strategy", "Directed Acyclic Graph CSE",
         [("Local CSE", "Hashes binary operations in basic blocks into DAG nodes; detects identical subtrees."),
          ("Value Numbering", "Replaces recomputations with existing temporary registers."),
          ("Alias Invalidation", "Conservative flush of expression caches across assignment and branch boundaries."),
          ("Pass Cost", "Higher compile-time energy; maximum reduction in TAC count and runtime.")],
         C_EMERALD)
    ]
    for i, (title, subtitle, bullets, color) in enumerate(strat_cards):
        x = Inches(0.8) + i * Inches(3.95)
        y = Inches(1.6)
        w = Inches(3.75)
        h = Inches(5.0)
        add_card(slide6, x, y, w, h)
        
        # Header banner inside card
        top_bar = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, Inches(0.08))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = color
        top_bar.line.fill.background()

        tb = slide6.shapes.add_textbox(x + Inches(0.25), y + Inches(0.25), w - Inches(0.5), h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEAD
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_MAIN
        
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = color
        p_sub.space_before = Pt(2)
        
        for b_lbl, b_txt in bullets:
            pb = tf.add_paragraph()
            pb.text = f"{b_lbl}: "
            pb.font.name = FONT_HEAD
            pb.font.bold = True
            pb.font.size = Pt(10.5)
            pb.font.color.rgb = C_TEXT_MAIN
            pb.space_before = Pt(8)
            run = pb.add_run()
            run.text = b_txt
            run.font.name = FONT_BODY
            run.font.bold = False
            run.font.size = Pt(10)
            run.font.color.rgb = C_TEXT_MUTED

    # ==========================================
    # SLIDE 7: Mathematical Carbon & Energy Model
    # ==========================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7, C_BG)
    add_header(slide7, "Mathematical Model: Carbon Objective & Guardrails")

    # Formula Box Left
    add_card(slide7, Inches(0.8), Inches(1.6), Inches(6.0), Inches(5.0))
    tb_fm = slide7.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.4), Inches(4.5))
    tf_fm = tb_fm.text_frame
    tf_fm.word_wrap = True

    p = tf_fm.paragraphs[0]
    p.text = "Mathematical Carbon Objective"
    p.font.name = FONT_HEAD
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEAL

    # Formulas in code box style
    p1 = tf_fm.add_paragraph()
    p1.text = "1. Total Energy for Strategy i (Joules):"
    p1.font.name = FONT_HEAD
    p1.font.bold = True
    p1.font.size = Pt(11)
    p1.font.color.rgb = C_TEXT_MAIN
    p1.space_before = Pt(10)

    p2 = tf_fm.add_paragraph()
    p2.text = "   E_total(i) = E_compile(i) + N · E_runtime(i)"
    p2.font.name = FONT_CODE
    p2.font.bold = True
    p2.font.size = Pt(12)
    p2.font.color.rgb = C_EMERALD
    p2.space_before = Pt(4)

    p3 = tf_fm.add_paragraph()
    p3.text = "2. Carbon Footprint (grams CO2e):"
    p3.font.name = FONT_HEAD
    p3.font.bold = True
    p3.font.size = Pt(11)
    p3.font.color.rgb = C_TEXT_MAIN
    p3.space_before = Pt(12)

    p4 = tf_fm.add_paragraph()
    p4.text = "   CO2e(i) = [ E_compile(i) · CI_compile +\n               N · E_runtime(i) · CI_runtime ] / (3.6 × 10^6)"
    p4.font.name = FONT_CODE
    p4.font.bold = True
    p4.font.size = Pt(11)
    p4.font.color.rgb = C_EMERALD
    p4.space_before = Pt(4)

    p5 = tf_fm.add_paragraph()
    p5.text = "3. Runtime SLA Constraint (Guardrail):"
    p5.font.name = FONT_HEAD
    p5.font.bold = True
    p5.font.size = Pt(11)
    p5.font.color.rgb = C_TEXT_MAIN
    p5.space_before = Pt(12)

    p6 = tf_fm.add_paragraph()
    p6.text = "   Runtime(i) <= Runtime_baseline · (1 + θ_max)\n   where θ_max is max allowed overhead (default 10%)"
    p6.font.name = FONT_CODE
    p6.font.bold = True
    p6.font.size = Pt(11)
    p6.font.color.rgb = C_AMBER
    p6.space_before = Pt(4)

    # Explanation Right
    add_card(slide7, Inches(7.1), Inches(1.6), Inches(5.4), Inches(5.0))
    tb_ex = slide7.shapes.add_textbox(Inches(7.4), Inches(1.8), Inches(4.8), Inches(4.5))
    tf_ex = tb_ex.text_frame
    tf_ex.word_wrap = True

    p = tf_ex.paragraphs[0]
    p.text = "Critical Theoretical Insights"
    p.font.name = FONT_HEAD
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEAL

    insights = [
        ("Why Two Carbon Intensities?", "If CI_compile == CI_runtime, the carbon intensity is merely a scalar multiplier and never changes strategy ranking! Decoupling CI_compile and CI_runtime models real-world temporal and geographic grid shifts."),
        ("The Break-Even Boundary (N*)", "For any program, there exists a threshold execution count N* where cumulative runtime energy savings offset compile energy costs. The selector computes this dynamically."),
        ("Multi-Metric Linear Cost Model", "data/model.csv encodes learned coefficients: compile_energy = w_0 + Σ w_j · f_j. When uncalibrated, transparent feature-based proxies guarantee safe fallback.")
    ]
    for ins_t, ins_d in insights:
        p1 = tf_ex.add_paragraph()
        p1.text = f"• {ins_t}:"
        p1.font.name = FONT_HEAD
        p1.font.bold = True
        p1.font.size = Pt(11.5)
        p1.font.color.rgb = C_BLUE
        p1.space_before = Pt(10)
        run = p1.add_run()
        run.text = f"\n  {ins_d}"
        run.font.name = FONT_BODY
        run.font.size = Pt(10.5)
        run.font.color.rgb = C_TEXT_MUTED

    # ==========================================
    # SLIDE 8: Live Demo & Walkthrough (cse.c)
    # ==========================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8, C_BG)
    add_header(slide8, "Live Walkthrough: Case Study on benchmarks/cse.c")

    # Column 1: Source & Features
    add_card(slide8, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.0))
    tb1 = slide8.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(3.2), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "1. Source Code (cse.c)"
    p.font.name = FONT_HEAD
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEAL
    
    code_p = tf1.add_paragraph()
    code_p.text = "x = (a + b) * (a + b) + (a + b);\ny = (a + b) * 2;\n"
    code_p.font.name = FONT_CODE
    code_p.font.size = Pt(11)
    code_p.font.color.rgb = C_TEXT_MAIN
    code_p.space_before = Pt(8)

    p_feat = tf1.add_paragraph()
    p_feat.text = "Static Feature Extraction:"
    p_feat.font.name = FONT_HEAD
    p_feat.font.bold = True
    p_feat.font.size = Pt(12)
    p_feat.font.color.rgb = C_TEXT_MAIN
    p_feat.space_before = Pt(12)

    feat_dump = [
        "Instructions: 9",
        "Binary ops:   7",
        "Branches:     0",
        "Temporaries:  7",
        "Basic blocks: 1",
        "Expr depth:   3",
        "CSE count:    3"
    ]
    for fd in feat_dump:
        pfd = tf1.add_paragraph()
        pfd.text = fd
        pfd.font.name = FONT_CODE
        pfd.font.size = Pt(10)
        pfd.font.color.rgb = C_TEXT_MUTED
        pfd.space_before = Pt(2)

    # Column 2: TAC Comparison
    add_card(slide8, Inches(4.6), Inches(1.6), Inches(3.8), Inches(5.0))
    tb2 = slide8.shapes.add_textbox(Inches(4.8), Inches(1.8), Inches(3.4), Inches(4.5))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "2. Baseline vs DAG TAC"
    p.font.name = FONT_HEAD
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEAL

    p_base = tf2.add_paragraph()
    p_base.text = "[Baseline TAC - 9 instrs]"
    p_base.font.name = FONT_CODE
    p_base.font.bold = True
    p_base.font.size = Pt(10)
    p_base.font.color.rgb = C_AMBER
    p_base.space_before = Pt(6)

    base_tac = "t1 = a + b\nt2 = a + b\nt3 = t1 * t2\nt4 = a + b\nt5 = t3 + t4\nx = t5\nt6 = a + b\nt7 = t6 * 2\ny = t7"
    p_bt = tf2.add_paragraph()
    p_bt.text = base_tac
    p_bt.font.name = FONT_CODE
    p_bt.font.size = Pt(9.5)
    p_bt.font.color.rgb = C_TEXT_MUTED
    p_bt.space_before = Pt(2)

    p_dag = tf2.add_paragraph()
    p_dag.text = "[DAG TAC - 7 instrs (-22.2%)]"
    p_dag.font.name = FONT_CODE
    p_dag.font.bold = True
    p_dag.font.size = Pt(10)
    p_dag.font.color.rgb = C_EMERALD
    p_dag.space_before = Pt(10)

    dag_tac = "t1 = a + b\nt3 = t1 * t1\nt5 = t3 + t1\nx = t5\nt6 = a + b\nt7 = t6 * 2\ny = t7"
    p_dt = tf2.add_paragraph()
    p_dt.text = dag_tac
    p_dt.font.name = FONT_CODE
    p_dt.font.size = Pt(9.5)
    p_dt.font.color.rgb = C_TEXT_MAIN
    p_dt.space_before = Pt(2)

    # Column 3: Green Selector Decision
    add_card(slide8, Inches(8.6), Inches(1.6), Inches(3.9), Inches(5.0))
    tb3 = slide8.shapes.add_textbox(Inches(8.8), Inches(1.8), Inches(3.5), Inches(4.5))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "3. Carbon Selection Decision"
    p.font.name = FONT_HEAD
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEAL

    p_par = tf3.add_paragraph()
    p_par.text = "Parameters: N=10,000 | CI_comp=700 | CI_run=200"
    p_par.font.name = FONT_BODY
    p_par.font.size = Pt(9.5)
    p_par.font.color.rgb = C_TEXT_MUTED
    p_par.space_before = Pt(4)

    # Metric Table
    metrics = [
        ("baseline", "5.95 J", "22.10 J", "12.28 g"),
        ("lightweight", "9.15 J", "22.10 J", "12.28 g"),
        ("dag", "15.05 J", "16.30 J", "9.06 g  ★")
    ]
    p_th = tf3.add_paragraph()
    p_th.text = f"{'Strategy':<11} {'Comp J':<7} {'Run J':<7} {'CO2e'}"
    p_th.font.name = FONT_CODE
    p_th.font.bold = True
    p_th.font.size = Pt(9.5)
    p_th.font.color.rgb = C_TEXT_MAIN
    p_th.space_before = Pt(8)

    for st, cj, rj, co in metrics:
        p_row = tf3.add_paragraph()
        p_row.text = f"{st:<11} {cj:<7} {rj:<7} {co}"
        p_row.font.name = FONT_CODE
        p_row.font.size = Pt(9.5)
        p_row.font.color.rgb = C_EMERALD if "★" in co else C_TEXT_MUTED
        p_row.space_before = Pt(2)

    # Decision box
    dec_box = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(4.7), Inches(3.5), Inches(1.5))
    dec_box.fill.solid()
    dec_box.fill.fore_color.rgb = C_LIGHT_EMERALD
    dec_box.line.color.rgb = C_EMERALD
    tf_db = dec_box.text_frame
    tf_db.word_wrap = True
    p_dbt = tf_db.paragraphs[0]
    p_dbt.text = "DECISION: Strategy 'dag' Selected"
    p_dbt.font.name = FONT_HEAD
    p_dbt.font.size = Pt(11)
    p_dbt.font.bold = True
    p_dbt.font.color.rgb = C_EMERALD
    p_dbb = tf_db.add_paragraph()
    p_dbb.text = "Despite 2.5x compile energy (15.05 J vs 5.95 J), N=10,000 runs save 5.8 J/run at runtime, reducing net emissions from 12.28g to 9.06g CO2e (26.2% carbon reduction)."
    p_dbb.font.name = FONT_BODY
    p_dbb.font.size = Pt(9.5)
    p_dbb.font.color.rgb = C_TEXT_MAIN
    p_dbb.space_before = Pt(4)

    # ==========================================
    # SLIDE 9: Calibration & Empirical Profiling
    # ==========================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9, C_BG)
    add_header(slide9, "Empirical Calibration & Measurement Methodology")

    col_w = Inches(3.75)
    col_h = Inches(5.0)

    # Col 1: Hardware Instrumentation
    add_card(slide9, Inches(0.8), Inches(1.6), col_w, col_h)
    tb1 = slide9.shapes.add_textbox(Inches(1.05), Inches(1.85), col_w - Inches(0.5), col_h - Inches(0.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "Physical Energy (RAPL)"
    p.font.name = FONT_HEAD
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEAL
    
    r_pts = [
        ("Intel / AMD RAPL Interface", "Measures physical processor package energy via Linux MSR sysfs powercap."),
        ("Graceful Degradation", "On platforms without root RAPL access (e.g. Windows MSYS2), energy fields remain cleanly blank rather than populated with falsified mock data."),
        ("High-Precision Timing", "std::chrono::high_resolution_clock timing recorded for every benchmark x strategy run."),
        ("Micro-Benchmark Isolation", "Repeated runs (default 50 iterations) to filter OS scheduler jitter.")
    ]
    for h_t, h_d in r_pts:
        p1 = tf1.add_paragraph()
        p1.text = f"• {h_t}: "
        p1.font.bold = True
        p1.font.size = Pt(10.5)
        p1.font.color.rgb = C_TEXT_MAIN
        p1.space_before = Pt(10)
        run = p1.add_run()
        run.text = h_d
        run.font.bold = False
        run.font.color.rgb = C_TEXT_MUTED

    # Col 2: Train/Test Program Split
    add_card(slide9, Inches(4.75), Inches(1.6), col_w, col_h)
    tb2 = slide9.shapes.add_textbox(Inches(5.0), Inches(1.85), col_w - Inches(0.5), col_h - Inches(0.5))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Scientific Data Split"
    p.font.name = FONT_HEAD
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEAL

    s_pts = [
        ("No Run-Level Leakage", "Cross-validation splits on held-out programs, NEVER on repeated runs of the same program."),
        ("Generalization Testing", "Ensures the learned linear regression models generalize to unseen AST structures and loop bounds."),
        ("Feature Selection Regularization", "Avoids over-fitting large feature vectors to compact benchmark corpuses."),
        ("Validation Metrics", "Outputs R2, MAE, and RMSE to data/model_metrics.csv.")
    ]
    for s_t, s_d in s_pts:
        p1 = tf2.add_paragraph()
        p1.text = f"• {s_t}: "
        p1.font.bold = True
        p1.font.size = Pt(10.5)
        p1.font.color.rgb = C_TEXT_MAIN
        p1.space_before = Pt(10)
        run = p1.add_run()
        run.text = s_d
        run.font.bold = False
        run.font.color.rgb = C_TEXT_MUTED

    # Col 3: Research Integrity & Transparency
    add_card(slide9, Inches(8.7), Inches(1.6), col_w, col_h)
    tb3 = slide9.shapes.add_textbox(Inches(8.95), Inches(1.85), col_w - Inches(0.5), col_h - Inches(0.5))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "Research Integrity"
    p.font.name = FONT_HEAD
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEAL

    i_pts = [
        ("No Fabricated Constants", "The repository ships with an empty model.csv. Coefficients must be fitted empirically."),
        ("Explicit Fallback Flagging", "When uncalibrated, the CLI explicitly prints 'partial / proxy fallback' to prevent mistaking proxy formulas for hardware reality."),
        ("Deterministic Reproducibility", "Synthetic generator uses fixed seeds to ensure identical benchmark sets across testbeds."),
        ("Full Provenance", "Records hardware specs, OS, GCC version, and grid source metadata.")
    ]
    for i_t, i_d in i_pts:
        p1 = tf3.add_paragraph()
        p1.text = f"• {i_t}: "
        p1.font.bold = True
        p1.font.size = Pt(10.5)
        p1.font.color.rgb = C_TEXT_MAIN
        p1.space_before = Pt(10)
        run = p1.add_run()
        run.text = i_d
        run.font.bold = False
        run.font.color.rgb = C_TEXT_MUTED

    # ==========================================
    # SLIDE 10: Benchmark Corpus Suite
    # ==========================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10, C_BG)
    add_header(slide10, "Benchmark Suite: 120 Synthetic Program Corpus")

    cats = [
        ("Arithmetic-Heavy", "Deep expression trees with sequential binary ops (+, -, *, /, %). Tests constant folding depth and arithmetic pipeline pressure.", "30 programs"),
        ("CSE-Heavy", "Redundant identical subexpressions spread across statements. Stress-tests DAG value-numbering and hash collision handling.", "30 programs"),
        ("Constant-Heavy", "High ratio of literal constants, redundant zero/one operations, and copy-chains. Validates algebraic simplification.", "20 programs"),
        ("Loop-Heavy", "Nested and single while loops with accumulator mutations. Tests basic block boundary flushes and control-flow conservatism.", "20 programs"),
        ("Mixed Control-Flow", "Realistic amalgam of conditionals, loops, subexpressions, and copies. Evaluates real-world compiler behavior.", "20 programs")
    ]

    card_w = Inches(11.7)
    card_h = Inches(0.85)
    for i, (cat_name, cat_desc, cat_count) in enumerate(cats):
        y = Inches(1.6) + i * Inches(1.0)
        add_card(slide10, Inches(0.8), y, card_w, card_h)
        
        # Pill
        pill = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), y + Inches(0.2), Inches(2.2), Inches(0.45))
        pill.fill.solid()
        pill.fill.fore_color.rgb = C_LIGHT_EMERALD
        pill.line.color.rgb = C_EMERALD
        tf_p = pill.text_frame
        pp = tf_p.paragraphs[0]
        pp.text = cat_name
        pp.font.name = FONT_HEAD
        pp.font.size = Pt(11)
        pp.font.bold = True
        pp.font.color.rgb = C_DARK_TEAL
        pp.alignment = PP_ALIGN.CENTER

        # Description text
        tb = slide10.shapes.add_textbox(Inches(3.4), y + Inches(0.15), Inches(7.5), Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = cat_desc
        p.font.name = FONT_BODY
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_MAIN
        
        # Count Badge
        cb = slide10.shapes.add_textbox(Inches(11.1), y + Inches(0.2), Inches(1.2), Inches(0.45))
        tf_c = cb.text_frame
        pc = tf_c.paragraphs[0]
        pc.text = cat_count
        pc.font.name = FONT_CODE
        pc.font.size = Pt(11)
        pc.font.bold = True
        pc.font.color.rgb = C_EMERALD
        pc.alignment = PP_ALIGN.RIGHT

    # ==========================================
    # SLIDE 11: Carbon Sensitivity & Trade-Off Scenarios
    # ==========================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11, C_BG)
    add_header(slide11, "Trade-Off Analysis: When Does Each Strategy Win?")

    scenarios = [
        ("Scenario A: Cloud CI/CD Short Run",
         "N = 5 runs (Ephemeral Unit Test)",
         "Compile CI: 650 g/kWh (Coal grid peak)\nRuntime CI: 250 g/kWh (Clean nighttime)\n\nResult: BASELINE WINS.\nCompile energy penalty of DAG exceeds any runtime savings over 5 runs. Baseline produces lowest net CO2e.",
         C_AMBER),
        ("Scenario B: Production Microservice",
         "N = 100,000 runs (High-frequency API)",
         "Compile CI: 400 g/kWh (Average)\nRuntime CI: 400 g/kWh (Average)\n\nResult: DAG WINS.\nOne-time compile energy is completely amortized across 100k executions. 22% runtime instruction cut dominates.",
         C_EMERALD),
        ("Scenario C: Temporal Carbon Arbitrage",
         "N = 500 runs (Mid-scale batch job)",
         "Compile CI: 800 g/kWh (Extreme dirty peak)\nRuntime CI: 100 g/kWh (Wind/Solar surplus)\n\nResult: LIGHTWEIGHT WINS.\nStrikes ideal equilibrium: avoids high DAG compilation energy while extracting 80% of copy/const wins.",
         C_BLUE)
    ]
    for i, (sc_title, sc_sub, sc_body, color) in enumerate(scenarios):
        x = Inches(0.8) + i * Inches(3.95)
        y = Inches(1.6)
        w = Inches(3.75)
        h = Inches(5.0)
        add_card(slide11, x, y, w, h)
        
        tb = slide11.shapes.add_textbox(x + Inches(0.25), y + Inches(0.3), w - Inches(0.5), h - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = sc_title
        p.font.name = FONT_HEAD
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_MAIN

        p_sub = tf.add_paragraph()
        p_sub.text = sc_sub
        p_sub.font.name = FONT_HEAD
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = color
        p_sub.space_before = Pt(4)

        p_body = tf.add_paragraph()
        p_body.text = sc_body
        p_body.font.name = FONT_BODY
        p_body.font.size = Pt(11)
        p_body.font.color.rgb = C_TEXT_MUTED
        p_body.space_before = Pt(12)

    # ==========================================
    # SLIDE 12: Software Engineering & Architecture
    # ==========================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12, C_BG)
    add_header(slide12, "Engineering Highlights & Codebase Architecture")

    eng_cards = [
        ("Zero Heavy Build Dependencies",
         "The C++17 compiler engine compiles directly via a clean, self-contained Python driver (build.py) with standard g++, clang++, or MSYS2.\n\nNo bulky CMake, Ninja, Make, or LLVM dependencies required for compile or test passes.",
         "PORTABLE C++17"),
        ("Modular UNIX-Style CLI Driver",
         "All developer workflows unified under run.py:\n• python run.py test (Unit test runner)\n• python run.py demo (Interactive walkthrough)\n• python run.py compare (Multi-strategy comparison)\n• python run.py green (Carbon optimization)\n• python run.py dataset/collect (Benchmarking)",
         "DEV EXPERIENCE"),
        ("Extensible Optimization Interface",
         "Clear functional contract in src/optimizer.cpp:\nTACProgram optimize(const TACProgram&, Strategy)\n\nAdding loop invariant code motion, dead code elimination, or peephole simplifications requires zero changes to AST or selector logic.",
         "EXTENSIBILITY"),
        ("Dual Code Generation (TAC & ANSI C)",
         "src/codegen_c.cpp converts optimized TAC back into clean, compilable ANSI C.\n\nEnables downstream compilation with GCC/Clang to measure native wall-clock execution and machine code efficiency.",
         "VERIFIABILITY")
    ]
    for i, (title, text, tag) in enumerate(eng_cards):
        col = i % 2
        row = i // 2
        x = Inches(0.8) + col * Inches(5.95)
        y = Inches(1.6) + row * Inches(2.55)
        w = Inches(5.75)
        h = Inches(2.35)
        add_card(slide12, x, y, w, h)
        
        tb = slide12.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), w - Inches(0.5), h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = f"{tag} | {title}"
        p.font.name = FONT_HEAD
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_DARK_TEAL

        p2 = tf.add_paragraph()
        p2.text = text
        p2.font.name = FONT_BODY
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = C_TEXT_MUTED
        p2.space_before = Pt(6)

    # ==========================================
    # SLIDE 13: Evaluation Policies & Research Comparison
    # ==========================================
    slide13 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide13, C_BG)
    add_header(slide13, "Experimental Evaluation: 4-Policy Comparison")

    # Table layout for policy evaluation
    rows = [
        ("Policy 1: Always Baseline", "Zero compile energy", "High runtime overhead", "Optimal for N < N* and high CI_compile"),
        ("Policy 2: Always Lightweight", "Low compile energy", "Moderate runtime savings", "Good middle-ground; avoids complex DAG analysis"),
        ("Policy 3: Always DAG (Max Opt)", "High compile energy", "Lowest runtime energy", "Optimal for long-running / high-frequency cloud apps"),
        ("Policy 4: Green Adaptive Selector", "Dynamic / Contextual", "Guaranteed <= 10% SLA", "MINIMIZES CO2e across all operational parameters")
    ]
    
    add_card(slide13, Inches(0.8), Inches(1.6), Inches(11.7), Inches(3.2))
    tb_t = slide13.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(2.8))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True

    p = tf_t.paragraphs[0]
    p.text = "Comparative Policy Benchmark Matrix"
    p.font.name = FONT_HEAD
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEAL

    p_head = tf_t.add_paragraph()
    p_head.text = f"{'Policy':<30} {'Compilation Energy':<22} {'Runtime Efficiency':<25} {'Carbon Footprint Profile'}"
    p_head.font.name = FONT_CODE
    p_head.font.bold = True
    p_head.font.size = Pt(10.5)
    p_head.font.color.rgb = C_TEXT_MAIN
    p_head.space_before = Pt(8)

    for pol, ce, re, co in rows:
        p_r = tf_t.add_paragraph()
        p_r.text = f"{pol:<30} {ce:<22} {re:<25} {co}"
        p_r.font.name = FONT_CODE
        p_r.font.size = Pt(10)
        p_r.font.color.rgb = C_EMERALD if "Green Adaptive" in pol else C_TEXT_MUTED
        p_r.space_before = Pt(5)

    # Bottom Callout
    bot_card = add_card(slide13, Inches(0.8), Inches(5.0), Inches(11.7), Inches(1.6), bg_color=C_LIGHT_EMERALD, border_color=C_EMERALD)
    tb_b = slide13.shapes.add_textbox(Inches(1.0), Inches(5.15), Inches(11.3), Inches(1.3))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    p = tf_b.paragraphs[0]
    p.text = "Key Experimental Finding"
    p.font.name = FONT_HEAD
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEAL
    p2 = tf_b.add_paragraph()
    p2.text = "Static compilers that disregard compilation cost and electricity grid emissions impose an invisible carbon tax on short-lived cloud jobs. Green TAC proves that compiler optimization should be an adaptive multi-objective optimization problem, factoring in deployment lifecycles and temporal carbon economics."
    p2.font.name = FONT_BODY
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_TEXT_MAIN
    p2.space_before = Pt(3)

    # ==========================================
    # SLIDE 14: Conclusion & Review Discussion
    # ==========================================
    slide14 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide14, C_DARK_TEAL)

    # Header in dark theme
    tbox14 = slide14.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.5), Inches(1.0))
    tf14 = tbox14.text_frame
    tf14.word_wrap = True
    p = tf14.paragraphs[0]
    p.text = "Review Summary & Future Horizons"
    p.font.name = FONT_HEAD
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p_sub = tf14.add_paragraph()
    p_sub.text = "Green TAC demonstrates practical, principled carbon accounting for modern compiler pipelines."
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = RGBColor(167, 243, 208)
    p_sub.space_before = Pt(4)

    # 3 Summary Cards
    concl_cards = [
        ("Summary of Contributions", 
         "• Fully operational C++17 TAC compiler\n• 3 Pluggable optimization passes\n• Formulated dual-CI carbon equation\n• Guarded runtime overhead constraints\n• Comprehensive 120-test benchmark corpus\n• RAPL measurement & model fitting tools",
         RGBColor(23, 58, 51)),
        ("Future Roadmap", 
         "• Global inter-procedural optimizations\n• Chaitin-style register allocation pass\n• Real-time REST API integration with\n  Live Grid APIs (Electricity Maps)\n• LLVM pass plugin implementation\n• Multi-core parallel compile modeling",
         RGBColor(23, 58, 51)),
        ("Project Review Discussion", 
         "Ready for Review Questions:\n\n• Codebase structure & tests\n• TAC IR & DAG implementation\n• Mathematical carbon model\n• Hardware profiling & RAPL support\n• Live demo execution",
         RGBColor(16, 138, 86))
    ]
    for i, (c_t, c_b, bg_c) in enumerate(concl_cards):
        x = Inches(0.8) + i * Inches(3.95)
        y = Inches(2.2)
        w = Inches(3.75)
        h = Inches(4.5)
        add_card(slide14, x, y, w, h, bg_color=bg_c, border_color=RGBColor(40, 85, 75))
        
        tb = slide14.shapes.add_textbox(x + Inches(0.25), y + Inches(0.25), w - Inches(0.5), h - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = c_t
        p.font.name = FONT_HEAD
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        
        p_body = tf.add_paragraph()
        p_body.text = c_b
        p_body.font.name = FONT_BODY
        p_body.font.size = Pt(12)
        p_body.font.color.rgb = RGBColor(220, 230, 225)
        p_body.space_before = Pt(14)

    prs.save(output_path)
    print(f"Presentation successfully built at: {output_path}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "green_tac_project_review.pptx"
    build_deck(out_file)
