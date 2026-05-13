"""Configuration loading for managed Codex lanes."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class RepoConfig(BaseModel):
    repo_id: str
    path: str
    role: str = ""
    default_branch: str = "main"


class LaneConfig(BaseModel):
    lane_id: str
    title: str
    state: str
    auto_continue: bool = False
    concurrency: int = Field(default=1, ge=0)
    owner: str = ""
    safety_policy: str = ""


class TaskConfig(BaseModel):
    task_id: str
    lane_id: str
    repo_id: str
    title: str
    state: str = "queued"
    priority: int = 0
    goal: str = ""
    done_criteria: str = ""


class CapabilityConfig(BaseModel):
    capability_id: str
    title: str
    category: str
    status: str
    lane_id: str
    summary: str
    evidence_paths: list[str] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class ControllerIssueConfig(BaseModel):
    issue_id: str
    title: str
    severity: str
    state: str
    lane_id: Optional[str] = None
    task_id: Optional[str] = None
    symptom: str = ""
    root_cause: str = ""
    improvement: str = ""
    evidence: str = ""


class ManagedConfig(BaseModel):
    repos: list[RepoConfig]
    lanes: list[LaneConfig]
    tasks: list[TaskConfig] = Field(default_factory=list)
    capabilities: list[CapabilityConfig] = Field(default_factory=list)
    controller_issues: list[ControllerIssueConfig] = Field(default_factory=list)


def load_config(path: Path) -> ManagedConfig:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return ManagedConfig.model_validate(payload)
