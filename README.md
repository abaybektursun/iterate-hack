# iterate_invariant

Repository for the iterate_invariant hackathon. Several people, each with a coding agent, work on one
research direction. The agents share memory through one past.dev project.

## Shared memory (past.dev)

Each Claude Code session opened in this repository is sent to the shared past.dev project when it ends,
and each prompt gets what past.dev recalls for it. Everyone in the project reads everything. Sessions in
your other folders are not sent: the plugin is enabled in this repository's `.claude/settings.json` only.

What is sent: your typed prompts and the agent's prose replies. Not sent: tool calls and their output,
file contents, diffs. Strings that look like keys are redacted before they leave.

### Join (Claude Code)

1. Get a project key (`past_sk_...`) for the hackathon project from the organizer, privately.
2. Open Claude Code in this repository and trust the folder. Accept the prompt to install the
   `pastdotdev` marketplace and plugin.
3. Run `/plugin configure pastdotdev@pastdotdev` and enter the key and your email as the identity.
   The form masks the key. Never paste the key into a chat or commit it.
4. Run `/pastdotdev:status`: it should show the key and your identity.

`/pastdotdev:connect` and `/plugin configure` write `~/.past/config.json`, which is one file per machine.
If you already use past.dev for another project, this replaces that connection.

Codex users: see https://github.com/pastdotdev/codex-plugin.
