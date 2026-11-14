# iterate_invariant

Repository for the iterate_invariant hackathon. Several people, each with a coding agent, work on one
research direction. The agents share memory through one past.dev project.

## Shared memory (past.dev)

Each Claude Code session opened in this repository is sent to the shared past.dev project when it ends.
Everyone in the project reads everything. Sessions in your other folders are not sent: the plugin is
enabled in this repository's `.claude/settings.json` only.

Nothing is recalled automatically. An agent searches the shared memory when it chooses, with
`python3 tools/recall.py "<question>"`.

### Prior work: check before building

The same project holds the prior work the team has found: papers, blog posts, published results.
One search then answers both "has this been published?" and "did one of us already try this?",
with dates and sources.

- Add one: `python3 tools/add_source.py --id arxiv:2401.12345 --title "..." --date 2024-01-22 --url ... --kind paper fulltext.txt`.
  Send the raw full text, not a summary. Ids use `:`, never `/`. The same id again replaces it.
- Before starting on an idea: `python3 tools/recall.py "<the idea, in the field's own terms>"`.
  Open the sources it names and read the close ones in full.
- Cost: one credit per 350 bytes; a 60,000-character paper is about 170 credits.

What is sent: your typed prompts and the agent's prose replies. Not sent: tool calls and their output,
file contents, diffs. Strings that look like keys are redacted before they leave.

### Join (Claude Code)

1. Get a project key (`past_sk_...`) for the hackathon project from the organizer, privately.
2. Open Claude Code in this repository and trust the folder. Accept the prompt to install the
   `pastdotdev` marketplace and plugin.
3. In a text editor (not in a chat), create `~/.past/config.json`:

   ```json
   { "apiKey": "past_sk_...", "identity": "you@example.com", "recall": false }
   ```

   Then `chmod 600 ~/.past/config.json`. `"recall": false` stops the plugin from adding memories to
   every prompt; `tools/recall.py` reads the same file. Never paste the key into a chat or commit it.
4. Run `/pastdotdev:status`: it should show the key, your identity, and recall off.

`~/.past/config.json` is one file per machine. If you already use past.dev for another project, this
replaces that connection.

Codex users: see https://github.com/pastdotdev/codex-plugin.
