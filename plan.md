# ScratchBot — Implementation Checklist (MVP → GA)

**Purpose:** A pragmatic, human‑verifiable checklist you (and async agents) can follow. Each item includes a **Test** you can run to confirm it works.

Legend: ☐ todo · ☐/☑ substeps · ⭐ critical path · 🧪 human test · 🧰 artifacts

---

## Phase 0 — Bootstrap & Naming

- ☑ Project artifacts use **ScratchBot** branding (repo name, package names, UI strings, commit messages)

  - 🧪 Test: Open any PR comment from the bot; it should say “ScratchBot” everywhere.

- ☑ Initialize monorepo or polyrepo (api, worker, ui, cli, infra)

  - 🧰 `apps/api`, `apps/worker`, `apps/ui`, `packages/cli`, `infra/compose.yml`

---

## Phase 1 — GitHub Integration (App + OAuth)

- ⭐ ☐ Create **GitHub App** (per‑repo install): permissions `contents: read/write`, `pull_requests: write`; webhook events `pull_request`, `issue_comment`, `installation`.

  - 🧰 App ID, private key (PEM), webhook secret.
  - 🧪 Test: From the App settings, deliver a test ping → API returns 200 and logs delivery.

- ⭐ ☐ Implement **/webhooks/github** endpoint with signature verification

  - 🧪 Test: Real webhook from GitHub shows `valid=true` in logs; invalid signature returns 401.

- ⭐ ☐ Implement **GitHub OAuth** for user login (PKCE/device flow acceptable)

  - 🧪 Test: Log in via UI → profile shows login + list of accessible repos.

- ☐ Repo installation flow in UI (detect missing install → deep‑link to install)

  - 🧪 Test: Try accessing a repo without install → UI prompts install; after install, repo appears.

---

## Phase 2 — Data & Infra Foundations

- ⭐ ☐ Provision **Postgres** (jobs, items, audits, commits, users, repos, installations)

  - 🧰 SQL migrations; connection via env `POSTGRES_URL`
  - 🧪 Test: `npm run db:migrate` succeeds; tables exist; health endpoint hits DB.

- ⭐ ☐ Provision **Redis** (BullMQ queue)

  - 🧪 Test: Enqueue a dummy job → worker consumes → status moves `pending→running→done`.

- ☐ Structured logging (pino) with `job_id` correlation

  - 🧪 Test: Trigger a job, then grep logs by the job ID and see all steps.

- ☐ Purge job data after **30 days** (cron)

  - 🧪 Test: Set retention to 1 minute in dev; create job; verify deletion after TTL.

---

## Phase 3 — Git Adapter & Repo Ops

- ⭐ ☐ Implement checkout of **PR branch** using installation token

  - 🧪 Test: Given `owner/repo#PR`, code is cloned to a temp dir and head SHA matches GitHub.

- ⭐ ☐ Implement commit & push (per‑file and batch modes)

  - 🧪 Test: Write a dummy `TEST.md`; push; verify commit appears on PR branch with expected message.

- ☐ Respect `.scratchbot.yml` config (commit_mode, docs_dir, include/exclude, threshold)

  - 🧪 Test: Change `commit_mode` to `batch` and run apply; verify single commit.

---

## Phase 4 — Heuristics & Parsers (JS/TS, Python)

- ⭐ ☐ JS/TS AST using **ts‑morph** → exported symbols (functions/classes/interfaces), file LoC

  - 🧪 Test: For a fixture package, API returns symbol list and LoC counts matching `wc -l` ±1.

- ⭐ ☐ Python AST (built‑in `ast` + heuristics) → public symbols, file LoC

  - 🧪 Test: For a fixture module, detect classes/functions; ignore `_private`.

- ⭐ ☐ Missing‑doc rule: **Files > 300 LoC** or packages >300 LoC with no README

  - 🧪 Test: Create a 301‑line file without a `.md`; plan must include it as Missing.

- ⭐ ☐ Needs‑update rules: exported signature deltas; README section presence; env var additions; REST route additions

  - 🧪 Test: Change a function signature; plan marks README for update with reason.

- ☐ Exclusion rules for deps/build dirs; dependency discovery via lockfiles

  - 🧪 Test: Add `node_modules/` with huge files; analyzer ignores; token estimate unchanged.

---

## Phase 5 — Planning Pipeline (Model Phase 1)

- ⭐ ☐ Implement **Plan Builder**: assemble diff + filtered tree + symbol summaries under **≤150k tokens**

  - 🧪 Test: For a large fixture, builder outputs prompt size report; if >150k, system produces a **prune request** payload.

- ⭐ ☐ Call GPT‑5 Plan prompt → structured JSON `{missing[], needs_update[]}` with `reason`, `estEffort`, `estTokens`

  - 🧪 Test: Snapshot JSON against golden file; schema validates; no free‑text outside fields.

- ⭐ ☐ Post **Docs Plan** to PR (single sticky comment) + `scratchbot/plan` status

  - 🧪 Test: Open PR triggers comment within ≤2 minutes; rerun replaces same comment (no spam).

- ☐ Slash commands: `/scratchbot apply ...`, `/scratchbot dismiss ...`, `/scratchbot mode ...`

  - 🧪 Test: Comment `/scratchbot apply all-missing` → webhook enqueues apply job.

---

## Phase 6 — Generation Pipeline (Model Phase 2)

- ⭐ ☐ Prompt for Markdown generation using templates (README, component, class)

  - 🧪 Test: For a selected item, model returns valid Markdown with required sections.

- ⭐ ☐ Anti‑hallucination checks: reconcile signatures vs AST; block unverifiable claims; insert `TODO (owner)` markers

  - 🧪 Test: Remove an API symbol from code; generator must not reference it.

- ⭐ ☐ Apply commits to PR branch (per selected items; per‑file/batch)

  - 🧪 Test: Approve two items; verify two commits (per‑file mode) with correct paths under docs_dir/colocated.

- ☐ Dependency lookup: fetch npm/PyPI README/types only for versions in lockfiles

  - 🧪 Test: Add a dep `lodash@4.x`; generator may cite method names used in code; log source as npmjs.

---

## Phase 7 — Web UI (Outside Actions)

- ⭐ ☐ GitHub OAuth login + repo picker (only collaborator repos)

  - 🧪 Test: Non‑collaborator repo doesn’t appear; collaborator repo does.

- ⭐ ☐ **New Job** page: select repo/branch; choose Missing/Updates; optional docs_dir; run

  - 🧪 Test: Start job from UI; see it in Jobs list with `running→needs_approval`.

- ⭐ ☐ **Docs Prompt PR** page: prompt with `@file` mentions; open PR with initial Docs Plan

  - 🧪 Test: Enter `@server.py document this, focus on the API` → PR opens with that text and a plan.

- ⭐ ☐ **Job Detail**: list items; filters; estimates; diff preview (rendered Markdown + raw diff); Select‑All Missing/Updates; **Apply** button

  - 🧪 Test: Select two items → Apply → commits appear on branch; UI shows commit SHAs.

- ☐ **Rebase & Recompute** flow when base branch moves

  - 🧪 Test: Advance base; click Rebase; plan recomputed; audit notes old/new SHAs.

- ☐ **Audit Log** page with export JSON/CSV

  - 🧪 Test: Export contains actions, actors, times, commit SHAs.

---

## Phase 8 — CLI (Local Runs)

- ⭐ ☐ `scratchbot` CLI: `auth login`, `analyze`, `plan show`, `apply`, `open-pr`

  - 🧪 Test: Run `scratchbot analyze --repo owner/repo --ref HEAD --missing` → prints Plan markdown identical to PR comment.

- ☐ Distribute via `npm` and/or `pipx`

  - 🧪 Test: Fresh machine can install and run `scratchbot --version`.

---

## Phase 9 — Deployment (Raspberry Pi Swarm + CapRover)

- ⭐ ☐ Build **multi‑arch Docker images** (arm64/amd64) for api/worker/ui

  - 🧪 Test: `docker run` each image; health checks pass.

- ⭐ ☐ CapRover apps for `api`, `worker`, `ui`, `redis`, `postgres`

  - 🧪 Test: Access UI via HTTPS; create job; watch worker logs consume it.

- ☐ `.env` secret management in CapRover; volumes for Postgres

  - 🧪 Test: Restart containers; data persists; secrets not printed in logs.

---

## Phase 10 — Quality Gates & E2E

- ⭐ ☐ **Fixture repos** (JS/TS, Python) with known missing docs and API diffs

  - 🧪 Test: Opening a PR in each fixture yields correct Missing/Update counts (match golden numbers).

- ⭐ ☐ **Golden tests** for generated Markdown (stable prompts with seeds)

  - 🧪 Test: CI compares generated docs to goldens (allow small whitespace diffs).

- ☐ Rate‑limit/backoff behavior mocked; DLQ surfaced in UI

  - 🧪 Test: Force 429 from model provider; job retries; UI shows transient error then success.

- ☐ Idempotency: re‑running apply on same job doesn’t double‑commit

  - 🧪 Test: Click Apply twice; second run should no‑op with audit entry.

---

## Phase 11 — Product Polish for Selling It

- ☐ Branding: logo, “ScratchBot” wording in UI/PR comments/commit messages

  - 🧪 Test: PR comment header reads `## 📚 Docs Plan (ScratchBot)`.

- ☐ Billing placeholder (no charges yet): capture org slug for future metering

  - 🧪 Test: New install stores org/repo IDs; can attribute jobs to org.

- ☐ Terms/Privacy placeholders + support link

  - 🧪 Test: Footer links render; docs pages load.

---

## Cut‑and‑Paste Smoke Tests (for you)

1. **PR Plan Smoke Test**

   - Create a branch changing a 350‑line file without README; open PR.
   - Expect: PR comment within 2 minutes listing that file under **Missing** with reason and estimates.

2. **Apply Commits Smoke Test**

   - Comment `/scratchbot apply all-missing`.
   - Expect: Commits land on PR branch (per‑file mode) with messages `docs: add <path> (ScratchBot)`; PR shows updated files.

3. **Web UI Job Smoke Test**

   - In UI, start a job on `main` with “Missing” only.
   - Expect: Job card shows `needs_approval`; open job → select item(s) → Apply → commits appear.

4. **Docs Prompt PR**

   - In UI, open a PR with prompt `@server.py document this, focus on the API`.
   - Expect: New PR titled “ScratchBot: docs prompt” containing your prompt and an initial Docs Plan.

5. **Token Guardrail**

   - Add a giant folder; rerun job.
   - Expect: UI prompts to prune paths; plan generation waits until you confirm exclusions.

---

## Tracking Template (duplicate per repo)

```
Repo: <owner/repo>
PR #: <id>   Ref: <branch/sha>

[ ] Phase 1 App+OAuth
[ ] Phase 2 Data/Infra
[ ] Phase 3 Git Ops
[ ] Phase 4 Heuristics
[ ] Phase 5 Plan
[ ] Phase 6 Generate+Apply
[ ] Phase 7 Web UI
[ ] Phase 8 CLI
[ ] Phase 9 Deploy
[ ] Phase 10 E2E
[ ] Phase 11 Polish

Notes:
- Blockers:
- Decisions:
```

---

**Done =** Phases 1–7 green; smoke tests 1–4 pass in a real monorepo; audits retained for 30 days; images live on CapRover and survive restarts.
