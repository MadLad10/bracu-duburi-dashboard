import shutil
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from plotly.subplots import make_subplots

from utils import styles, content, auth

SAVED_RUNS_DIR = Path(__file__).parent.parent / "saved_runs"
SAVE_PATTERNS = [
    "results.csv", "args.yaml",
    "train_batch*.jpg", "train_batch*.png",
    "val_batch*.jpg",   "val_batch*.png",
    "confusion_matrix*.png",
    "BoxPR_curve.png", "PR_curve.png",
    "BoxF1_curve.png", "F1_curve.png",
    "BoxP_curve.png",  "P_curve.png",
    "BoxR_curve.png",  "R_curve.png",
    "labels.jpg",      "labels.png",
    "results.png",
]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#FFFFFF", plot_bgcolor="#F8FAFC",
    font=dict(color="#0F172A", size=12, family="Inter, sans-serif"),
    legend=dict(bgcolor="#FFFFFF", bordercolor="#E2E8F0", borderwidth=1),
    margin=dict(l=50, r=20, t=50, b=40),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#1E3A5F", font_color="#FFFFFF", font_size=12),
)
COLORS = {
    "train": "#2563EB", "val": "#059669",
    "map50": "#DC2626", "map95": "#D97706",
    "prec":  "#7C3AED", "rec":  "#0891B2",
}


def save_run(src: Path, name: str) -> Path:
    dest = SAVED_RUNS_DIR / name
    dest.mkdir(parents=True, exist_ok=True)
    for pat in SAVE_PATTERNS:
        for f in src.glob(pat):
            shutil.copy2(f, dest / f.name)
    return dest


def find_images(run_dir: Path, pattern: str) -> list:
    return sorted(run_dir.glob(pattern))


def load_results(run_dir: Path):
    csv = run_dir / "results.csv"
    if not csv.exists():
        return None
    df = pd.read_csv(csv)
    df.columns = [c.strip() for c in df.columns]
    return df


def image_gallery(title: str, images: list, key: str) -> None:
    st.markdown(
        f"<p style='font-size:13px;font-weight:700;color:#1E3A5F;margin-bottom:8px'>"
        f"{title} <span style='font-weight:400;color:#94A3B8'>({len(images)})</span></p>",
        unsafe_allow_html=True,
    )
    if not images:
        st.info("No images found.")
        return
    idx_key = f"{key}_idx"
    if idx_key not in st.session_state:
        st.session_state[idx_key] = 0
    idx = max(0, min(st.session_state[idx_key], len(images) - 1))
    nav1, nav2, nav3 = st.columns([1, 5, 1])
    with nav1:
        if st.button("←", key=f"{key}_prev", disabled=(idx == 0)):
            st.session_state[idx_key] = idx - 1
            st.rerun()
    with nav3:
        if st.button("→", key=f"{key}_next", disabled=(idx == len(images) - 1)):
            st.session_state[idx_key] = idx + 1
            st.rerun()
    with nav2:
        st.caption(f"{images[idx].name}  ({idx + 1} / {len(images)})")
    try:
        st.image(Image.open(images[idx]), use_container_width=True)
    except Exception as e:
        st.error(f"Could not load image: {e}")


def show_run_analytics(run_dir: Path, task_color: str) -> None:
    df = load_results(run_dir)
    if df is None:
        st.error("results.csv not found in this run.")
        return

    map50_col = next((c for c in df.columns if "mAP50" in c and "95" not in c), None)
    map95_col = next((c for c in df.columns if "mAP50-95" in c), None)
    prec_col  = next((c for c in df.columns if "precision" in c.lower()), None)
    rec_col   = next((c for c in df.columns if "recall"    in c.lower()), None)

    best_map50 = df[map50_col].max()              if map50_col else 0
    best_map95 = df[map95_col].max()              if map95_col else 0
    best_epoch = int(df[map50_col].idxmax() + 1)  if map50_col else 0
    best_prec  = df[prec_col].max()               if prec_col  else 0
    best_rec   = df[rec_col].max()                if rec_col   else 0
    total_ep   = len(df)
    epochs     = df["epoch"] if "epoch" in df.columns else range(1, len(df) + 1)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: styles.metric_card("mAP50",     f"{best_map50:.3f}", f"epoch {best_epoch}", "")
    with c2: styles.metric_card("mAP50-95",  f"{best_map95:.3f}", f"epoch {best_epoch}", "green")
    with c3: styles.metric_card("Precision", f"{best_prec:.3f}",  "best val",            "purple")
    with c4: styles.metric_card("Recall",    f"{best_rec:.3f}",   "best val",            "cyan")
    with c5: styles.metric_card("Epochs",    str(total_ep),        "completed",           "amber")

    st.markdown("<br>", unsafe_allow_html=True)
    styles.section("Training Curves")
    c_left, c_right = st.columns(2)

    with c_left:
        box_tr = next((c for c in df.columns if "box_loss" in c and "train" in c.lower()), None) or \
                 next((c for c in df.columns if "box_loss" in c), None)
        cls_tr = next((c for c in df.columns if "cls_loss" in c and "train" in c.lower()), None) or \
                 next((c for c in df.columns if "cls_loss" in c), None)
        dfl_tr = next((c for c in df.columns if "dfl_loss" in c and "train" in c.lower()), None) or \
                 next((c for c in df.columns if "dfl_loss" in c), None)
        box_vl = next((c for c in df.columns if "box_loss" in c and "val" in c.lower()), None)
        cls_vl = next((c for c in df.columns if "cls_loss" in c and "val" in c.lower()), None)
        dfl_vl = next((c for c in df.columns if "dfl_loss" in c and "val" in c.lower()), None)

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            subplot_titles=("Box Loss", "Class Loss", "DFL Loss"),
                            vertical_spacing=0.09)
        for row, (tr_col, vl_col) in enumerate(
            [(box_tr, box_vl), (cls_tr, cls_vl), (dfl_tr, dfl_vl)], start=1
        ):
            if tr_col and tr_col in df.columns:
                fig.add_trace(go.Scatter(x=epochs, y=df[tr_col], name="Train",
                                         line=dict(color=COLORS["train"], width=2.5),
                                         showlegend=(row == 1)), row=row, col=1)
            if vl_col and vl_col in df.columns:
                fig.add_trace(go.Scatter(x=epochs, y=df[vl_col], name="Val",
                                         line=dict(color=COLORS["val"], width=2.5, dash="dot"),
                                         showlegend=(row == 1)), row=row, col=1)
        fig.update_layout(height=480, title_text="<b>Loss Curves</b>", **PLOTLY_LAYOUT)
        fig.update_xaxes(gridcolor="#E2E8F0", linecolor="#CBD5E1", title_text="Epoch", row=3, col=1)
        fig.update_yaxes(gridcolor="#E2E8F0", linecolor="#CBD5E1")
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                             subplot_titles=("mAP Scores", "Precision & Recall"),
                             vertical_spacing=0.12)
        if map50_col and map50_col in df.columns:
            fig2.add_trace(go.Scatter(x=epochs, y=df[map50_col], name="mAP50",
                                      line=dict(color=task_color, width=2.5),
                                      fill="tozeroy", fillcolor=f"{task_color}15"), row=1, col=1)
        if map95_col and map95_col in df.columns:
            fig2.add_trace(go.Scatter(x=epochs, y=df[map95_col], name="mAP50-95",
                                      line=dict(color=COLORS["map95"], width=2.5),
                                      fill="tozeroy", fillcolor="rgba(217,119,6,0.06)"), row=1, col=1)
        if prec_col and prec_col in df.columns:
            fig2.add_trace(go.Scatter(x=epochs, y=df[prec_col], name="Precision",
                                      line=dict(color=COLORS["prec"], width=2.5)), row=2, col=1)
        if rec_col and rec_col in df.columns:
            fig2.add_trace(go.Scatter(x=epochs, y=df[rec_col], name="Recall",
                                      line=dict(color=COLORS["rec"], width=2.5)), row=2, col=1)
        if map50_col:
            best_ep_idx = int(df[map50_col].idxmax())
            x_val = epochs.iloc[best_ep_idx] if hasattr(epochs, "iloc") else best_ep_idx + 1
            fig2.add_vline(x=x_val, line_dash="dash", line_color="#94A3B8",
                           annotation_text="Best", annotation_font_color="#475569",
                           annotation_font_size=11)
        fig2.update_layout(height=480, title_text="<b>Metrics</b>", **PLOTLY_LAYOUT)
        fig2.update_xaxes(gridcolor="#E2E8F0", linecolor="#CBD5E1", title_text="Epoch", row=2, col=1)
        fig2.update_yaxes(gridcolor="#E2E8F0", linecolor="#CBD5E1")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    styles.section("Detection Images")
    train_imgs = find_images(run_dir, "train_batch*.jpg") or find_images(run_dir, "train_batch*.png")
    val_pred   = find_images(run_dir, "val_batch*pred*.jpg") or find_images(run_dir, "val_batch*pred*.png")
    val_label  = find_images(run_dir, "val_batch*label*.jpg") or find_images(run_dir, "val_batch*label*.png")

    img_c1, img_c2 = st.columns(2)
    with img_c1: image_gallery("Train Batches",   train_imgs, f"train_{run_dir.name}")
    with img_c2: image_gallery("Val Predictions", val_pred,   f"valpred_{run_dir.name}")

    if val_label:
        st.markdown("<br>", unsafe_allow_html=True)
        styles.section("Val Labels vs Predictions")
        lb_c, pr_c = st.columns(2)
        with lb_c: image_gallery("Ground Truth Labels", val_label, f"vallabel_{run_dir.name}")
        with pr_c: image_gallery("Model Predictions",   val_pred,  f"valpred2_{run_dir.name}")

    st.divider()
    styles.section("Evaluation Plots")
    eval_images = {
        "Confusion Matrix": find_images(run_dir, "confusion_matrix_normalized.png") or find_images(run_dir, "confusion_matrix.png"),
        "PR Curve":  find_images(run_dir, "BoxPR_curve.png") or find_images(run_dir, "PR_curve.png"),
        "F1 Curve":  find_images(run_dir, "BoxF1_curve.png") or find_images(run_dir, "F1_curve.png"),
        "P Curve":   find_images(run_dir, "BoxP_curve.png")  or find_images(run_dir, "P_curve.png"),
        "R Curve":   find_images(run_dir, "BoxR_curve.png")  or find_images(run_dir, "R_curve.png"),
        "Labels":    find_images(run_dir, "labels.jpg")      or find_images(run_dir, "labels.png"),
    }
    eval_cols = st.columns(len(eval_images))
    for col, (t, imgs) in zip(eval_cols, eval_images.items()):
        with col:
            st.markdown(
                f"<p style='font-size:11px;font-weight:700;color:#475569;text-align:center;"
                f"text-transform:uppercase;letter-spacing:1px'>{t}</p>",
                unsafe_allow_html=True,
            )
            if imgs:
                try:
                    st.image(Image.open(imgs[0]), use_container_width=True)
                except Exception:
                    st.info("Could not load.")
            else:
                st.markdown("<p style='color:#CBD5E1;text-align:center;font-size:12px'>Not found</p>",
                            unsafe_allow_html=True)


# ── Main ─────────────────────────────────────────────────────────────────────
data = content.load()
tasks = data.get("tasks", [])

styles.page_header("Task Analytics", "Per-Task Training Results · YOLO11n")

if not tasks:
    st.warning("No tasks configured. Check content/site.yaml.")
    st.stop()

tab_labels = [t.get("name", f"Task {i+1}") for i, t in enumerate(tasks)]
tabs = st.tabs(tab_labels)

for tab, task in zip(tabs, tasks):
    with tab:
        task_color    = task.get("color", "#2563EB")
        task_name     = task.get("name", "")
        task_run      = task.get("run_name", "")
        saved_run_dir = SAVED_RUNS_DIR / task_run if task_run else None

        st.markdown(
            f'<div style="border-left:5px solid {task_color};padding:10px 16px;'
            f'background:linear-gradient(90deg,{task_color}0D,transparent);'
            f'border-radius:0 8px 8px 0;margin-bottom:20px">'
            f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:24px;'
            f'color:{task_color};letter-spacing:3px">{task_name}</span>'
            f'<span style="font-size:12px;color:#64748B;margin-left:12px">'
            f'{task.get("description","")}</span></div>',
            unsafe_allow_html=True,
        )

        has_saved = saved_run_dir and saved_run_dir.exists() and (saved_run_dir / "results.csv").exists()

        if auth.is_admin():
            modes = ["Saved Run", "Import Directory"] if has_saved else ["Import Directory"]
            view_mode = st.radio("View", modes, horizontal=True,
                                 key=f"viewmode_{task_name}", label_visibility="collapsed")

            if view_mode == "Import Directory":
                dir_path = st.text_input("Run directory path", key=f"dirpath_{task_name}",
                                         placeholder=r"C:\...\runs\train\yolo11n_custom")
                run_dir = Path(dir_path) if dir_path else None
                if run_dir and run_dir.exists() and (run_dir / "results.csv").exists():
                    _, btn_col = st.columns([3, 1])
                    with btn_col:
                        if st.button("Save run (no weights)", key=f"save_{task_name}",
                                     type="primary", use_container_width=True):
                            save_run(run_dir, task_run or task_name)
                            st.success(f"Saved to saved_runs/{task_run or task_name}")
                            st.rerun()
                    show_run_analytics(run_dir, task_color)
                elif dir_path:
                    st.warning("Directory not found or missing results.csv")
                else:
                    st.info("Enter the path to a training run directory above.")
            else:
                show_run_analytics(saved_run_dir, task_color)

        else:
            if has_saved:
                st.info("Showing saved training results for this task.", icon="📊")
                show_run_analytics(saved_run_dir, task_color)
                st.divider()

            st.markdown(
                "<p style='font-size:12px;font-weight:700;color:#475569;margin-bottom:6px'>"
                "Upload your own run (temporary — not saved)</p>",
                unsafe_allow_html=True,
            )
            uploaded = st.file_uploader(
                "Upload a zip of your run folder (results.csv required, no .pt weights needed)",
                type=["zip"], key=f"upload_{task_name}", label_visibility="collapsed",
            )
            if uploaded:
                with tempfile.TemporaryDirectory() as tmpdir:
                    zip_path = Path(tmpdir) / "run.zip"
                    zip_path.write_bytes(uploaded.read())
                    with zipfile.ZipFile(zip_path, "r") as zf:
                        zf.extractall(tmpdir)
                    run_root = next(
                        (p.parent for p in Path(tmpdir).rglob("results.csv")), None
                    )
                    if run_root:
                        st.success("Loaded temporary run — showing analytics below.")
                        show_run_analytics(run_root, task_color)
                    else:
                        st.error("results.csv not found in the uploaded zip.")

styles.footer()
