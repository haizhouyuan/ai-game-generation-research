PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS registry_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS repos (
  repo_id TEXT PRIMARY KEY,
  path TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT '',
  default_branch TEXT NOT NULL DEFAULT 'main',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lanes (
  lane_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  state TEXT NOT NULL CHECK (state IN ('enabled', 'paused', 'disabled', 'draining', 'error')),
  auto_continue INTEGER NOT NULL DEFAULT 0 CHECK (auto_continue IN (0, 1)),
  concurrency INTEGER NOT NULL DEFAULT 1 CHECK (concurrency >= 0),
  owner TEXT NOT NULL DEFAULT '',
  safety_policy TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
  task_id TEXT PRIMARY KEY,
  lane_id TEXT NOT NULL REFERENCES lanes(lane_id),
  repo_id TEXT NOT NULL REFERENCES repos(repo_id),
  title TEXT NOT NULL,
  goal TEXT NOT NULL DEFAULT '',
  done_criteria TEXT NOT NULL DEFAULT '',
  state TEXT NOT NULL CHECK (state IN (
    'queued',
    'dispatching',
    'planning',
    'running',
    'waiting_approval',
    'waiting_user',
    'blocked',
    'review_ready',
    'task_complete',
    'needs_retry',
    'interrupted',
    'failed',
    'archiving',
    'archived'
  )),
  priority INTEGER NOT NULL DEFAULT 0,
  thread_id TEXT,
  current_turn_id TEXT,
  base_branch TEXT,
  worktree_path TEXT,
  branch_name TEXT,
  pr_url TEXT,
  dispatch_count INTEGER NOT NULL DEFAULT 0,
  retry_count INTEGER NOT NULL DEFAULT 0,
  max_retries INTEGER NOT NULL DEFAULT 0,
  last_summary TEXT,
  last_worker_status TEXT,
  last_error TEXT,
  blocked_reason TEXT,
  needs_human_reason TEXT,
  next_dispatch_at TEXT,
  last_dispatched_at TEXT,
  last_event_at TEXT,
  completed_at TEXT,
  archived_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS threads (
  thread_id TEXT PRIMARY KEY,
  task_id TEXT REFERENCES tasks(task_id),
  lane_id TEXT REFERENCES lanes(lane_id),
  repo_id TEXT REFERENCES repos(repo_id),
  runtime_status TEXT NOT NULL DEFAULT 'unknown',
  app_status TEXT,
  archived INTEGER NOT NULL DEFAULT 0 CHECK (archived IN (0, 1)),
  last_event_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS turns (
  turn_id TEXT PRIMARY KEY,
  thread_id TEXT NOT NULL REFERENCES threads(thread_id),
  task_id TEXT REFERENCES tasks(task_id),
  state TEXT NOT NULL CHECK (state IN (
    'not_started',
    'in_progress',
    'completed',
    'failed',
    'interrupted',
    'timeout',
    'orphaned'
  )),
  prompt_hash TEXT,
  output_schema_id TEXT,
  started_at TEXT,
  completed_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS codex_events (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  thread_id TEXT REFERENCES threads(thread_id),
  turn_id TEXT REFERENCES turns(turn_id),
  event_type TEXT NOT NULL,
  item_type TEXT,
  payload_json TEXT NOT NULL,
  observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT REFERENCES tasks(task_id),
  lane_id TEXT REFERENCES lanes(lane_id),
  type TEXT NOT NULL,
  path_or_url TEXT NOT NULL,
  sha256 TEXT,
  validation_status TEXT NOT NULL DEFAULT 'unknown',
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence_items (
  evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT REFERENCES tasks(task_id),
  lane_id TEXT REFERENCES lanes(lane_id),
  evidence_type TEXT NOT NULL,
  path_or_url TEXT NOT NULL,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_dependencies (
  task_id TEXT NOT NULL REFERENCES tasks(task_id),
  depends_on_task_id TEXT NOT NULL REFERENCES tasks(task_id),
  relation TEXT NOT NULL DEFAULT 'blocks',
  PRIMARY KEY (task_id, depends_on_task_id)
);

CREATE TABLE IF NOT EXISTS downloads (
  download_id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT REFERENCES tasks(task_id),
  source_url TEXT NOT NULL,
  retained_path TEXT,
  size_bytes INTEGER,
  sha256 TEXT,
  command TEXT,
  no_proxy_proof TEXT,
  status TEXT NOT NULL DEFAULT 'planned',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS capabilities (
  capability_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('available', 'partial', 'blocked', 'planned', 'rejected')),
  lane_id TEXT NOT NULL REFERENCES lanes(lane_id),
  summary TEXT NOT NULL DEFAULT '',
  evidence_paths_json TEXT NOT NULL DEFAULT '[]',
  commands_json TEXT NOT NULL DEFAULT '[]',
  inputs_json TEXT NOT NULL DEFAULT '[]',
  outputs_json TEXT NOT NULL DEFAULT '[]',
  limitations_json TEXT NOT NULL DEFAULT '[]',
  next_steps_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS controller_issues (
  issue_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
  state TEXT NOT NULL CHECK (state IN ('open', 'triaged', 'fixed', 'wont_fix')),
  lane_id TEXT REFERENCES lanes(lane_id),
  task_id TEXT REFERENCES tasks(task_id),
  symptom TEXT NOT NULL DEFAULT '',
  root_cause TEXT NOT NULL DEFAULT '',
  improvement TEXT NOT NULL DEFAULT '',
  evidence TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_lane_state ON tasks(lane_id, state);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_threads_task ON threads(task_id);
CREATE INDEX IF NOT EXISTS idx_events_thread_time ON codex_events(thread_id, observed_at);
CREATE INDEX IF NOT EXISTS idx_artifacts_task ON artifacts(task_id);
CREATE INDEX IF NOT EXISTS idx_evidence_task ON evidence_items(task_id);
CREATE INDEX IF NOT EXISTS idx_capabilities_status ON capabilities(status, category);
CREATE INDEX IF NOT EXISTS idx_controller_issues_state ON controller_issues(state, severity);
