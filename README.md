# BRACU Duburi — Vision Pipeline Dashboard

A Streamlit dashboard for the BRAC University AUV team's RoboSub 2026 computer-vision
work. It turns raw YOLO training output into browsable per-task analytics, and
documents the n8n workflows that automate dataset annotation.

Built for Team BRACU Duburi (BRAC University, Dhaka) — Autonomous Underwater Vehicle,
RoboSub 2026, Irvine CA.

<!-- Add once deployed: **[Live demo](https://your-app.streamlit.app)** -->

## What it does

**Per-task training analytics.** Point the app at a YOLO run directory and it renders
loss curves (box/cls/DFL, train vs val), mAP50 and mAP50-95 over epochs with the best
epoch marked, precision/recall curves, the confusion matrix, PR/F1/P/R curves, and
navigable galleries of train batches and val predictions against ground truth.

Column detection is defensive — it matches `metrics/mAP50(B)`-style headers by
substring, so runs from different Ultralytics versions load without edits.

**Run ingestion.** Upload a zip of a run folder and the app finds the run root by
locating `results.csv` at any depth, then renders analytics immediately. Admins can
persist a run into `saved_runs/`; visitors get a temporary view that isn't saved.

**Annotation pipeline docs.** The [Pipeline page](pages/3_Pipeline.py) reads the
committed n8n workflow JSON from [`pipeline/workflows/`](pipeline/workflows/) and
renders the real node graph, the JavaScript in each Code node, and a download button
to import it into your own n8n. See [`pipeline/README.md`](pipeline/README.md).

**Content-driven.** Tasks, descriptions, accent colours and run bindings live in
[`content/site.yaml`](content/site.yaml), editable in-app in admin mode.

## Results

Torpedo detection (`saved_runs/Torpedo/`), YOLO11n, 640px, batch 16, early-stopped
at epoch 136 of 200:

| Metric | Best |
|---|---|
| mAP50 | 0.995 |
| mAP50-95 | 0.846 |
| Precision | 0.999 |
| Recall | 1.000 |

Trained on a custom underwater dataset collected during pool trials and annotated
through the n8n pipeline below. These figures come from a small single-class merged
dataset — treat them as a working baseline, not a generalisation claim.

## Architecture

```
dashboard.py              entrypoint — st.navigation, sidebar, auth widget
pages/
  home.py                 hero, task cards, pipeline overview
  1_About.py              competition and team background
  2_Tasks.py              task list; admin-editable, writes back to site.yaml
  3_Pipeline.py           renders n8n workflows from pipeline/workflows/
  4_Task_Analytics.py     per-task tabs: metrics, Plotly charts, image galleries
utils/
  auth.py                 Google OAuth + password admin login
  content.py              site.yaml load/save
  styles.py               shared CSS, page_header/section/metric_card/footer
content/site.yaml         all editable site content
pipeline/workflows/       exported n8n workflows (no credentials)
saved_runs/<Task>/        committed YOLO artefacts per task
```

The six-stage pipeline splits across three owners: **local** scripts split video,
merge annotations and train; **n8n** distributes clips and collects replies; **human**
annotators label in CVAT. n8n is started by a webhook and reports back to a callback
URL when a round completes.

## Run locally

```bash
git clone https://github.com/MadLad10/bracu-duburi-dashboard.git
cd bracu-duburi-dashboard
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard.py
```

Opens on http://localhost:8501. The Torpedo run renders with no configuration.

### Admin mode (optional)

Admin mode unlocks task editing and persisting uploaded runs.

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then set ADMIN_PASSWORD
```

Password login is **disabled** unless `ADMIN_PASSWORD` is set. Google OAuth is
optional; when `GOOGLE_CLIENT_ID` is set, only `ADMIN_EMAIL` may sign in.
`.streamlit/secrets.toml` is git-ignored — never commit it.

## Deploy to Streamlit Community Cloud

1. Push to GitHub.
2. At [share.streamlit.io](https://share.streamlit.io), **New app** → this repo,
   branch `main`, main file `dashboard.py`.
3. **Advanced settings → Secrets**: paste the contents of
   `.streamlit/secrets.toml.example` with real values. Set `REDIRECT_URI` to the
   app's final URL, and add that same URL to your Google OAuth client's authorised
   redirect URIs.
4. Deploy, then put the URL at the top of this README.

**Note on persistence:** Streamlit Cloud filesystems are ephemeral. Runs saved via
admin upload survive only until the container restarts — commit them to
`saved_runs/` to publish them permanently.

## Adding a task's training run

1. Train with Ultralytics YOLO; you get a run dir containing `results.csv`,
   `args.yaml`, curve PNGs and batch JPGs.
2. Zip it (weights not needed) and upload it on the Task Analytics tab in admin mode,
   or copy it to `saved_runs/<RunName>/` by hand.
3. Make sure `run_name` for that task in `content/site.yaml` matches the folder name.

Currently only the Torpedo run is committed; the other four tasks show as *Pending*
until their runs are added.

## Built with

Streamlit · Plotly · pandas · Pillow · PyYAML · Ultralytics YOLO11 · n8n · CVAT
