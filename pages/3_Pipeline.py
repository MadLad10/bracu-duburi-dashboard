import json
from pathlib import Path

import streamlit as st

from utils import styles, content

try:
    import requests as _req
except ImportError:
    _req = None

WORKFLOW_DIR = Path(__file__).parent.parent / "pipeline" / "workflows"

# Where this project's own stages run vs. what n8n orchestrates.
STAGES = [
    ("01", "Split Video",   "Dive footage cut into fixed-length clips, one zip per annotator.", "local"),
    ("02", "Distribute",    "n8n emails each annotator their clip with CVAT instructions.",     "n8n"),
    ("03", "Annotate",      "Annotators label in CVAT and reply with a YOLO 1.1 export.",       "human"),
    ("04", "Collect",       "n8n polls Gmail, saves each zip, counts until the round is done.", "n8n"),
    ("05", "Merge & Split", "Annotations merged and split 85/5/10 train/val/test.",             "local"),
    ("06", "Train",         "YOLO trained on the merged set with underwater augmentation.",     "local"),
]
OWNER_STYLE = {
    "n8n":   ("#EFF6FF", "#BFDBFE", "#1D4ED8", "n8n"),
    "local": ("#F8FAFC", "#E2E8F0", "#475569", "Local"),
    "human": ("#FDF4FF", "#E9D5FF", "#7C3AED", "Human"),
}
# What each step does, in plain language. The page is for readers who want to
# know what the automation does — not what an n8n node type is called.
STEP_TEXT = {
    # distribution
    "Receive Pipeline Trigger": "A round begins — the training script sends over the annotator list, their clips, and where to report back.",
    "Build Round State":        "Checks the request is complete and records who owes work this round.",
    "State to File":            "Writes that record down…",
    "Write Round State":        "…so the collecting side can pick it up later.",
    "Fan Out Annotators":       "Splits the round into one job per annotator.",
    "Loop Annotators":          "Works through them one at a time.",
    "Read Clip Zip":            "Loads that person's video clip.",
    "Send Gmail":               "Emails it to them with the class list and CVAT instructions.",
    "Respond OK":               "Confirms back to the training script that the clips are out.",
    # collection
    "Gmail Trigger":            "Watches the inbox every minute for replies with attachments.",
    "Extract Zip Attachment":   "Pulls out the annotation zip and works out who sent it.",
    "Save Zip to Disk":         "Saves their labelled data.",
    "Read Round State":         "Looks up the round record from when the clips went out.",
    "Parse Round State":        "Reads who is still outstanding.",
    "Update Round State":       "Ticks that person off — counting people, not emails, so replying twice can't finish a round early.",
    "All Received?":            "Is everyone in?",
    "Read Saved Zip":           "Yes — gathers the finished annotations…",
    "Notify Pipeline":          "…and hands them back to the training script.",
    "Partial - Log Only":       "Not yet — keep waiting for the rest.",
}
# Only shown as small print under each step.
NODE_LABELS = {
    "n8n-nodes-base.webhook":          "webhook",
    "n8n-nodes-base.code":             "code",
    "n8n-nodes-base.splitInBatches":   "loop",
    "n8n-nodes-base.readWriteFile":    "file",
    "n8n-nodes-base.convertToFile":    "file",
    "n8n-nodes-base.extractFromFile":  "file",
    "n8n-nodes-base.gmail":            "gmail",
    "n8n-nodes-base.gmailTrigger":     "gmail",
    "n8n-nodes-base.respondToWebhook": "respond",
    "n8n-nodes-base.httpRequest":      "http",
    "n8n-nodes-base.if":               "branch",
    "n8n-nodes-base.noOp":             "wait",
}


def load_workflows() -> list:
    if not WORKFLOW_DIR.exists():
        return []
    # send before receive — alphabetical order would tell the story backwards
    order = {"send-annotation-emails.json": 0, "receive-annotation-replies.json": 1}
    out = []
    for path in sorted(WORKFLOW_DIR.glob("*.json"), key=lambda q: (order.get(q.name, 99), q.name)):
        try:
            out.append((path, json.loads(path.read_text())))
        except Exception as e:
            st.warning(f"Could not parse {path.name}: {e}")
    return out


def node_levels(wf: dict) -> list:
    """Group nodes by graph depth from the trigger.

    Returns a list of levels, each a list of nodes. Nodes sharing a level are
    parallel branches, not sequential steps — so the view never implies an edge
    between two nodes that aren't actually connected.
    """
    nodes = {n["name"]: n for n in wf.get("nodes", [])}
    conns = wf.get("connections", {})
    targets = {
        c["node"]
        for v in conns.values()
        for branch in v.get("main", [])
        for c in branch
    }
    roots = [n for n in nodes if n not in targets] or list(nodes)[:1]

    depth, queue = {r: 0 for r in roots}, list(roots)
    while queue:
        name = queue.pop(0)
        for branch in conns.get(name, {}).get("main", []):
            for c in branch:
                nxt = c["node"]
                if nxt not in nodes:
                    continue
                # a back-edge (loop) must not push the target deeper forever
                cand = depth[name] + 1
                if nxt not in depth:
                    depth[nxt] = cand
                    queue.append(nxt)

    for name in nodes:                       # unreachable nodes go last
        depth.setdefault(name, max(depth.values(), default=0) + 1)

    levels = []
    for d in sorted(set(depth.values())):
        levels.append([nodes[n] for n in nodes if depth[n] == d])
    return levels


data = content.load()
pipeline = data.get("pipeline", {})
workflows = load_workflows()

styles.page_header("Automation Pipeline", "n8n · Annotation Distribution & Collection")

styles.section("How It Works")
st.markdown(
    f'<div class="card" style="margin-bottom:20px">'
    f'<p style="color:#334155;font-size:14px;line-height:1.7">{pipeline.get("description","")}</p>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Stage strip, labelled by who actually runs each stage ────────────────────
styles.section("Pipeline Stages")
st.caption(
    "n8n owns distribution and collection. Splitting, merging and training run "
    "locally and are wired to n8n over HTTP — a webhook starts a round, a callback "
    "fires when every annotator has replied."
)
stage_cols = st.columns(len(STAGES))
for col, (num, title, desc, owner) in zip(stage_cols, STAGES):
    bg, bdr, fg, tag = OWNER_STYLE[owner]
    with col:
        st.markdown(
            f'<div style="background:{bg};border:1px solid {bdr};border-radius:12px;'
            f'padding:14px 12px;height:100%">'
            f'<div style="font-size:9px;font-weight:800;color:{fg};letter-spacing:1.5px;'
            f'text-transform:uppercase;margin-bottom:6px">{tag}</div>'
            f'<div style="font-size:11px;font-weight:800;color:#0F172A">{num} &nbsp;{title}</div>'
            f'<div style="font-size:10px;color:#64748B;line-height:1.5;margin-top:5px">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── The actual workflows, read from the committed JSON ───────────────────────
styles.section("What The Automation Does")

if not workflows:
    st.warning(
        "No workflow files found in `pipeline/workflows/`. "
        "Export them from n8n (Workflow → Download) and commit them there."
    )
else:
    total_steps = sum(len(wf.get("nodes", [])) for _, wf in workflows)
    m1, m2, m3 = st.columns(3)
    with m1: styles.metric_card("Workflows", str(len(workflows)), "email out, collect back", "")
    with m2: styles.metric_card("Steps",     str(total_steps),    "fully automated", "purple")
    with m3: styles.metric_card("Verified",  "n8n 2.26",          "runs a round end to end", "green")

    st.markdown("<br>", unsafe_allow_html=True)

    BLURB = {
        "AUV - Send Annotation Emails":
            "Takes a list of annotators and gets each of them their own video clip, "
            "with instructions, without anyone sending a single email by hand.",
        "AUV - Receive Annotation Replies":
            "Watches for the labelled data coming back, keeps track of who has replied, "
            "and only kicks off training once the whole round is in.",
    }

    for path, wf in workflows:
        levels = node_levels(wf)
        nodes  = [n for lvl in levels for n in lvl]
        title  = wf.get("name", path.stem)
        pretty = title.replace("AUV - ", "")

        st.markdown(
            f'<p style="font-size:15px;font-weight:900;color:#0F172A;margin:18px 0 2px">{pretty}</p>'
            f'<p style="font-size:12px;color:#64748B;line-height:1.6;margin:0 0 12px;max-width:760px">'
            f'{BLURB.get(title, "")}</p>',
            unsafe_allow_html=True,
        )

        step_no = 0
        for level in levels:
            branching = len(level) > 1
            if branching:
                cols = st.columns(len(level))
            for j, n in enumerate(level):
                name = n.get("name", "")
                text = STEP_TEXT.get(name, name)
                kind = NODE_LABELS.get(n.get("type", ""), "step")
                if not branching:
                    step_no += 1
                    num = f"{step_no:02d}"
                    bg, bdr = "#FFFFFF", "#E2E8F0"
                else:
                    num = "↳"
                    bg, bdr = "#F8FAFC", "#E2E8F0"
                block = (
                    f'<div style="background:{bg};border:1px solid {bdr};border-radius:10px;'
                    f'padding:12px 16px;margin-bottom:8px;display:flex;gap:14px;align-items:flex-start">'
                    f'<div style="font-size:11px;font-weight:900;color:#94A3B8;min-width:20px;'
                    f'padding-top:1px">{num}</div>'
                    f'<div><div style="font-size:13px;color:#1E293B;line-height:1.55">{text}</div>'
                    f'<div style="font-size:10px;color:#CBD5E1;margin-top:3px">{name} · {kind}</div>'
                    f'</div></div>'
                )
                if branching:
                    with cols[j]:
                        st.markdown(block, unsafe_allow_html=True)
                else:
                    st.markdown(block, unsafe_allow_html=True)

        c1, c2 = st.columns([1, 3])
        with c1:
            st.download_button(
                "Download for n8n",
                data=path.read_text(),
                file_name=path.name,
                mime="application/json",
                key=f"dl_{path.stem}",
            )
        with c2:
            with st.expander("Show the JavaScript behind these steps"):
                code_nodes = [n for n in nodes if n.get("type") == "n8n-nodes-base.code"]
                if not code_nodes:
                    st.caption("No code steps in this workflow.")
                for n in code_nodes:
                    st.markdown(
                        f'<p style="font-size:11px;font-weight:700;color:#475569;'
                        f'margin:6px 0 2px">{n["name"]}</p>',
                        unsafe_allow_html=True,
                    )
                    st.code(n.get("parameters", {}).get("jsCode", ""), language="javascript")

st.markdown("<br>", unsafe_allow_html=True)

# ── Optional live instance, only when one is configured ──────────────────────
n8n_url = ""
try:
    n8n_url = st.secrets["N8N_URL"]
except Exception:
    pass

if n8n_url:
    styles.section("Live Instance")
    online = False
    if _req:
        try:
            online = _req.get(f"{n8n_url.rstrip('/')}/healthz", timeout=2).ok
        except Exception:
            pass
    color = "#059669" if online else "#DC2626"
    bg    = "#F0FDF4" if online else "#FEF2F2"
    bdr   = "#BBF7D0" if online else "#FECACA"
    left, right = st.columns([4, 1])
    with left:
        st.markdown(
            f'<div style="background:{bg};border:1.5px solid {bdr};border-radius:12px;'
            f'padding:18px 24px;display:flex;align-items:center;gap:16px">'
            f'<div style="width:12px;height:12px;border-radius:50%;background:{color};'
            f'flex-shrink:0;box-shadow:0 0 8px {color}88"></div>'
            f'<div><div style="font-size:13px;font-weight:800;color:{color}">'
            f'n8n {"Online" if online else "Unreachable"}</div>'
            f'<div style="font-size:11px;color:#64748B;margin-top:2px">{n8n_url}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    with right:
        st.link_button("Open n8n Editor", n8n_url, use_container_width=True)
else:
    st.info(
        "**Run it yourself** — `docker run -it --rm -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n`, "
        "then import the workflows above. Setup notes are in `pipeline/README.md`. "
        "Set `N8N_URL` in Streamlit secrets to show live status here."
    )

styles.footer()
