"""
PolyArt Meta-Language v1.0
A declarative DSL for generating polynomial art.

Grammar:
  program     := statement*
  statement   := command | assignment | loop | if | function_def | comment
  command     := IDENTIFIER '(' args? ')' ';'
  assignment  := IDENTIFIER '=' expression ';'
  loop        := 'repeat' NUMBER '{' program '}'
  if          := 'if' condition '{' program '}'
  function_def:= 'def' IDENTIFIER '(' params? ')' '{' program '}'
  comment     := '#' ... '\n'

  expression  := NUMBER | STRING | IDENTIFIER | expression OP expression | '(' expression ')'
  args        := expression (',' expression)*
  condition   := expression COMP_OP expression
  OP          := '+' | '-' | '*' | '/' | '%' | '..'
  COMP_OP     := '==' | '!=' | '<' | '>' | '<=' | '>='
"""

import re
import sys
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import warnings
warnings.filterwarnings("ignore")


# ============================================================
#  TOKENIZER
# ============================================================

TOKEN_SPEC = [
    ("NUMBER",    r"\d+\.?\d*"),
    ("STRING",    r'"[^"]*"'),
    ("IDENT",     r"\$[A-Za-z_][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*"),
    ("OP",        r"\.\.|\+|\-|\*|\/|%"),
    ("COMP",      r"==|!=|<=|>=|<|>"),
    ("ASSIGN",    r"="),
    ("LPAREN",    r"\("),
    ("RPAREN",    r"\)"),
    ("LBRACE",    r"\{"),
    ("RBRACE",    r"\}"),
    ("SEMI",      r";"),
    ("COMMA",     r","),
    ("DOT",       r"\."),
    ("NEWLINE",   r"\n"),
    ("SKIP",      r"[ \t]+"),
    ("COMMENT",   r"#[^\n]*"),
]

MASTER_PATTERN = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC))


class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, L{self.line})"


def tokenize(source):
    tokens = []
    line = 1
    for m in MASTER_PATTERN.finditer(source):
        kind = m.lastgroup
        value = m.group()
        if kind == "NEWLINE":
            line += 1
        elif kind == "SKIP" or kind == "COMMENT":
            continue
        elif kind == "STRING":
            value = value[1:-1]
        elif kind == "NUMBER":
            value = float(value) if "." in value else int(value)
        tokens.append(Token(kind, value, line))
    tokens.append(Token("EOF", None, line))
    return tokens


# ============================================================
#  AST NODES
# ============================================================

class ASTNode:
    pass

class CommandNode(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class AssignNode(ASTNode):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class BinOpNode(ASTNode):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class UnaryOpNode(ASTNode):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value

class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value

class VarNode(ASTNode):
    def __init__(self, name):
        self.name = name

class LoopNode(ASTNode):
    def __init__(self, count, body):
        self.count = count
        self.body = body

class IfNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class FuncDefNode(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class FuncCallNode(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class ListNode(ASTNode):
    def __init__(self, elements):
        self.elements = elements


# ============================================================
#  PARSER
# ============================================================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == "NEWLINE":
            self.pos += 1
        return self.tokens[min(self.pos, len(self.tokens) - 1)]

    def advance(self):
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == "NEWLINE":
            self.pos += 1
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, type_):
        tok = self.advance()
        if tok.type != type_:
            raise SyntaxError(f"Expected {type_}, got {tok.type} ({tok.value!r}) at line {tok.line}")
        return tok

    def parse(self):
        stmts = []
        while self.peek().type != "EOF":
            stmts.append(self.parse_statement())
        return stmts

    def parse_statement(self):
        tok = self.peek()
        if tok.type == "COMMENT":
            self.advance()
            return self.parse_statement()
        if tok.type == "IDENT" and tok.value == "repeat":
            return self.parse_loop()
        if tok.type == "IDENT" and tok.value == "if":
            return self.parse_if()
        if tok.type == "IDENT" and tok.value == "def":
            return self.parse_func_def()
        if tok.type == "IDENT" and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == "ASSIGN":
            return self.parse_assign()
        return self.parse_command()

    def parse_loop(self):
        self.expect("IDENT")  # 'repeat'
        count = self.parse_expr()
        self.expect("LBRACE")
        body = []
        while self.peek().type != "RBRACE":
            body.append(self.parse_statement())
        self.expect("RBRACE")
        return LoopNode(count, body)

    def parse_if(self):
        self.expect("IDENT")  # 'if'
        cond = self.parse_condition()
        self.expect("LBRACE")
        body = []
        while self.peek().type != "RBRACE":
            body.append(self.parse_statement())
        self.expect("RBRACE")
        return IfNode(cond, body)

    def parse_func_def(self):
        self.expect("IDENT")  # 'def'
        name = self.expect("IDENT").value
        self.expect("LPAREN")
        params = []
        if self.peek().type != "RPAREN":
            params.append(self.expect("IDENT").value)
            while self.peek().type == "COMMA":
                self.advance()
                params.append(self.expect("IDENT").value)
        self.expect("RPAREN")
        self.expect("LBRACE")
        body = []
        while self.peek().type != "RBRACE":
            body.append(self.parse_statement())
        self.expect("RBRACE")
        return FuncDefNode(name, params, body)

    def parse_assign(self):
        name = self.expect("IDENT").value
        self.expect("ASSIGN")
        expr = self.parse_expr()
        self.expect("SEMI")
        return AssignNode(name, expr)

    def parse_command(self):
        name = self.expect("IDENT").value
        self.expect("LPAREN")
        args = []
        if self.peek().type != "RPAREN":
            args.append(self.parse_expr())
            while self.peek().type == "COMMA":
                self.advance()
                args.append(self.parse_expr())
        self.expect("RPAREN")
        self.expect("SEMI")
        return CommandNode(name, args)

    def parse_condition(self):
        left = self.parse_expr()
        op_tok = self.advance()
        if op_tok.type != "COMP":
            raise SyntaxError(f"Expected comparison operator, got {op_tok.type} at line {op_tok.line}")
        right = self.parse_expr()
        return BinOpNode(op_tok.value, left, right)

    def parse_expr(self):
        return self.parse_additive()

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.peek().type == "OP" and self.peek().value in ("+", "-", ".."):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = BinOpNode(op, left, right)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.peek().type == "OP" and self.peek().value in ("*", "/", "%"):
            op = self.advance().value
            right = self.parse_unary()
            left = BinOpNode(op, left, right)
        return left

    def parse_unary(self):
        if self.peek().type == "OP" and self.peek().value in ("-", "+"):
            op = self.advance().value
            operand = self.parse_primary()
            return UnaryOpNode(op, operand)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()
        if tok.type == "NUMBER":
            self.advance()
            return NumberNode(tok.value)
        if tok.type == "STRING":
            self.advance()
            return StringNode(tok.value)
        if tok.type == "IDENT":
            name = self.advance().value
            if self.peek().type == "LPAREN":
                self.advance()
                args = []
                if self.peek().type != "RPAREN":
                    args.append(self.parse_expr())
                    while self.peek().type == "COMMA":
                        self.advance()
                        args.append(self.parse_expr())
                self.expect("RPAREN")
                return FuncCallNode(name, args)
            if self.peek().type == "LBRACE":
                self.advance()
                elems = []
                if self.peek().type != "RBRACE":
                    elems.append(self.parse_expr())
                    while self.peek().type == "COMMA":
                        self.advance()
                        elems.append(self.parse_expr())
                self.expect("RBRACE")
                return ListNode(elems)
            return VarNode(name)
        if tok.type == "LPAREN":
            self.advance()
            expr = self.parse_expr()
            self.expect("RPAREN")
            return expr
        raise SyntaxError(f"Unexpected token {tok.type} ({tok.value!r}) at line {tok.line}")


# ============================================================
#  INTERPRETER
# ============================================================

class Interpreter:
    def __init__(self):
        self.vars = {}
        self.funcs = {}
        self.fig = None
        self.ax = None
        self._output_path = "output.png"
        self._width = 10
        self._height = 10
        self._bg = "#0d0a1a"
        self._dpi = 150
        self._xlim = (-5, 5)
        self._ylim = (-5, 5)
        self._init_fig()

    def _init_fig(self):
        if self.fig:
            plt.close(self.fig)
        self.fig, self.ax = plt.subplots(1, 1, figsize=(self._width, self._height), dpi=self._dpi)
        self.fig.patch.set_facecolor(self._bg)
        self.ax.set_facecolor(self._bg)
        self.ax.set_xlim(*self._xlim)
        self.ax.set_ylim(*self._ylim)
        self.ax.set_aspect("equal")
        self.ax.axis("off")

    def run(self, nodes):
        for node in nodes:
            self.exec_node(node)

    def exec_node(self, node):
        if isinstance(node, CommandNode):
            self.exec_command(node)
        elif isinstance(node, AssignNode):
            self.vars[node.name] = self.eval_expr(node.expr)
        elif isinstance(node, LoopNode):
            count = int(self.eval_expr(node.count))
            for i in range(count):
                self.vars["$i"] = i
                self.exec_node_list(node.body)
        elif isinstance(node, IfNode):
            if self.eval_condition(node.condition):
                self.exec_node_list(node.body)
        elif isinstance(node, FuncDefNode):
            self.funcs[node.name] = node
        elif isinstance(node, FuncCallNode):
            self.eval_expr(node)

    def exec_node_list(self, nodes):
        for n in nodes:
            self.exec_node(n)

    def eval_expr(self, node):
        if isinstance(node, NumberNode):
            return node.value
        if isinstance(node, StringNode):
            return node.value
        if isinstance(node, VarNode):
            return self.vars.get(node.name, 0)
        if isinstance(node, BinOpNode):
            l = self.eval_expr(node.left)
            r = self.eval_expr(node.right)
            if node.op == "+": return l + r
            if node.op == "-": return l - r
            if node.op == "*": return l * r
            if node.op == "/": return l / r if r != 0 else 0
            if node.op == "%": return l % r if r != 0 else 0
            if node.op == "..":
                return [float(l + (r - l) * i / max(1, int(r - l) * 10)) for i in range(int(abs(r - l) * 10 + 1))]
        if isinstance(node, UnaryOpNode):
            val = self.eval_expr(node.operand)
            if node.op == "-": return -val
            if node.op == "+": return val
        if isinstance(node, FuncCallNode):
            return self.call_func(node.name, [self.eval_expr(a) for a in node.args])
        if isinstance(node, ListNode):
            return [self.eval_expr(e) for e in node.elements]
        return 0

    def eval_condition(self, node):
        l = self.eval_expr(node.left)
        r = self.eval_expr(node.right)
        if node.op == "==": return l == r
        if node.op == "!=": return l != r
        if node.op == "<": return l < r
        if node.op == ">": return l > r
        if node.op == "<=": return l <= r
        if node.op == ">=": return l >= r
        return False

    def call_func(self, name, args):
        if name in self.funcs:
            f = self.funcs[name]
            saved = dict(self.vars)
            for i, p in enumerate(f.params):
                self.vars[p] = args[i] if i < len(args) else 0
            self.exec_node_list(f.body)
            result = self.vars.get("_return", 0)
            self.vars = saved
            return result
        return self.builtin(name, args)

    # ============================================================
    #  BUILT-IN COMMANDS
    # ============================================================

    def exec_command(self, node):
        name = node.name
        args = [self.eval_expr(a) for a in node.args]
        self.builtin(name, args)

    def builtin(self, name, args):
        a = args

        # --- Canvas ---
        if name == "canvas":
            self._width = a[0] if len(a) > 0 else 10
            self._height = a[1] if len(a) > 1 else 10
            self._bg = a[2] if len(a) > 2 else "#0d0a1a"
            self._init_fig()
            return

        if name == "xlim":
            self._xlim = (a[0], a[1])
            self.ax.set_xlim(*self._xlim)
            return
        if name == "ylim":
            self._ylim = (a[0], a[1])
            self.ax.set_ylim(*self._ylim)
            return
        if name == "dpi":
            self._dpi = int(a[0])
            return
        if name == "output":
            self._output_path = str(a[0])
            return

        # --- Primitives ---
        if name == "circle":
            cx, cy, r = (a + [0, 0, 1])[:3]
            fill = len(a) > 3 and a[3]
            fc = a[4] if len(a) > 4 else "#c8a040"
            fa = a[5] if len(a) > 5 else 1.0
            ec = a[6] if len(a) > 6 else "#c8a040"
            ew = a[7] if len(a) > 7 else 0.5
            if fill:
                circ = plt.Circle((cx, cy), r, facecolor=fc, alpha=fa, edgecolor=ec, linewidth=ew)
                self.ax.add_patch(circ)
            else:
                th = np.linspace(0, 2*np.pi, 100)
                self.ax.plot(cx + r*np.cos(th), cy + r*np.sin(th), color=ec, linewidth=ew, alpha=fa)
            return

        if name == "oval":
            cx, cy, rx, ry = (a + [0, 0, 1, 1])[:4]
            fill = len(a) > 4 and a[4]
            fc = a[5] if len(a) > 5 else "#c8a040"
            fa = a[6] if len(a) > 6 else 1.0
            ec = a[7] if len(a) > 7 else "#c8a040"
            ew = a[8] if len(a) > 8 else 0.5
            th = np.linspace(0, 2*np.pi, 120)
            ox = cx + rx * np.cos(th)
            oy = cy + ry * np.sin(th)
            if fill:
                self.ax.fill(ox, oy, color=fc, alpha=fa, edgecolor=ec, linewidth=ew)
            else:
                self.ax.plot(ox, oy, color=ec, linewidth=ew, alpha=fa)
            return

        if name == "line":
            x1, y1, x2, y2 = (a + [0, 0, 0, 0])[:4]
            c = a[4] if len(a) > 4 else "#c8a040"
            lw = a[5] if len(a) > 5 else 0.5
            al = a[6] if len(a) > 6 else 1.0
            self.ax.plot([x1, x2], [y1, y2], color=c, linewidth=lw, alpha=al)
            return

        if name == "rect":
            x, y, w, h = (a + [0, 0, 1, 1])[:4]
            fc = a[4] if len(a) > 4 else "#c8a040"
            ec = a[5] if len(a) > 5 else "#c8a040"
            lw = a[6] if len(a) > 6 else 0.5
            al = a[7] if len(a) > 7 else 1.0
            r = plt.Rectangle((x - w/2, y - h/2), w, h, facecolor=fc, edgecolor=ec, linewidth=lw, alpha=al)
            self.ax.add_patch(r)
            return

        if name == "polygon":
            pts = a[0] if a and isinstance(a[0], list) else a
            fc = a[1] if len(a) > 1 and isinstance(a[1], str) else "#c8a040"
            ec = a[2] if len(a) > 2 and isinstance(a[2], str) else "#c8a040"
            if pts and isinstance(pts[0], (list, tuple)):
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
            else:
                xs = pts[::2]
                ys = pts[1::2]
            self.ax.fill(xs, ys, color=fc, edgecolor=ec, linewidth=0.5)
            return

        # --- Curves ---
        if name == "spiral":
            cx, cy, a_val, turns = (a + [0, 0, 0.1, 3])[:4]
            c = a[4] if len(a) > 4 else "#c8a040"
            lw = a[5] if len(a) > 5 else 0.5
            n = int(a[6]) if len(a) > 6 else 200
            th = np.linspace(0, turns * 2 * np.pi, n)
            r = a_val * np.exp(0.3063 * th)
            self.ax.plot(cx + r*np.cos(th), cy + r*np.sin(th), color=c, linewidth=lw)
            return

        if name == "bezier":
            pts = a[0] if a and isinstance(a[0], list) else [(a[i], a[i+1]) for i in range(0, len(a)-1, 2)]
            c = a[1] if len(a) > 1 and isinstance(a[1], str) else "#c8a040"
            lw = a[2] if len(a) > 2 and isinstance(a[2], (int, float)) else 0.5
            n = int(a[3]) if len(a) > 3 else 100
            if len(pts) < 2:
                return
            from matplotlib.path import Path
            verts = [pts[0]]
            codes = [Path.MOVETO]
            for i in range(1, len(pts)):
                verts.append(pts[i])
                codes.append(Path.CURVE3 if i % 2 == 1 else Path.CURVE3)
            path = Path(verts, codes)
            patch = mpath.PathPatch(path, facecolor="none", edgecolor=c, linewidth=lw)
            self.ax.add_patch(patch)
            return

        if name == "sine":
            x1, x2, amp, freq = (a + [0, 5, 1, 1])[:4]
            cy = a[4] if len(a) > 4 else 0
            c = a[5] if len(a) > 5 else "#c8a040"
            lw = a[6] if len(a) > 6 else 0.5
            x = np.linspace(x1, x2, 200)
            y = cy + amp * np.sin(freq * x)
            self.ax.plot(x, y, color=c, linewidth=lw)
            return

        if name == "cosine":
            x1, x2, amp, freq = (a + [0, 5, 1, 1])[:4]
            cy = a[4] if len(a) > 4 else 0
            c = a[5] if len(a) > 5 else "#c8a040"
            lw = a[6] if len(a) > 6 else 0.5
            x = np.linspace(x1, x2, 200)
            y = cy + amp * np.cos(freq * x)
            self.ax.plot(x, y, color=c, linewidth=lw)
            return

        # --- Patterns ---
        if name == "greek_meander":
            cx, cy, w, h = (a + [0, 0, 2, 1])[:4]
            c = a[4] if len(a) > 4 else "#c8a040"
            lw = a[5] if len(a) > 5 else 0.5
            steps = 8
            dx = w / steps
            pts_x = []
            pts_y = []
            for i in range(steps):
                x = cx - w/2 + i * dx
                pts_x.extend([x, x, x + dx, x + dx])
                pts_y.extend([cy - h/2, cy + h/2, cy + h/2, cy - h/2])
            self.ax.plot(pts_x, pts_y, color=c, linewidth=lw)
            return

        if name == "greek_volute":
            cx, cy, a_val = (a + [0, 0, 0.3])[:3]
            c = a[3] if len(a) > 3 else "#c8a040"
            lw = a[4] if len(a) > 4 else 0.5
            th = np.linspace(0, 4*np.pi, 200)
            r = a_val * (1 - th / (4*np.pi))
            self.ax.plot(cx + r*np.cos(th), cy + r*np.sin(th), color=c, linewidth=lw)
            return

        if name == "roman_arch":
            cx, cy, w, h = (a + [0, 0, 2, 3])[:4]
            c = a[4] if len(a) > 4 else "#c8a040"
            lw = a[5] if len(a) > 5 else 0.5
            th = np.linspace(0, np.pi, 60)
            self.ax.plot(cx + (w/2)*np.cos(th), cy + h + (h*0.6)*np.sin(th), color=c, linewidth=lw)
            self.ax.plot([cx - w/2, cx - w/2], [cy, cy + h], color=c, linewidth=lw)
            self.ax.plot([cx + w/2, cx + w/2], [cy, cy + h], color=c, linewidth=lw)
            return

        if name == "golden_rect":
            cx, cy, w = (a + [0, 0, 2])[:3]
            c = a[3] if len(a) > 3 else "#c8a040"
            PHI = (1 + math.sqrt(5)) / 2
            h = w / PHI
            r = plt.Rectangle((cx - w/2, cy - h/2), w, h, fill=False, edgecolor=c, linewidth=0.5)
            self.ax.add_patch(r)
            return

        if name == "golden_spiral":
            cx, cy, a_val, turns = (a + [0, 0, 0.05, 3])[:4]
            c = a[4] if len(a) > 4 else "#c8a040"
            lw = a[5] if len(a) > 5 else 0.5
            th = np.linspace(0, turns * 2 * np.pi, 300)
            r = a_val * np.exp(0.3063 * th)
            self.ax.plot(cx + r*np.cos(th), cy + r*np.sin(th), color=c, linewidth=lw)
            return

        # --- Grid / Background ---
        if name == "grid":
            spacing = a[0] if len(a) > 0 else 1
            c = a[1] if len(a) > 1 else "#c8a040"
            al = a[2] if len(a) > 2 else 0.1
            xmin, xmax = self._xlim
            ymin, ymax = self._ylim
            for x in np.arange(xmin, xmax + spacing, spacing):
                self.ax.plot([x, x], [ymin, ymax], color=c, linewidth=0.1, alpha=al)
            for y in np.arange(ymin, ymax + spacing, spacing):
                self.ax.plot([xmin, xmax], [y, y], color=c, linewidth=0.1, alpha=al)
            return

        if name == "rays":
            cx, cy, n_rays, length = (a + [0, 0, 12, 5])[:4]
            c = a[4] if len(a) > 4 else "#c8a040"
            al = a[5] if len(a) > 5 else 0.1
            lw = a[6] if len(a) > 6 else 0.3
            for i in range(int(n_rays)):
                ang = i * 2 * math.pi / n_rays
                self.ax.plot([cx, cx + length*math.cos(ang)],
                             [cy, cy + length*math.sin(ang)],
                             color=c, linewidth=lw, alpha=al)
            return

        # --- Biology ---
        if name == "phyllotaxis":
            n = int(a[0]) if len(a) > 0 else 100
            sc = a[1] if len(a) > 1 else 1.0
            cx, cy = (a + [0, 0])[2:4]
            c = a[4] if len(a) > 4 else "#c8a040"
            for i in range(int(n)):
                ang = i * 2 * math.pi / ((1 + math.sqrt(5)) / 2)
                r = sc * math.sqrt(i) * 0.1
                self.ax.plot(cx + r*math.cos(ang), cy + r*math.sin(ang),
                             "o", color=c, markersize=1.5, alpha=0.7)
            return

        if name == "turing_spots":
            cx, cy, size = (a + [0, 0, 2])[:3]
            c = a[3] if len(a) > 3 else "#2a6a1a"
            n = int(a[4]) if len(a) > 4 else 30
            np.random.seed(42)
            for _ in range(int(n)):
                x = cx + np.random.uniform(-size, size)
                y = cy + np.random.uniform(-size, size)
                r = np.random.uniform(0.05, 0.2)
                circ = plt.Circle((x, y), r, color=c, alpha=0.6)
                self.ax.add_patch(circ)
            return

        # --- Emotions ---
        if name == "emotion":
            emotion = str(a[0]) if a else "joy"
            cx, cy, sc = (a + [0, 0, 1])[1:4]
            self._draw_emotion(emotion, cx, cy, sc)
            return

        if name == "state":
            state = str(a[0]) if a else "calm"
            cx, cy, sc = (a + [0, 0, 1])[1:4]
            self._draw_state(state, cx, cy, sc)
            return

        # --- Animals ---
        if name == "animal":
            animal = str(a[0]) if a else "lion"
            cx, cy, sc = (a + [0, 0, 1])[1:4]
            self._draw_animal(animal, cx, cy, sc)
            return

        # --- Text ---
        if name == "text":
            x, y, txt = (a + [0, 0, ""])[0:3]
            fs = int(a[3]) if len(a) > 3 else 12
            c = a[4] if len(a) > 4 else "#c8a040"
            al = a[5] if len(a) > 5 else 1.0
            fw = a[6] if len(a) > 6 else "normal"
            self.ax.text(x, y, str(txt), fontsize=fs, color=c, alpha=al,
                        ha="center", va="center", fontweight=fw, fontfamily="serif")
            return

        # --- Render ---
        if name == "render":
            path = str(a[0]) if a else self._output_path
            dpi = int(a[1]) if len(a) > 1 else self._dpi
            self.fig.savefig(path, dpi=dpi, bbox_inches="tight",
                           facecolor=self._bg, edgecolor="none", pad_inches=0.2)
            print(f"[OK] Saved: {path}")
            return

        if name == "show":
            plt.show()
            return

        # --- Utility ---
        if name == "print":
            print(" ".join(str(x) for x in a))
            return

        if name == "sin":
            return math.sin(a[0]) if a else 0
        if name == "cos":
            return math.cos(a[0]) if a else 0
        if name == "sqrt":
            return math.sqrt(a[0]) if a else 0
        if name == "pow":
            return math.pow(a[0], a[1]) if len(a) >= 2 else 0
        if name == "pi":
            return math.pi
        if name == "phi":
            return (1 + math.sqrt(5)) / 2
        if name == "abs":
            return abs(a[0]) if a else 0
        if name == "rand":
            return np.random.uniform(a[0], a[1]) if len(a) >= 2 else np.random.random()
        if name == "len":
            return len(a[0]) if a and isinstance(a[0], (list, str)) else 0
        if name == "int":
            return int(a[0]) if a else 0
        if name == "float":
            return float(a[0]) if a else 0.0

        print(f"[WARN] Unknown command: {name}")
        return 0

    # ============================================================
    #  EMOTION BODY DRAWING
    # ============================================================

    def _draw_emotion(self, emotion, cx, cy, s):
        emotions = {
            "joy": self._emotion_joy,
            "sorrow": self._emotion_sorrow,
            "anger": self._emotion_anger,
            "fear": self._emotion_fear,
            "love": self._emotion_love,
            "surprise": self._emotion_surprise,
            "calm": self._emotion_calm,
            "pride": self._emotion_pride,
        }
        fn = emotions.get(emotion, self._emotion_joy)
        fn(cx, cy, s)

    def _draw_oval(self, cx, cy, rx, ry, fc="#d4a574", ec="#c8a040", lw=0.3, al=1.0):
        th = np.linspace(0, 2*np.pi, 60)
        self.ax.fill(cx + rx*np.cos(th), cy + ry*np.sin(th), color=fc, alpha=al)
        self.ax.plot(cx + rx*np.cos(th), cy + ry*np.sin(th), color=ec, linewidth=lw, alpha=al)

    def _emotion_joy(self, cx, cy, s):
        self._draw_oval(cx, cy + 5.5*s, 0.8*s, 1.0*s)
        th = np.linspace(-0.4*s, 0.4*s, 30)
        self.ax.plot(cx + th, cy + 5.1*s + 0.15*s*np.sin(np.pi*th/(0.8*s)), color="#8b4020", linewidth=0.8)
        for ex in [cx - 0.25*s, cx + 0.25*s]:
            self.ax.plot(ex, cy + 5.7*s, "o", color="#2a1a0a", markersize=2)
        self.ax.plot([cx - 0.5*s, cx - 2*s], [cy + 4.5*s, cy + 7*s], color="#d4a574", linewidth=3)
        self.ax.plot([cx + 0.5*s, cx + 2*s], [cy + 4.5*s, cy + 7*s], color="#d4a574", linewidth=3)
        self.ax.plot([cx, cx], [cy + 4.5*s, cy + 2*s], color="#d4a574", linewidth=5)
        self.ax.plot([cx, cx - 0.5*s], [cy + 2*s, cy], color="#d4a574", linewidth=3)
        self.ax.plot([cx, cx + 0.5*s], [cy + 2*s, cy], color="#d4a574", linewidth=3)

    def _emotion_sorrow(self, cx, cy, s):
        self._draw_oval(cx, cy + 4.5*s, 0.8*s, 1.0*s)
        th = np.linspace(-0.3*s, 0.3*s, 30)
        self.ax.plot(cx + th, cy + 4.1*s - 0.1*s*np.sin(np.pi*th/(0.6*s)), color="#8b4020", linewidth=0.8)
        self.ax.plot([cx, cx + 0.3*s], [cy + 4.5*s, cy + 2*s], color="#d4a574", linewidth=5, alpha=0.85)
        self.ax.plot([cx - 0.3*s, cx - 0.6*s], [cy + 4*s, cy + 1.5*s], color="#d4a574", linewidth=2.5)
        self.ax.plot([cx + 0.3*s, cx + 0.5*s], [cy + 4*s, cy + 1.5*s], color="#d4a574", linewidth=2.5)

    def _emotion_anger(self, cx, cy, s):
        self._draw_oval(cx + 0.2*s, cy + 5.5*s, 0.8*s, 1.0*s)
        self.ax.plot([cx - 0.3*s, cx], [cy + 5.9*s, cy + 5.7*s], color="#5a3a20", linewidth=1)
        self.ax.plot([cx + 0.7*s, cx + 0.4*s], [cy + 5.9*s, cy + 5.7*s], color="#5a3a20", linewidth=1)
        self.ax.plot([cx + 0.2*s, cx + 0.2*s], [cy + 4.5*s, cy + 2*s], color="#d4a574", linewidth=5)
        self.ax.plot([cx - 0.3*s, cx - 1*s], [cy + 4.5*s, cy + 3.5*s], color="#d4a574", linewidth=3)
        self.ax.plot([cx + 0.7*s, cx + 1.2*s], [cy + 4.5*s, cy + 3.5*s], color="#d4a574", linewidth=3)
        self.ax.plot([cx + 0.2*s, cx - 0.7*s], [cy + 2*s, cy], color="#d4a574", linewidth=3)
        self.ax.plot([cx + 0.2*s, cx + 1.1*s], [cy + 2*s, cy], color="#d4a574", linewidth=3)

    def _emotion_fear(self, cx, cy, s):
        self._draw_oval(cx - 0.3*s, cy + 5.5*s, 0.8*s, 1.0*s)
        for ex in [cx - 0.5*s, cx - 0.1*s]:
            self._draw_oval(ex, cy + 5.7*s, 0.12*s, 0.1*s, fc="#ffffff", ec="#5a3a20", lw=0.3)
            self.ax.plot(ex, cy + 5.7*s, "o", color="#1a0a05", markersize=1.5)
        self.ax.plot([cx - 0.3*s, cx - 1.2*s], [cy + 4.5*s, cy + 5.5*s], color="#d4a574", linewidth=2.5)
        self.ax.plot([cx + 0.3*s, cx + 0.8*s], [cy + 4.5*s, cy + 5.5*s], color="#d4a574", linewidth=2.5)
        self.ax.plot([cx - 0.3*s, cx - 0.3*s], [cy + 4.5*s, cy + 2*s], color="#d4a574", linewidth=5, alpha=0.85)

    def _emotion_love(self, cx, cy, s):
        self._draw_oval(cx + 0.1*s, cy + 5.5*s, 0.8*s, 1.0*s)
        self.ax.plot([cx + 0.3*s, cx + 0.2*s], [cy + 4.5*s, cy + 3.8*s], color="#d4a574", linewidth=2.5)
        self.ax.plot([cx - 0.3*s, cx - 1*s], [cy + 4.5*s, cy + 3.5*s], color="#d4a574", linewidth=2, alpha=0.8)
        self.ax.plot([cx, cx], [cy + 4.5*s, cy + 2*s], color="#d4a574", linewidth=5, alpha=0.85)
        # Heart
        th = np.linspace(0, 2*np.pi, 100)
        hx = 0.16 * (16 * np.sin(th)**3)
        hy = 0.16 * (13*np.cos(th) - 5*np.cos(2*th) - 2*np.cos(3*th) - np.cos(4*th))
        self.ax.plot(cx + 0.2*s + hx*s, cy + 3.5*s + hy*s, color="#ff4060", linewidth=1, alpha=0.7)

    def _emotion_surprise(self, cx, cy, s):
        self._draw_oval(cx, cy + 6*s, 0.8*s, 1.0*s)
        for ex in [cx - 0.25*s, cx + 0.25*s]:
            self._draw_oval(ex, cy + 6.2*s, 0.12*s, 0.1*s, fc="#ffffff", ec="#5a3a20", lw=0.3)
            self.ax.plot(ex, cy + 6.2*s, "o", color="#1a0a05", markersize=1.5)
        self._draw_oval(cx, cy + 5.7*s, 0.12*s, 0.15*s, fc="#3a1010", ec="#8b4020", lw=0.3)
        self.ax.plot([cx - 0.5*s, cx - 1.5*s], [cy + 4.5*s, cy + 7*s], color="#d4a574", linewidth=2.5)
        self.ax.plot([cx + 0.5*s, cx + 1.5*s], [cy + 4.5*s, cy + 7*s], color="#d4a574", linewidth=2.5)
        self.ax.plot([cx, cx], [cy + 5*s, cy + 2.5*s], color="#d4a574", linewidth=5, alpha=0.85)

    def _emotion_calm(self, cx, cy, s):
        self._draw_oval(cx, cy + 5*s, 0.8*s, 1.0*s)
        for ex in [cx - 0.25*s, cx + 0.25*s]:
            self.ax.plot([ex - 0.08*s, ex + 0.08*s], [cy + 5.2*s, cy + 5.2*s], color="#5a3a20", linewidth=0.8)
        self.ax.plot([cx, cx], [cy + 4.2*s, cy + 2.5*s], color="#d4a574", linewidth=5, alpha=0.85)
        self.ax.plot([cx - 0.3*s, cx - 1*s], [cy + 4.2*s, cy + 2.5*s], color="#d4a574", linewidth=2)
        self.ax.plot([cx + 0.3*s, cx + 1*s], [cy + 4.2*s, cy + 2.5*s], color="#d4a574", linewidth=2)
        self.ax.plot([cx, cx - 0.8*s], [cy + 2.5*s, cy + 1.8*s], color="#d4a574", linewidth=3)
        self.ax.plot([cx, cx + 0.8*s], [cy + 2.5*s, cy + 1.8*s], color="#d4a574", linewidth=3)

    def _emotion_pride(self, cx, cy, s):
        self._draw_oval(cx, cy + 5.8*s, 0.8*s, 1.0*s)
        self.ax.plot([cx, cx], [cy + 4.2*s, cy + 2*s], color="#d4a574", linewidth=5, alpha=0.85)
        self.ax.plot([cx - 0.8*s, cx - 1.2*s], [cy + 4.5*s, cy + 3*s], color="#d4a574", linewidth=2.5)
        self.ax.plot([cx + 0.8*s, cx + 1.2*s], [cy + 4.5*s, cy + 3*s], color="#d4a574", linewidth=2.5)
        self.ax.plot([cx, cx - 0.8*s], [cy + 2*s, cy], color="#d4a574", linewidth=3)
        self.ax.plot([cx, cx + 0.8*s], [cy + 2*s, cy], color="#d4a574", linewidth=3)

    # ============================================================
    #  ANIMAL BODY DRAWING
    # ============================================================

    def _draw_animal(self, animal, cx, cy, s):
        animals = {
            "lion": self._animal_lion, "eagle": self._animal_eagle,
            "wolf": self._animal_wolf, "horse": self._animal_horse,
            "snake": self._animal_snake, "bear": self._animal_bear,
            "dolphin": self._animal_dolphin, "owl": self._animal_owl,
            "dragon": self._animal_dragon,
        }
        fn = animals.get(animal, self._animal_lion)
        fn(cx, cy, s)

    def _animal_lion(self, cx, cy, s):
        th = np.linspace(0, 2*np.pi, 80)
        self.ax.fill(cx + 2.5*s*np.cos(th), cy + 2*s + 1.2*s*np.sin(th), color="#c8a040", alpha=0.9)
        for i in range(16):
            ang = i * 2*np.pi/16
            mx, my = cx + 1.8*s + 0.8*s*np.cos(ang), cy + 2.8*s + 0.8*s*np.sin(ang)
            self.ax.fill(mx + 0.5*s*np.cos(th), my + 0.5*s*np.sin(th), color="#b08030", alpha=0.5)
        self._draw_oval(cx + 2*s, cy + 3*s, 0.7*s, 0.6*s, fc="#c8a040")
        self.ax.plot(cx + 2*s, cy + 2.5*s, "o", color="#c8a040", markersize=3)

    def _animal_eagle(self, cx, cy, s):
        self._draw_oval(cx, cy + 3*s, 1*s, 0.6*s, fc="#3a2a1a")
        self._draw_oval(cx + 1*s, cy + 3.3*s, 0.4*s, 0.35*s, fc="#f0f0f0")
        wing_x = np.linspace(cx - 0.5*s, cx - 3.5*s, 40)
        wing_y = cy + 3.5*s + 1.5*s*np.sin(np.pi*(wing_x - cx + 0.5*s)/(-3*s))
        self.ax.plot(wing_x, wing_y, color="#3a2a1a", linewidth=2)
        wing_x2 = np.linspace(cx + 0.5*s, cx + 3.5*s, 40)
        wing_y2 = cy + 3.5*s + 1.5*s*np.sin(np.pi*(wing_x2 - cx - 0.5*s)/(3*s))
        self.ax.plot(wing_x2, wing_y2, color="#3a2a1a", linewidth=2)

    def _animal_wolf(self, cx, cy, s):
        self._draw_oval(cx, cy + 2.5*s, 2*s, 0.8*s, fc="#5a5a6a")
        self._draw_oval(cx + 1.8*s, cy + 3.8*s, 0.5*s, 0.5*s, fc="#6a6a7a")
        for lx in [cx - 1.2*s, cx - 0.4*s, cx + 0.4*s, cx + 1.2*s]:
            self.ax.plot([lx, lx], [cy + 1.7*s, cy], color="#5a5a6a", linewidth=2.5)

    def _animal_horse(self, cx, cy, s):
        self._draw_oval(cx, cy + 3*s, 2.5*s, 1*s, fc="#8b4513")
        self.ax.plot([cx + 1.5*s, cx + 2*s], [cy + 3.5*s, cy + 5*s], color="#8b4513", linewidth=5)
        self._draw_oval(cx + 2*s, cy + 5.2*s, 0.5*s, 0.35*s, fc="#8b4513")
        for lx in [cx - 1*s, cx, cx + 1*s, cx + 1.8*s]:
            self.ax.plot([lx, lx + 0.3*s], [cy + 2*s, cy], color="#8b4513", linewidth=3)

    def _animal_snake(self, cx, cy, s):
        t = np.linspace(0, 4*np.pi, 200)
        r = (0.5 + 0.3*t/(4*np.pi))*s
        self.ax.plot(cx + r*np.cos(t)*0.8, cy + r*np.sin(t)*0.4 + t*0.15*s,
                     color="#2a6a1a", linewidth=3)
        self._draw_oval(cx + 0.8*s, cy + 3.5*s, 0.3*s, 0.2*s, fc="#2a6a1a")

    def _animal_bear(self, cx, cy, s):
        self._draw_oval(cx, cy + 2.5*s, 2.5*s, 1.5*s, fc="#5a3a1a")
        self._draw_oval(cx + 2*s, cy + 3.5*s, 0.7*s, 0.6*s, fc="#5a3a1a")
        self.ax.plot(cx + 1.7*s, cy + 4.1*s, "o", color="#5a3a1a", markersize=6)
        self.ax.plot(cx + 2.3*s, cy + 4.1*s, "o", color="#5a3a1a", markersize=6)

    def _animal_dolphin(self, cx, cy, s):
        t = np.linspace(0, 1, 100)
        bx = cx + 3*s*(t - 0.5)
        by = cy + 2.5*s + 0.8*s*np.sin(np.pi*t)
        self.ax.fill(bx, by + 0.5*s*np.sin(np.pi*t), color="#4a6a8a", alpha=0.8)
        self.ax.plot(bx, by + 0.5*s*np.sin(np.pi*t), color="#4a6a8a", linewidth=2)
        self.ax.plot(bx, by - 0.4*s*np.sin(np.pi*t), color="#4a6a8a", linewidth=2)

    def _animal_owl(self, cx, cy, s):
        self._draw_oval(cx, cy + 2*s, 1.2*s, 1.5*s, fc="#8b7355")
        self._draw_oval(cx, cy + 3.8*s, 0.9*s, 0.8*s, fc="#8b7355")
        for ex in [cx - 0.35*s, cx + 0.35*s]:
            self._draw_oval(ex, cy + 3.9*s, 0.25*s, 0.25*s, fc="#f0e0c0", ec="#5a4a30", lw=0.3)
            self.ax.plot(ex, cy + 3.9*s, "o", color="#1a0a05", markersize=4)

    def _animal_dragon(self, cx, cy, s):
        t = np.linspace(0, 1, 80)
        bx = cx + 2*s*(t - 0.5)
        by = cy + 2.5*s + 0.6*s*np.sin(4*np.pi*t)
        self.ax.plot(bx, by, color="#8b2020", linewidth=4)
        self._draw_oval(cx + 2*s, cy + 2.8*s, 0.5*s, 0.35*s, fc="#8b2020")
        # Fire
        for i in range(8):
            fx = cx + 2.5*s + i*0.15*s
            fy = cy + 2.8*s + 0.3*s*np.sin(2*np.pi*i/5)*np.exp(-i*0.15)
            self.ax.plot(fx, fy, "o", color="#ff6020", markersize=3-i*0.3, alpha=0.7)
        wing = plt.Polygon([[cx+0.5*s, cy+3*s], [cx-1.5*s, cy+4.5*s], [cx-2*s, cy+4*s], [cx-1*s, cy+3.5*s]],
                           color="#8b2020", alpha=0.3)
        self.ax.add_patch(wing)

    def _draw_state(self, state, cx, cy, s):
        if state == "sleeping":
            self._draw_oval(cx - 2*s, cy + 1*s, 0.8*s, 0.7*s)
            self.ax.plot([cx - 2.2*s, cx - 1.8*s], [cy + 1.1*s, cy + 1.1*s], color="#5a3a20", linewidth=0.8)
            self.ax.plot([cx - 2*s, cx + 2*s], [cy + 0.5*s, cy + 0.5*s], color="#d4a574", linewidth=5, alpha=0.85)
        elif state == "running":
            self._draw_oval(cx + 0.5*s, cy + 5*s, 0.7*s, 0.9*s)
            self.ax.plot([cx + 0.5*s, cx + 0.5*s], [cy + 4.5*s, cy + 2*s], color="#d4a574", linewidth=5, alpha=0.9)
            self.ax.plot([cx + 0.5*s, cx + 1.5*s], [cy + 2*s, cy + 0.5*s], color="#d4a574", linewidth=3)
            self.ax.plot([cx + 0.5*s, cx - 0.8*s], [cy + 2*s, cy + 0.8*s], color="#d4a574", linewidth=3)
        elif state == "thinking":
            self._draw_oval(cx, cy + 5.5*s, 0.8*s, 1.0*s)
            self.ax.plot([cx + 0.3*s, cx + 0.2*s], [cy + 4.5*s, cy + 5*s], color="#d4a574", linewidth=2.5)
            self.ax.plot([cx, cx], [cy + 4.5*s, cy + 2*s], color="#d4a574", linewidth=5, alpha=0.85)
        elif state == "dancing":
            self._draw_oval(cx - 0.2*s, cy + 5.5*s, 0.7*s, 0.9*s)
            self.ax.plot([cx - 0.3*s, cx + 0.5*s], [cy + 4.5*s, cy + 7.5*s], color="#d4a574", linewidth=2.5)
            self.ax.plot([cx - 0.2*s, cx - 0.2*s], [cy + 4.5*s, cy + 2*s], color="#d4a574", linewidth=5, alpha=0.9)
            self.ax.plot([cx - 0.2*s, cx + 0.3*s], [cy + 2*s, cy], color="#d4a574", linewidth=3)


# ============================================================
#  MAIN API
# ============================================================

def run_source(source):
    tokens = tokenize(source)
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.run(ast)
    return interp

def run_file(path):
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    return run_source(source)


# ============================================================
#  CLI
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(f"[PolyArt Lang] Running: {path}")
        run_file(path)
        print("[DONE]")
    else:
        print("PolyArt Meta-Language v1.0")
        print("Usage: python polyart_lang.py <script.polyart>")
        print()
        print("Example script:")
        print('  canvas(10, 10, "#0d0a1a");')
        print('  golden_spiral(0, 0, 0.05, 4, "#c8a040", 0.5);')
        print('  circle(0, 0, 2, true, "#4a90d9", 0.3, "#c8a040", 0.3);')
        print('  emotion("joy", 0, 0, 0.8);')
        print('  animal("lion", 2, 0, 0.5);')
        print('  render("output.png", 200);')
