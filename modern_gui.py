
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch modern_gui.py to safely init fade_* Tk variables and guard on_ok().
Usage:
    python patch_modern_gui_vars.py [path/to/modern_gui.py]
"""
import sys, io, re, os

target = sys.argv[1] if len(sys.argv) > 1 else "modern_gui.py"
if not os.path.exists(target):
    print("File not found:", target)
    sys.exit(1)

with open(target, "r", encoding="utf-8", errors="ignore") as f:
    src = f.read()

changed = False

# Ensure tk import is present
if not re.search(r"\bimport\s+tkinter\s+as\s+tk\b", src):
    src = re.sub(r"(^from\s+tkinter\s+import\s+.*$)", r"import tkinter as tk\n\1", src, flags=re.M)
    if not re.search(r"\bfrom\s+tkinter\s+import\s+messagebox\b", src):
        src = "from tkinter import messagebox\n" + src
    changed = True

# Inject defaults dict and Var inits into the first __init__ of a class that looks like a dialog/GUI
init_pat = re.compile(r"(def\s+__init__\s*\(\s*self(?:,|\))[^\n]*\)\s*:\s*\n)(?P<body>(?:\s+.*\n)+?)\n\s*def\s+", re.M)
m = init_pat.search(src)
if m and "fade_sat_var" not in m.group("body"):
    inject = """
            # ---- safe Var defaults ----
            try:
                _ = self.fade_sat_var
            except AttributeError:
                defaults = {'fade_sat_drop': 50.0, 'fade_val_drop': 50.0, 'fade_start': 5, 'max_age': 60}
                self.fade_sat_var   = tk.DoubleVar(value=defaults['fade_sat_drop'])
                self.fade_val_var   = tk.DoubleVar(value=defaults['fade_val_drop'])
                self.fade_start_var = tk.IntVar(value=defaults['fade_start'])
                self.max_age_var    = tk.IntVar(value=defaults['max_age'])
    """
    body = m.group("body") + inject
    src = src[:m.start("body")] + body + src[m.end("body"):]
    changed = True

# Insert safe helpers and wrap on_ok
if "def _safe_float(" not in src:
    helpers = """

    def _safe_float(self, var, default=0.0):
        try:
            return float(var.get())
        except Exception:
            try:
                return float(var)
            except Exception:
                return float(default)

    def _safe_int(self, var, default=0):
        try:
            return int(var.get())
        except Exception:
            try:
                return int(var)
            except Exception:
                return int(default)
    """
    # Drop helpers before on_ok definition
    src = re.sub(r"\n(\s*)def\s+on_ok\s*\(", helpers + r"\n\1def on_ok(", src, count=1)
    changed = True

# Rewrite on_ok content to safely read values (minimal invasive).
on_ok_pat = re.compile(r"(def\s+on_ok\s*\(\s*self[^\)]*\)\s*:\s*\n)(?P<body>(?:\s+.*\n)+?)(?=\n\s*def\s+|\Z)", re.M)
m2 = on_ok_pat.search(src)
if m2 and "_safe_float(" not in m2.group("body"):
    body = m2.group("body")
    # Replace direct var.get() occurrences for known names
    repls = {
        r"fade_sat_var\.get\(\)": "self._safe_float(self.fade_sat_var, 50.0)",
        r"fade_val_var\.get\(\)": "self._safe_float(self.fade_val_var, 50.0)",
        r"fade_start_var\.get\(\)": "self._safe_int(self.fade_start_var, 5)",
        r"max_age_var\.get\(\)": "self._safe_int(self.max_age_var, 60)",
    }
    for pat, rep in repls.items():
        body = re.sub(pat, rep, body)
    src = src[:m2.start("body")] + body + src[m2.end("body"):]
    changed = True

if not changed:
    print("No changes were necessary.")
else:
    backup = target + ".bak"
    with open(backup, "w", encoding="utf-8") as f:
        f.write(src)
    # Write back to original file
    with open(target, "w", encoding="utf-8") as f:
        f.write(src)
    print("Patched:", target)
    print("Backup saved as:", backup)
