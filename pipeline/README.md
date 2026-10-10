# Annotation Pipeline (n8n)

Two n8n workflows automate the slowest part of building the training set:
getting dive footage to human annotators and getting labelled data back.

Splitting, merging and training are **not** done in n8n — they run locally and
are wired to these workflows over HTTP (webhook in, callback out).

## Workflows

### 1. `workflows/send-annotation-emails.json` — distribution

| Node | Type | Role |
|---|---|---|
| Receive Pipeline Trigger | webhook | `POST /webhook/auv-pipeline-send` starts a round |
| Store Context | code | stashes `callback_url`, `expected`, `save_dir` in workflow static data; fans out one item per annotator |
| Loop Annotators | splitInBatches | one annotator at a time (`batchSize: 1`) |
| Read Zip File | readWriteFile | loads that annotator's clip zip from `zip_path` |
| Send Gmail | gmail | emails the zip with CVAT instructions and the class list |
| Respond OK | respondToWebhook | returns `{status: "emails_sent", count: N}` |

Trigger payload:

```json
{
  "callback_url": "http://host.docker.internal:8000/pipeline/complete",
  "expected": 3,
  "save_dir": "/tmp/auv_replies",
  "classes": ["torpedo_board", "torpedo_hole"],
  "annotators": [
    { "name": "Ayesha", "email": "a@example.com", "part_num": 1, "zip_path": "/data/clips/part1.zip" }
  ]
}
```

### 2. `workflows/receive-annotation-replies.json` — collection

| Node | Type | Role |
|---|---|---|
| Gmail Trigger | gmailTrigger | polls every minute for mail with attachments |
| Filter Zip Attachments | code | keeps `.zip` attachments, drops everything else |
| Save Zip to Disk | readWriteFile | writes `annotated_<sender>.zip` into `save_dir` |
| Check If All Received | code | increments the counter, appends the saved path, sets `allDone` |
| All Received? | if | branches on `received >= expected` |
| Notify Pipeline | httpRequest | POSTs the zip back as base64 to `callback_url` |
| Partial — Log Only | noOp | still waiting on other annotators |

Round state (`callbackUrl`, `expected`, `received`, `savedPaths`) lives in n8n
global static data, so the collector knows when a round is complete without a
database.

## Importing

1. Start n8n: `docker run -it --rm -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n`
2. Open http://localhost:5678 → **Workflows → Import from File**
3. Import both files from `workflows/`
4. Each has a Gmail node with `credentials.gmailOAuth2.id` set to
   `REPLACE_WITH_YOUR_CREDENTIAL_ID` — create a Gmail OAuth2 credential in n8n
   and re-select it on the **Send Gmail** and **Gmail Trigger** nodes
5. Activate both workflows

No credentials or email addresses are stored in these files.

## Known limitations

- Round state is in-memory static data: restarting n8n mid-round loses the count
- `Notify Pipeline` sends only the most recently saved zip, not all of them
- One concurrent round per n8n instance (static data is global, not keyed by round)
