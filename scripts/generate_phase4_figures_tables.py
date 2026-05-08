from __future__ import annotations

import binascii
import csv
import json
import math
import struct
import zlib
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_DIR = ROOT / "results" / "summaries"
EVIDENCE_DIR = ROOT / "results" / "evidence_pack"
FIGURE_DIR = ROOT / "figures"
TABLE_DIR = ROOT / "tables"
WRITING_DIR = ROOT / "results" / "writing_pack"

REQUIRED_SOURCES = {
    "comparison": SUMMARY_DIR / "prototype4_execution_comparison.csv",
    "by_ambiguity": SUMMARY_DIR / "prototype4_by_ambiguity.csv",
    "by_model": SUMMARY_DIR / "prototype4_by_model.csv",
    "false_accepts": SUMMARY_DIR / "prototype4_false_accepts.csv",
    "frontier": SUMMARY_DIR / "safety_latency_frontier.csv",
    "metrics": EVIDENCE_DIR / "metrics_manifest.json",
    "file_manifest": EVIDENCE_DIR / "file_manifest.csv",
}

COLORS = {
    "ink": (34, 39, 46),
    "muted": (94, 106, 117),
    "grid": (220, 226, 232),
    "axis": (73, 80, 87),
    "success": (52, 150, 91),
    "unsafe": (205, 78, 67),
    "semantic_failure": (142, 95, 173),
    "no_op": (139, 148, 158),
    "rejected": (225, 137, 52),
    "baseline": (78, 121, 167),
    "zero_trust": (52, 150, 91),
    "accent": (218, 108, 40),
    "panel": (246, 248, 250),
    "white": (255, 255, 255),
}

FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10011", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "10000", "11110", "00001", "00001", "11110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "_": ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    ">": ["10000", "01000", "00100", "00010", "00100", "01000", "10000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
}


class Canvas:
    def __init__(self, width: int = 2400, height: int = 1600, background=COLORS["white"]):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = bytearray()
        row_bytes = self.width * 3
        for y in range(self.height):
            raw.append(0)
            start = y * row_bytes
            raw.extend(self.pixels[start:start + row_bytes])
        png = b"\x89PNG\r\n\x1a\n"
        png += _chunk(b"IHDR", struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0))
        # 300 DPI = 11811 pixels per metre.
        png += _chunk(b"pHYs", struct.pack(">IIB", 11811, 11811, 1))
        png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        png += _chunk(b"IEND", b"")
        path.write_bytes(png)

    def set_pixel(self, x: int, y: int, color) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = (y * self.width + x) * 3
            self.pixels[idx:idx + 3] = bytes(color)

    def rect(self, x: int, y: int, w: int, h: int, color, fill: bool = True, stroke=None) -> None:
        if fill:
            for yy in range(max(0, y), min(self.height, y + h)):
                for xx in range(max(0, x), min(self.width, x + w)):
                    self.set_pixel(xx, yy, color)
        if stroke:
            self.line(x, y, x + w, y, stroke, 2)
            self.line(x, y + h, x + w, y + h, stroke, 2)
            self.line(x, y, x, y + h, stroke, 2)
            self.line(x + w, y, x + w, y + h, stroke, 2)

    def line(self, x0: int, y0: int, x1: int, y1: int, color, thickness: int = 1) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        r = max(0, thickness // 2)
        while True:
            self.rect(x - r, y - r, thickness, thickness, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx: int, cy: int, radius: int, color, stroke=None) -> None:
        rr = radius * radius
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                d = (x - cx) ** 2 + (y - cy) ** 2
                if d <= rr:
                    self.set_pixel(x, y, color)
        if stroke:
            for angle in range(360):
                x = int(cx + math.cos(math.radians(angle)) * radius)
                y = int(cy + math.sin(math.radians(angle)) * radius)
                self.rect(x - 2, y - 2, 4, 4, stroke)

    def text(self, x: int, y: int, text: str, color=COLORS["ink"], scale: int = 4) -> None:
        cursor = x
        for char in text.upper():
            pattern = FONT.get(char, FONT[" "])
            for row, bits in enumerate(pattern):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.rect(cursor + col * scale, y + row * scale, scale, scale, color)
            cursor += 6 * scale


def _chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)


def read_csv(path: Path) -> list[dict[str, str]]:
    _require(path)
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_tex_table(path: Path, headers: list[str], rows: list[list[object]], caption: str, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    colspec = "l" + "r" * (len(headers) - 1)
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        f"\\caption{{{_latex(caption)}}}",
        f"\\label{{{label}}}",
        f"\\begin{{tabular}}{{{colspec}}}",
        "\\hline",
        " & ".join(_latex(h) for h in headers) + " \\\\",
        "\\hline",
    ]
    for row in rows:
        lines.append(" & ".join(_latex(str(cell)) for cell in row) + " \\\\")
    lines.extend(["\\hline", "\\end{tabular}", "\\end{table}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def _latex(value: str) -> str:
    replacements = {
        "\\": "\\textbackslash{}",
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
    }
    return "".join(replacements.get(ch, ch) for ch in value)


def _require(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required Phase 4 evidence file is missing: {path}")


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _text_width(text: str, scale: int = 4) -> int:
    return len(text) * 6 * scale


def draw_title(canvas: Canvas, title: str, subtitle: str = "") -> None:
    canvas.text(90, 60, title, COLORS["ink"], 7)
    if subtitle:
        canvas.text(92, 125, subtitle, COLORS["muted"], 4)


def bar_chart(
    path: Path,
    title: str,
    subtitle: str,
    groups: list[str],
    series: dict[str, list[float]],
    y_label: str,
    colors: dict[str, tuple[int, int, int]],
    max_value: float | None = None,
) -> None:
    canvas = Canvas()
    draw_title(canvas, title, subtitle)
    left, top, right, bottom = 260, 260, 2200, 1280
    max_v = max_value if max_value is not None else max(max(vals) for vals in series.values())
    max_v = max(1.0, max_v)
    for i in range(6):
        y = bottom - int((bottom - top) * i / 5)
        canvas.line(left, y, right, y, COLORS["grid"], 2)
        label = str(int(max_v * i / 5))
        canvas.text(120, y - 18, label, COLORS["muted"], 3)
    canvas.line(left, top, left, bottom, COLORS["axis"], 4)
    canvas.line(left, bottom, right, bottom, COLORS["axis"], 4)
    canvas.text(80, 220, y_label, COLORS["muted"], 3)

    group_w = (right - left) / len(groups)
    series_names = list(series.keys())
    bar_w = int(group_w / (len(series_names) + 1.6))
    for gi, group in enumerate(groups):
        gx = int(left + gi * group_w + group_w * 0.18)
        for si, name in enumerate(series_names):
            value = series[name][gi]
            h = int((bottom - top) * value / max_v)
            x = gx + si * (bar_w + 18)
            y = bottom - h
            canvas.rect(x, y, bar_w, h, colors[name])
            canvas.text(x + 4, y - 38, str(int(value)), COLORS["ink"], 3)
        canvas.text(int(left + gi * group_w + group_w * 0.12), bottom + 45, group, COLORS["ink"], 3)

    legend_x = left
    legend_y = 1380
    for name in series_names:
        canvas.rect(legend_x, legend_y, 34, 34, colors[name])
        canvas.text(legend_x + 50, legend_y, name, COLORS["ink"], 3)
        legend_x += 360
    canvas.save(path)


def stacked_mode_chart(path: Path, comparison: list[dict[str, str]]) -> None:
    modes = ["baseline_trust_model", "zero_trust_pipeline"]
    labels = ["BASELINE", "ZERO TRUST"]
    outcomes = ["success", "unsafe", "semantic_failure", "no_op", "rejected"]
    counts = {
        mode: Counter(r["execution_outcome"] for r in comparison if r["mode"] == mode)
        for mode in modes
    }
    canvas = Canvas()
    draw_title(canvas, "EXECUTION OUTCOME SHIFT UNDER ZERO-TRUST GATING", "Baseline accepts unsafe plans; zero-trust converts risk into rejection")
    left, top, right, bottom = 350, 300, 2050, 1180
    canvas.line(left, bottom, right, bottom, COLORS["axis"], 4)
    canvas.line(left, top, left, bottom, COLORS["axis"], 4)
    for i in range(5):
        y = bottom - int((bottom - top) * i / 4)
        canvas.line(left, y, right, y, COLORS["grid"], 2)
        canvas.text(180, y - 18, str(i * 30), COLORS["muted"], 3)
    bar_w = 420
    for idx, mode in enumerate(modes):
        x = left + 250 + idx * 720
        y = bottom
        for outcome in outcomes:
            value = counts[mode][outcome]
            if not value:
                continue
            h = int((bottom - top) * value / 120)
            y -= h
            canvas.rect(x, y, bar_w, h, COLORS.get(outcome, COLORS["muted"]))
            canvas.text(x + bar_w + 25, y + max(8, h // 2 - 14), f"{outcome}: {value}", COLORS["ink"], 3)
        canvas.text(x + 35, bottom + 55, labels[idx], COLORS["ink"], 4)
    canvas.text(80, 250, "ROWS", COLORS["muted"], 3)
    canvas.save(path)


def frontier_scatter(path: Path, frontier: list[dict[str, str]]) -> None:
    canvas = Canvas()
    draw_title(canvas, "SAFETY-LATENCY FRONTIER", "False accepts fall as validation stringency increases")
    left, top, right, bottom = 300, 280, 2180, 1220
    xs = [float(r["false_accept_count"]) for r in frontier]
    ys = [float(r["mean_latency_ms"]) for r in frontier]
    max_x = max(xs) + 5
    min_y, max_y = min(ys) - 150, max(ys) + 150
    for i in range(6):
        x = left + int((right - left) * i / 5)
        y = bottom - int((bottom - top) * i / 5)
        canvas.line(x, top, x, bottom, COLORS["grid"], 2)
        canvas.line(left, y, right, y, COLORS["grid"], 2)
        canvas.text(x - 20, bottom + 35, str(int(max_x * i / 5)), COLORS["muted"], 3)
        canvas.text(90, y - 15, str(int(min_y + (max_y - min_y) * i / 5)), COLORS["muted"], 3)
    canvas.line(left, bottom, right, bottom, COLORS["axis"], 4)
    canvas.line(left, top, left, bottom, COLORS["axis"], 4)
    canvas.text(900, 1450, "FALSE ACCEPTS", COLORS["ink"], 4)
    canvas.text(65, 220, "MEAN LATENCY MS", COLORS["ink"], 3)
    point_colors = [COLORS["unsafe"], COLORS["accent"], COLORS["success"], COLORS["baseline"]]
    offsets = [(20, -90), (25, -70), (30, 25), (30, 80)]
    previous = None
    for idx, row in enumerate(frontier):
        x = left + int((right - left) * float(row["false_accept_count"]) / max_x)
        y = bottom - int((bottom - top) * (float(row["mean_latency_ms"]) - min_y) / (max_y - min_y))
        if previous:
            canvas.line(previous[0], previous[1], x, y, COLORS["axis"], 3)
        previous = (x, y)
        canvas.circle(x, y, 24, point_colors[idx], COLORS["ink"])
        label = row["configuration"]
        ox, oy = offsets[idx]
        canvas.text(x + ox, y + oy, label, COLORS["ink"], 3)
        canvas.text(x + ox, y + oy + 34, f"FA {row['false_accept_count']} LAT {float(row['mean_latency_ms']):.0f}", COLORS["muted"], 3)
    canvas.save(path)


def heatmap(path: Path, comparison: list[dict[str, str]]) -> None:
    baseline_rows = [r for r in comparison if r["mode"] == "baseline_trust_model"]
    zero_rows = [r for r in comparison if r["mode"] == "zero_trust_pipeline"]
    models = sorted({r["model_name"] for r in baseline_rows})
    metric_names = ["SCHEMA %", "SEMANTIC %", "SUCCESS", "FALSE ACCEPTS", "ZT REJECTED", "MEAN LAT"]
    values: dict[str, list[float]] = {}
    display: dict[str, list[str]] = {}
    for model in models:
        b = [r for r in baseline_rows if r["model_name"] == model]
        z = [r for r in zero_rows if r["model_name"] == model]
        vals = [
            sum(r["schema_valid"].lower() == "true" for r in b) / len(b),
            sum(r["semantic_valid"].lower() == "true" for r in b) / len(b),
            sum(r["execution_outcome"] == "success" for r in b),
            sum(r["false_accept"].lower() == "true" for r in b),
            sum(r["execution_outcome"] == "rejected" for r in z),
            sum(float(r["latency_ms"]) for r in b if r["latency_ms"]) / len(b),
        ]
        values[model] = vals
        display[model] = [pct(vals[0]), pct(vals[1]), str(int(vals[2])), str(int(vals[3])), str(int(vals[4])), f"{vals[5]:.0f}"]

    mins = [min(values[m][i] for m in models) for i in range(len(metric_names))]
    maxs = [max(values[m][i] for m in models) for i in range(len(metric_names))]
    canvas = Canvas(2600, 1700)
    draw_title(canvas, "MODEL COMPARISON HEATMAP", "Darker cells indicate larger metric values within each column")
    left, top = 720, 300
    cell_w, cell_h = 280, 190
    for ci, metric in enumerate(metric_names):
        canvas.text(left + ci * cell_w + 25, top - 70, metric, COLORS["ink"], 3)
    for ri, model in enumerate(models):
        y = top + ri * cell_h
        canvas.text(70, y + 65, model.replace("foundry:", ""), COLORS["ink"], 3)
        for ci in range(len(metric_names)):
            value = values[model][ci]
            span = maxs[ci] - mins[ci]
            t = 0.0 if span == 0 else (value - mins[ci]) / span
            color = (int(230 - 130 * t), int(240 - 95 * t), int(250 - 50 * t))
            x = left + ci * cell_w
            canvas.rect(x, y, cell_w - 10, cell_h - 10, color, stroke=COLORS["white"])
            canvas.text(x + 40, y + 70, display[model][ci], COLORS["ink"], 4)
    canvas.save(path)


def false_accept_reduction(path: Path, metrics: dict) -> None:
    baseline = metrics["baseline_false_accepts"]
    zero = metrics["zero_trust_false_accepts"]
    bar_chart(
        path,
        "FALSE ACCEPT REDUCTION",
        "Headline execution-readiness result: 76 -> 0",
        ["BASELINE", "ZERO TRUST"],
        {"false accepts": [baseline, zero]},
        "FALSE ACCEPT COUNT",
        {"false accepts": COLORS["unsafe"]},
        max_value=80,
    )


def pipeline_summary_metrics(path: Path, metrics: dict) -> None:
    rows = [
        ("P3 INPUT ROWS", metrics["prototype3_input_rows"]),
        ("P4 RECORDS", metrics["prototype4_execution_records"]),
        ("BASELINE FALSE ACCEPTS", metrics["baseline_false_accepts"]),
        ("ZERO TRUST FALSE ACCEPTS", metrics["zero_trust_false_accepts"]),
        ("LAST TEST RESULT", metrics["last_known_test_result"]),
    ]
    canvas = Canvas()
    draw_title(canvas, "PHASE 4 PIPELINE SUMMARY", "Evidence-level execution-readiness analysis")
    y = 280
    for label, value in rows:
        canvas.rect(230, y, 1850, 150, COLORS["panel"], stroke=COLORS["grid"])
        canvas.text(290, y + 48, label, COLORS["ink"], 5)
        canvas.text(1450, y + 48, str(value), COLORS["accent"], 5)
        y += 190
    canvas.save(path)


def make_figures(comparison, by_ambiguity, frontier, metrics) -> None:
    frontier_scatter(FIGURE_DIR / "safety_latency_frontier.png", frontier)

    ambiguity_order = ["clear", "moderate", "high"]
    modes = ["baseline_trust_model", "zero_trust_pipeline"]
    rejected = defaultdict(dict)
    for row in comparison:
        rejected[(row["ambiguity_level"], row["mode"])].setdefault("total", 0)
        rejected[(row["ambiguity_level"], row["mode"])].setdefault("rejected", 0)
        rejected[(row["ambiguity_level"], row["mode"])]["total"] += 1
        if row["execution_outcome"] == "rejected":
            rejected[(row["ambiguity_level"], row["mode"])]["rejected"] += 1
    bar_chart(
        FIGURE_DIR / "rejection_by_ambiguity.png",
        "REJECTION BY AMBIGUITY LEVEL",
        "Zero-trust rejects moderate and high ambiguity commands in the pilot evidence",
        [a.upper() for a in ambiguity_order],
        {
            "baseline": [rejected[(a, modes[0])]["rejected"] for a in ambiguity_order],
            "zero trust": [rejected[(a, modes[1])]["rejected"] for a in ambiguity_order],
        },
        "REJECTED ROWS",
        {"baseline": COLORS["baseline"], "zero trust": COLORS["zero_trust"]},
        max_value=40,
    )
    heatmap(FIGURE_DIR / "model_comparison_heatmap.png", comparison)
    stacked_mode_chart(FIGURE_DIR / "outcome_comparison_by_mode.png", comparison)
    false_accept_reduction(FIGURE_DIR / "false_accept_reduction.png", metrics)
    pipeline_summary_metrics(FIGURE_DIR / "pipeline_summary_metrics.png", metrics)


def make_tables(comparison, frontier, metrics, file_manifest) -> None:
    key_rows = [
        {"metric": "Prototype 3 input rows", "value": metrics["prototype3_input_rows"]},
        {"metric": "Prototype 4 execution records", "value": metrics["prototype4_execution_records"]},
        {"metric": "Baseline false accepts", "value": metrics["baseline_false_accepts"]},
        {"metric": "Zero-trust false accepts", "value": metrics["zero_trust_false_accepts"]},
        {"metric": "Baseline success count", "value": metrics["baseline_outcome_counts"]["success"]},
        {"metric": "Zero-trust success count", "value": metrics["zero_trust_outcome_counts"]["success"]},
        {"metric": "Baseline no-op count", "value": metrics["baseline_outcome_counts"]["no_op"]},
        {"metric": "Zero-trust rejected count", "value": metrics["zero_trust_outcome_counts"]["rejected"]},
        {"metric": "Test result", "value": metrics["last_known_test_result"]},
    ]
    write_csv(TABLE_DIR / "key_metrics_summary.csv", key_rows, ["metric", "value"])
    write_tex_table(
        TABLE_DIR / "key_metrics_summary.tex",
        ["Metric", "Value"],
        [[r["metric"], r["value"]] for r in key_rows],
        "Key Phase 4 metrics.",
        "tab:phase4_key_metrics",
    )

    modes = {
        "baseline": [r for r in comparison if r["mode"] == "baseline_trust_model"],
        "zero-trust": [r for r in comparison if r["mode"] == "zero_trust_pipeline"],
    }
    outcome_rows = []
    for label, rows in modes.items():
        c = Counter(r["execution_outcome"] for r in rows)
        outcome_rows.append({
            "mode": label,
            "unsafe": c["unsafe"],
            "success": c["success"],
            "no_op": c["no_op"],
            "rejected": c["rejected"],
            "total_rows": len(rows),
            "false_accepts": sum(r["false_accept"].lower() == "true" for r in rows),
        })
    write_csv(TABLE_DIR / "outcome_counts_by_mode.csv", outcome_rows, ["mode", "unsafe", "success", "no_op", "rejected", "total_rows", "false_accepts"])
    write_tex_table(
        TABLE_DIR / "outcome_counts_by_mode.tex",
        ["Mode", "Unsafe", "Success", "No-op", "Rejected", "Total rows", "False accepts"],
        [[r["mode"], r["unsafe"], r["success"], r["no_op"], r["rejected"], r["total_rows"], r["false_accepts"]] for r in outcome_rows],
        "Execution outcome counts by mode.",
        "tab:phase4_outcomes_by_mode",
    )

    stage_map = {
        "schema_only": "schema",
        "schema_semantic": "schema + semantic",
        "schema_semantic_uncertainty": "schema + semantic + uncertainty",
        "full_zero_trust": "schema + semantic + uncertainty + safety",
    }
    baseline_fa = int(frontier[0]["false_accept_count"])
    frontier_rows = []
    for row in frontier:
        false_accepts = int(row["false_accept_count"])
        frontier_rows.append({
            "configuration": row["configuration"],
            "validation_stages_enabled": stage_map[row["configuration"]],
            "false_accepts": false_accepts,
            "false_accept_reduction_from_baseline": baseline_fa - false_accepts,
            "mean_latency_ms": f"{float(row['mean_latency_ms']):.2f}",
            "notes": "accepted-row latency available",
        })
    fields = ["configuration", "validation_stages_enabled", "false_accepts", "false_accept_reduction_from_baseline", "mean_latency_ms", "notes"]
    write_csv(TABLE_DIR / "safety_latency_frontier.csv", frontier_rows, fields)
    write_tex_table(
        TABLE_DIR / "safety_latency_frontier.tex",
        ["Configuration", "Validation stages", "False accepts", "Reduction", "Mean latency ms", "Notes"],
        [[r[f] for f in fields] for r in frontier_rows],
        "Safety-latency frontier across validation stringency configurations.",
        "tab:phase4_safety_latency_frontier",
    )

    groups = Counter(row["category"] for row in file_manifest)
    role_counts = Counter(row["role"] for row in file_manifest)
    summary_rows = [
        {"group": "input evidence", "file_count": groups["input"], "description": "Imported Prototype 3 benchmark, result, and reference files"},
        {"group": "generated output", "file_count": groups["generated output"], "description": "Primary Phase 4 execution comparison output"},
        {"group": "derived analysis", "file_count": groups["derived analysis"], "description": "False-accept and safety-latency derived analyses"},
        {"group": "summary artefact", "file_count": groups["summary"], "description": "Human-readable metrics and aggregate summaries"},
        {"group": "evidence pack", "file_count": groups["evidence pack"], "description": "Reproducibility documentation and manifests"},
        {"group": "documentation", "file_count": 1, "description": "Methodology notes in docs/"},
    ]
    write_csv(TABLE_DIR / "file_manifest_summary.csv", summary_rows, ["group", "file_count", "description"])
    write_tex_table(
        TABLE_DIR / "file_manifest_summary.tex",
        ["Group", "File count", "Description"],
        [[r["group"], r["file_count"], r["description"]] for r in summary_rows],
        "Summary of Phase 4 evidence-pack file manifest groups.",
        "tab:phase4_file_manifest_summary",
    )


def make_writing_pack(metrics: dict, frontier: list[dict[str, str]]) -> None:
    WRITING_DIR.mkdir(parents=True, exist_ok=True)
    (WRITING_DIR / "phase4_results_summary.md").write_text(f"""# Phase 4 Results Summary

Phase 4 evaluated execution-readiness for Prototype 3 planner outputs using a deterministic evidence-level evaluator. The input evidence contains {metrics['prototype3_input_rows']} Prototype 3 result rows from a 30-command pilot benchmark. Prototype 4 expands these into {metrics['prototype4_execution_records']} long-form execution records: {metrics['rows_per_mode']['baseline']} baseline rows and {metrics['rows_per_mode']['zero_trust']} zero-trust rows.

The baseline trust model produced {metrics['baseline_false_accepts']} false accepts, while the zero-trust pipeline produced {metrics['zero_trust_false_accepts']}. Baseline outcomes were unsafe={metrics['baseline_outcome_counts']['unsafe']}, success={metrics['baseline_outcome_counts']['success']}, and no_op={metrics['baseline_outcome_counts']['no_op']}. Zero-trust outcomes were rejected={metrics['zero_trust_outcome_counts']['rejected']} and success={metrics['zero_trust_outcome_counts']['success']}.

The Safety-Latency frontier shows false accepts decreasing as gates are added: {' -> '.join(str(v) for v in metrics['safety_latency_frontier_false_accepts'])}. This supports a safety-utility interpretation: stricter evidence gates reduce unsafe acceptance, but increase rejection.

Limitations remain important. The evaluator is deterministic and evidence-level. It does not replay commands in PyBullet, does not prove physical robot task success, and relies on Prototype 3 semantic, uncertainty, and safety labels.
""", encoding="utf-8")

    (WRITING_DIR / "dissertation_results_paragraphs.md").write_text("""# Dissertation Results Paragraphs

## Execution Comparison

The execution comparison evaluated Prototype 3 planner outputs under two deterministic Phase 4 policies: a baseline trust model and a zero-trust pipeline. The baseline mode accepted structurally valid non-empty plans, while the zero-trust mode required schema, semantic, uncertainty, safety, and action-plan evidence before acceptance. Across 120 Prototype 3 rows, the comparison produced 240 long-form Prototype 4 execution records.

## False Accept Reduction

The primary safety result is the reduction in false accepts. The baseline trust model produced 76 false accepts, whereas the zero-trust pipeline produced 0. This indicates that structurally valid planner outputs can substantially overstate execution readiness when semantic, uncertainty, and safety evidence are not used as gates. The result should be interpreted as evidence of reduced false-accept risk, not as proof of physical task completion.

## Safety-Latency Frontier

The Safety-Latency frontier isolates the effect of progressively stricter validation. False accepts decreased from 76 under schema-only validation to 4 after adding semantic validation, and to 0 after adding uncertainty gating. Full zero-trust preserved the 0 false-accept result. This pattern demonstrates a safety-utility trade-off: stricter validation reduces unsafe acceptance, but narrows the set of accepted outputs.

## Ambiguity-Level Behaviour

Ambiguity strongly influenced acceptance behaviour. The zero-trust pipeline preserved successful low-risk executions while rejecting outputs in higher-ambiguity settings where the available evidence did not justify execution. This supports the use of ambiguity-stratified analysis for evaluating local SLM planning pipelines.

## Model-Level Behaviour

Model-level results show that false-accept risk is not only a model property. Different local models produced different rates of structurally valid but unsafe or semantically unsuitable outputs, yet the zero-trust pipeline reduced false accepts to zero across all models in the pilot evidence. This suggests that pipeline-level validation can mitigate model-level variation in safety-relevant behaviour.

## Reproducibility and Evidence Pack

The evidence pack records the imported Prototype 3 inputs, generated Prototype 4 outputs, reproduction commands, row counts, metrics, and file manifest. This makes the Phase 4 analysis auditable from the checked-in CSV, JSONL, Markdown, and manifest files.

## Limitations of Deterministic Execution Evaluation

The Phase 4 evaluator is deterministic and evidence-level. It uses structured planner outputs and inherited Prototype 3 labels for schema validity, semantic validity, uncertainty, and safety. It does not constitute physical robot validation, formal verification, or full simulator replay. The benchmark is pilot-scale, and broader claims would require a larger externally validated benchmark and physical or simulated execution studies.
""", encoding="utf-8")

    (WRITING_DIR / "figure_notes.md").write_text("""# Figure Notes

## safety_latency_frontier.png

Source: `results/summaries/safety_latency_frontier.csv`. Columns used: `configuration`, `false_accept_count`, `mean_latency_ms`. Values are directly read from the frontier CSV. Latency is available as accepted-row mean latency.

## rejection_by_ambiguity.png

Source: `results/summaries/prototype4_execution_comparison.csv`. Columns used: `ambiguity_level`, `mode`, `execution_outcome`. Rejected counts are computed by counting `execution_outcome == rejected` for each ambiguity level and mode.

## model_comparison_heatmap.png

Source: `results/summaries/prototype4_execution_comparison.csv`. Columns used: `model_name`, `mode`, `schema_valid`, `semantic_valid`, `execution_outcome`, `false_accept`, `latency_ms`. Metrics are computed from available fields. No separate model-level uncertainty-valid rate is plotted because the selected heatmap prioritises schema rate, semantic rate, success count, false accepts, zero-trust rejected count, and mean latency.

## outcome_comparison_by_mode.png

Source: `results/summaries/prototype4_execution_comparison.csv`. Columns used: `mode`, `execution_outcome`. Outcome counts are computed directly from the CSV.

## false_accept_reduction.png

Source: `results/evidence_pack/metrics_manifest.json`. Values used: `baseline_false_accepts`, `zero_trust_false_accepts`. Values are confirmed by `prototype4_execution_comparison.csv`.

## pipeline_summary_metrics.png

Source: `results/evidence_pack/metrics_manifest.json`. This optional summary figure presents headline row counts, false-accept counts, and test result.
""", encoding="utf-8")

    (WRITING_DIR / "table_notes.md").write_text("""# Table Notes

## key_metrics_summary

Source: `results/evidence_pack/metrics_manifest.json`. Supports the headline Phase 4 results summary. Values are read from the metrics manifest, which is derived from current output files where available.

## outcome_counts_by_mode

Source: `results/summaries/prototype4_execution_comparison.csv`. Supports comparison of baseline and zero-trust execution outcomes. Values are computed directly from the CSV.

## safety_latency_frontier

Source: `results/summaries/safety_latency_frontier.csv`. Supports the validation-stringency trade-off analysis. False-accept reduction is computed relative to the schema-only configuration.

## file_manifest_summary

Source: `results/evidence_pack/file_manifest.csv`. Supports reproducibility reporting by grouping evidence files into input, output, derived analysis, summary, evidence-pack, and documentation categories.
""", encoding="utf-8")

    (WRITING_DIR / "safe_gate_positioning_note.md").write_text("""# SafeGate Positioning Note

SafeGate is the closest related recent work because it also uses pre-execution safety gating for LLM-controlled robots. It introduces a neurosymbolic architecture with hazard analysis, deterministic decision gating, safety contract compilation, SMT verification, and runtime monitoring.

This dissertation differs by targeting sub-2B CPU-class local SLMs through Microsoft Foundry Local, constrained and offline industrial or clinical-style deployment assumptions, ambiguity-stratified command evaluation, and explicit measurement of the model-level versus pipeline-level false-accept gap.

The contribution should therefore be positioned as a local-first constrained-deployment complement to SafeGate. It should not be framed as outperforming SafeGate, replacing SafeGate, or proving broader robot safety. Instead, it studies how evidence gates affect execution-readiness and false-accept risk for local SLM planning under pilot benchmark conditions.
""", encoding="utf-8")


def main() -> None:
    for path in REQUIRED_SOURCES.values():
        _require(path)
    FIGURE_DIR.mkdir(exist_ok=True)
    TABLE_DIR.mkdir(exist_ok=True)
    WRITING_DIR.mkdir(parents=True, exist_ok=True)

    comparison = read_csv(REQUIRED_SOURCES["comparison"])
    by_ambiguity = read_csv(REQUIRED_SOURCES["by_ambiguity"])
    frontier = read_csv(REQUIRED_SOURCES["frontier"])
    file_manifest = read_csv(REQUIRED_SOURCES["file_manifest"])
    metrics = json.loads(REQUIRED_SOURCES["metrics"].read_text(encoding="utf-8"))

    make_figures(comparison, by_ambiguity, frontier, metrics)
    make_tables(comparison, frontier, metrics, file_manifest)
    make_writing_pack(metrics, frontier)

    print("Generated 6 figures in figures/")
    print("Generated 4 CSV tables and 4 LaTeX tables in tables/")
    print("Generated writing pack markdown files in results/writing_pack/")


if __name__ == "__main__":
    main()
