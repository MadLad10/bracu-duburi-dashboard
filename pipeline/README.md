# Annotation Pipeline (n8n)

Two n8n workflows automate the slowest part of building the training set: getting
dive footage to human annotators and getting labelled data back.

Splitting, merging and training are **not** done in n8n — they run locally and are
wired to these workflows over HTTP: a webhook starts a round, and a callback fires
once every annotator has replied.

## Verification status

Both workflows were executed on **n8n 2.26.8** and complete successfully:

- a round of 2 annotators is seeded, each clip zip is read and attached as binary
- the first reply is saved and the round correctly does **not** complete
- a duplicate reply from the same annotator does not advance the count
- the second distinct sender completes the round and fires the callback exactly
  once, as multipart form data with the zip attached

**Not verified:** the Gmail nodes themselves. Sending and the Gmail trigger need a
real Gmail OAuth2 credential, so in testing they were stubbed (send) and simulated
(receive, by reproducing the trigger's `From` header + `attachment_N` binary output
shape). Everything downstream of the trigger is exercised for real.

## Required configuration

**File access must be allowlisted.** n8n blocks filesystem access from the
`readWriteFile` node by default; without this, every file step fails with
`Access to the file is not allowed`:

```
N8N_RESTRICT_FILE_ACCESS_TO=/tmp
```

Point it at wherever the clips, reply zips and round-state file live. In the Docker
command below that is `/tmp`; for anything real, mount a volume and use that path.

Round state lives in `/tmp/auv_round_state.json`, written by the send workflow and
read by the receive workflow. It is deliberately a **file**, not n8n workflow static
data: `$getWorkflowStaticData('global')` is scoped to the workflow that writes it,
so the receive workflow can never see what the send workflow stored there.

## Workflows

### 1. `workflows/send-annotation-emails.json` — distribution (9 nodes)

| Node | Type | Role |
|---|---|---|
| Receive Pipeline Trigger | webhook | `POST /webhook/auv-pipeline-send` starts a round |
| Build Round State | code | validates the payload, builds the round record |
| State to File | convertToFile | serialises it to JSON |
| Write Round State | readWriteFile | writes `/tmp/auv_round_state.json` |
| Fan Out Annotators | code | one item per annotator, carrying the class list |
| Loop Annotators | splitInBatches | one annotator at a time |
| Read Clip Zip | readWriteFile | loads that annotator's clip into binary `data` |
| Send Gmail | gmail | emails the zip with CVAT instructions |
| Respond OK | respondToWebhook | `{status, round_id, expected}` |

Trigger payload (`callback_url` and a non-empty `annotators` array are required;
each annotator needs `email` and `zip_path`, or the node throws):

```json
{
  "callback_url": "http://host.docker.internal:8000/pipeline/complete",
  "save_dir": "/tmp/auv_replies",
  "classes": ["torpedo_board", "torpedo_hole"],
  "annotators": [
    { "name": "Ayesha", "email": "a@example.com", "part_num": 1, "zip_path": "/tmp/clips/part1.zip" }
  ]
}
```

Note `Loop Annotators` output **0 is `done`** and output **1 is `loop`**. Wiring
them the other way round emails only on the final iteration.

### 2. `workflows/receive-annotation-replies.json` — collection (12 nodes)

| Node | Type | Role |
|---|---|---|
| Gmail Trigger | gmailTrigger | polls every minute, `downloadAttachments` on |
| Extract Zip Attachment | code | finds the `.zip` among `attachment_N` binaries, parses the sender |
| Save Zip to Disk | readWriteFile | writes `/tmp/auv_reply_<sender>.zip` |
| Read Round State | readWriteFile | reads the round file (tolerates it missing) |
| Parse Round State | extractFromFile | JSON → `json.state` |
| Update Round State | code | counts **distinct** senders, sets `all_done` |
| State to File / Write Round State | convertToFile, readWriteFile | persists the updated round |
| All Received? | if | branches on `all_done` |
| Read Saved Zip | readWriteFile | loads the zip for upload |
| Notify Pipeline | httpRequest | multipart POST to `callback_url` with the zip |
| Partial - Log Only | noOp | still waiting on other annotators |

`downloadAttachments` is essential: without it the trigger fetches no attachment
binaries at all. Attachments arrive as **binary** properties (`attachment_0`, …),
not as `json.attachments[].content`.

The callback is multipart rather than base64-in-JSON because `require('fs')` is not
available inside n8n expressions.

## Importing

1. Start n8n:

   ```bash
   docker run -it --rm -p 5678:5678 \
     -e N8N_RESTRICT_FILE_ACCESS_TO=/tmp \
     -v n8n_data:/home/node/.n8n n8nio/n8n
   ```

2. Open http://localhost:5678 → **Workflows → Import from File**, import both files
   from `workflows/`.
3. Create a Gmail OAuth2 credential, then re-select it on **Send Gmail** and
   **Gmail Trigger** — both ship with `credentials.gmailOAuth2.id` set to
   `REPLACE_WITH_YOUR_CREDENTIAL_ID`.
4. Activate both workflows.

No credentials or email addresses are stored in these files.

## Known limitations

- **One round at a time per instance.** The state file path is fixed, so a second
  concurrent round would overwrite the first.
- Reply zips are written flat as `/tmp/auv_reply_<sender>.zip`, keyed on the local
  part of the sender's address — two annotators at different domains with the same
  local part would collide. `save_dir` in the payload is recorded in the round state
  but not currently used for the reply filenames.
- The callback uploads only the most recent zip; the others are referenced by path
  in the `saved_paths` field, which assumes the receiver shares the filesystem.
- If the state file is missing or unreadable, `expected` is 0 and the round never
  completes. That is deliberate — it fails closed rather than firing the callback on
  the first reply.
- Restarting n8n is safe (state is on disk), but deleting the state file mid-round
  loses the count.
