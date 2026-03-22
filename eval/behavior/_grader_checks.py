"""Dispatch tables and check functions for the behavioral grader.

Each check function returns ``(passed, evidence)`` when applicable,
or ``None`` when the check does not match the given assertion.

Three families:
    - **file_check**: operates on ``assertion`` + ``diff``
    - **content_check**: operates on ``assertion`` + ``diff`` + ``transcript``
    - **output_check**: operates on ``assertion`` + ``transcript``
"""
from __future__ import annotations

import re
from typing import Callable

# ===================================================================
# Type aliases
# ===================================================================

Result = tuple[bool, str]

FileCheckFn = Callable[[dict, dict], Result | None]
ContentCheckFn = Callable[[dict, dict, str], Result | None]
OutputCheckFn = Callable[[dict, str], Result | None]

# ===================================================================
# Helper: common CR-file gathering
# ===================================================================

def _cr_files_from(diff: dict, *, include_created: bool = True, include_modified: bool = True) -> list[str]:
    files: list[str] = []
    if include_created:
        files.extend(diff.get("files_created", []))
    if include_modified:
        files.extend(diff.get("files_modified", []))
    return [f for f in files if "backlog/CR-" in f]


def _all_changed(diff: dict) -> list[str]:
    return diff.get("files_created", []) + diff.get("files_modified", [])


def _state_changed(diff: dict) -> bool:
    return any("state.md" in f for f in _all_changed(diff))


# ===================================================================
# FILE CHECKS — named (from _check field)
# ===================================================================

def file_check_schema_compliant(assertion: dict, diff: dict) -> Result | None:
    if assertion.get("_check") != "schema_compliant_structure":
        return None
    cr_files = _cr_files_from(diff)
    passed = len(cr_files) > 0
    evidence = (
        f"CR files present for schema compliance check: {', '.join(cr_files)}"
        if passed
        else "No CR files to check schema compliance"
    )
    return passed, evidence


NAMED_FILE_CHECKS: dict[str, FileCheckFn] = {
    "schema_compliant_structure": file_check_schema_compliant,
}

# ===================================================================
# FILE CHECKS — keyword-based
# ===================================================================

def file_check_cr_created(assertion: dict, diff: dict) -> Result | None:
    text = assertion["text"].lower()
    if not ("cr" in text and ("created" in text or "new" in text) and "backlog" in text):
        return None
    cr_files = [f for f in diff.get("files_created", []) if "backlog/CR-" in f and f.endswith(".md")]
    passed = len(cr_files) > 0
    evidence = (
        f"Found new CR files: {', '.join(cr_files)}"
        if passed
        else "No new CR-*.md files found in .devpace/backlog/"
    )
    return passed, evidence


def file_check_state_updated(assertion: dict, diff: dict) -> Result | None:
    text = assertion["text"].lower()
    if not ("state.md" in text and ("updated" in text or "update" in text)):
        return None
    all_files = _all_changed(diff)
    state_files = [f for f in all_files if "state.md" in f]
    passed = len(state_files) > 0
    evidence = (
        f"state.md modified: {', '.join(state_files)}"
        if passed
        else "state.md not found in changed files"
    )
    return passed, evidence


def file_check_state_version(assertion: dict, diff: dict) -> Result | None:
    text = assertion["text"].lower()
    if not ("state.md" in text and "version" in text):
        return None
    all_files = _all_changed(diff)
    state_files = [f for f in all_files if "state.md" in f]
    passed = len(state_files) > 0
    evidence = (
        "state.md present in changed files (version marker check)"
        if passed
        else "state.md not in changed files"
    )
    return passed, evidence


def file_check_context_generated(assertion: dict, diff: dict) -> Result | None:
    text = assertion["text"].lower()
    if not ("context.md" in text and ("generated" in text or "created" in text)):
        return None
    ctx_files = [f for f in diff.get("files_created", []) if "context.md" in f]
    passed = len(ctx_files) > 0
    evidence = (
        f"context.md created: {', '.join(ctx_files)}"
        if passed
        else "context.md not found in created files"
    )
    return passed, evidence


def file_check_root_cause(assertion: dict, diff: dict) -> Result | None:
    text = assertion["text"].lower()
    if not ("root cause" in text and "section" in text):
        return None
    cr_files = [f for f in _all_changed(diff) if "backlog/CR-" in f]
    if cr_files:
        return True, f"CR files modified (root cause section check): {', '.join(cr_files)}"
    return False, "No CR files modified"


def file_check_execution_plan(assertion: dict, diff: dict) -> Result | None:
    text = assertion["text"].lower()
    if not ("execution plan" in text and ("section" in text or "filled" in text)):
        return None
    cr_files = [f for f in _all_changed(diff) if "backlog/CR-" in f]
    passed = len(cr_files) > 0
    evidence = (
        f"CR files with execution plan: {', '.join(cr_files)}"
        if passed
        else "No CR files modified"
    )
    return passed, evidence


def file_check_acceptance_criteria(assertion: dict, diff: dict) -> Result | None:
    text = assertion["text"].lower()
    if not ("acceptance criteria" in text and "cr" in text):
        return None
    cr_files = [f for f in _all_changed(diff) if "backlog/CR-" in f]
    passed = len(cr_files) > 0
    evidence = (
        f"CR files modified (acceptance criteria check): {', '.join(cr_files)}"
        if passed
        else "No CR files modified"
    )
    return passed, evidence


# Order matters: more specific patterns first to avoid shadowing.
KEYWORD_FILE_CHECKS: list[FileCheckFn] = [
    file_check_cr_created,
    file_check_state_updated,
    file_check_state_version,
    file_check_context_generated,
    file_check_root_cause,
    file_check_execution_plan,
    file_check_acceptance_criteria,
]


# ===================================================================
# CONTENT CHECKS — named (from _check field)
# ===================================================================

def content_check_state_current_work(assertion: dict, diff: dict, transcript: str) -> Result | None:
    if assertion.get("_check") != "state_current_work":
        return None
    passed = _state_changed(diff)
    evidence = (
        "state.md was modified (current-work presumed updated)"
        if passed
        else "state.md not modified"
    )
    return passed, evidence


def content_check_state_next_step(assertion: dict, diff: dict, transcript: str) -> Result | None:
    if assertion.get("_check") != "state_next_step":
        return None
    passed = _state_changed(diff)
    evidence = (
        "state.md was modified (next-step presumed updated)"
        if passed
        else "state.md not modified"
    )
    return passed, evidence


def content_check_state_last_updated(assertion: dict, diff: dict, transcript: str) -> Result | None:
    if assertion.get("_check") != "state_last_updated":
        return None
    passed = _state_changed(diff)
    evidence = (
        "state.md was modified (timestamp presumed updated)"
        if passed
        else "state.md not modified"
    )
    return passed, evidence


def content_check_cr_status_valid(assertion: dict, diff: dict, transcript: str) -> Result | None:
    if assertion.get("_check") != "cr_status_valid":
        return None
    cr_files = _cr_files_from(diff)
    passed = len(cr_files) > 0
    evidence = f"CR files changed: {', '.join(cr_files)}" if passed else "No CR files changed"
    return passed, evidence


def content_check_cr_events_updated(assertion: dict, diff: dict, transcript: str) -> Result | None:
    if assertion.get("_check") != "cr_events_updated":
        return None
    cr_files = _cr_files_from(diff)
    passed = len(cr_files) > 0
    evidence = f"CR files updated (events presumed appended): {', '.join(cr_files)}" if passed else "No CR files updated"
    return passed, evidence


def content_check_cr_events_have_timestamp(assertion: dict, diff: dict, transcript: str) -> Result | None:
    if assertion.get("_check") != "cr_events_have_timestamp":
        return None
    cr_files = _cr_files_from(diff)
    passed = len(cr_files) > 0
    evidence = "CR events with timestamps (structural check)" if passed else "No CR files to check"
    return passed, evidence


def content_check_required_fields_present(assertion: dict, diff: dict, transcript: str) -> Result | None:
    if assertion.get("_check") != "required_fields_present":
        return None
    cr_files = _cr_files_from(diff)
    passed = len(cr_files) > 0
    evidence = f"CR files for field check: {', '.join(cr_files)}" if passed else "No CR files"
    return passed, evidence


NAMED_CONTENT_CHECKS: dict[str, ContentCheckFn] = {
    "state_current_work": content_check_state_current_work,
    "state_next_step": content_check_state_next_step,
    "state_last_updated": content_check_state_last_updated,
    "cr_status_valid": content_check_cr_status_valid,
    "cr_events_updated": content_check_cr_events_updated,
    "cr_events_have_timestamp": content_check_cr_events_have_timestamp,
    "required_fields_present": content_check_required_fields_present,
}

# ===================================================================
# CONTENT CHECKS — keyword-based
# ===================================================================

def content_check_cr_type(assertion: dict, diff: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("cr type" in text or "type is" in text):
        return None
    type_match = None
    if "'feature'" in text or '"feature"' in text:
        type_match = "feature"
    elif "'defect'" in text or '"defect"' in text:
        type_match = "defect"
    elif "'hotfix'" in text or '"hotfix"' in text:
        type_match = "hotfix"

    if type_match:
        pattern = rf"type[:\s]*{type_match}"
        if re.search(pattern, transcript, re.IGNORECASE):
            return True, f"Found type '{type_match}' reference in transcript"
        else:
            cr_created = any("backlog/CR-" in f for f in diff.get("files_created", []))
            if cr_created:
                return True, f"CR file created (type={type_match} expected but not confirmed in transcript)"
            return False, f"No evidence of CR with type={type_match}"
    return False, "Could not determine expected CR type from assertion"


def content_check_cr_status(assertion: dict, diff: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("cr status" in text or "status transitions" in text or "status remains" in text):
        return None
    if "remains" in text:
        return True, "CR status unchanged (no counter-evidence in diff)"
    else:
        cr_files = diff.get("files_modified", []) + diff.get("files_created", [])
        cr_changed = any("backlog/CR-" in f for f in cr_files)
        if cr_changed:
            return True, f"CR files changed (status transition expected): {', '.join(f for f in cr_files if 'CR-' in f)}"
        return False, "No CR status transition detected"


def content_check_cr_complexity(assertion: dict, diff: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("complexity" in text and ("is s" in text or "is m" in text or "is l" in text)):
        return None
    passed = any("backlog/CR-" in f for f in _all_changed(diff))
    evidence = "CR file changed (complexity field check)" if passed else "No CR file changed"
    return passed, evidence


def content_check_cr_severity(assertion: dict, diff: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if "severity" not in text:
        return None
    passed = any("backlog/CR-" in f for f in _all_changed(diff))
    evidence = "CR file changed (severity field check)" if passed else "No CR file changed"
    return passed, evidence


def content_check_cr_intent_section(assertion: dict, diff: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("intent" in text and "section" in text):
        return None
    cr_changed = any("backlog/CR-" in f for f in _all_changed(diff))
    evidence = "CR file present (intent section check)" if cr_changed else "No CR file"
    return cr_changed, evidence


def content_check_cr_scope_section(assertion: dict, diff: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("scope" in text and "section" in text):
        return None
    cr_changed = any("backlog/CR-" in f for f in _all_changed(diff))
    evidence = "CR file present (scope section check)" if cr_changed else "No CR file"
    return cr_changed, evidence


def content_check_cr_event_log(assertion: dict, diff: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("event log" in text or "event_log" in text):
        return None
    cr_changed = any("backlog/CR-" in f for f in _all_changed(diff))
    evidence = "CR file changed (event log check)" if cr_changed else "No CR file changed"
    return cr_changed, evidence


def content_check_complexity_assessed(assertion: dict, diff: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("complexity" in text and ("assessed" in text or "detected" in text)):
        return None
    complexity_patterns = [r"\b[SMLX]{1,2}\b", r"complexity[:\s]*(S|M|L|XL)", r"(simple|medium|large|extra.?large)"]
    for pat in complexity_patterns:
        if re.search(pat, transcript, re.IGNORECASE):
            return True, f"Complexity reference found in transcript (pattern: {pat})"
    return False, "No complexity assessment found in transcript"


def content_check_acceptance_gwt(assertion: dict, diff: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("acceptance criteria" in text and "given/when/then" in text):
        return None
    gwt_pattern = r"(given|when|then)"
    matches = re.findall(gwt_pattern, transcript, re.IGNORECASE)
    passed = len(matches) >= 3
    evidence = (
        f"Found {len(matches)} Given/When/Then keywords in transcript"
        if passed
        else "Insufficient Given/When/Then format evidence"
    )
    return passed, evidence


def content_check_ambiguity_markers(assertion: dict, diff: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("[待确认]" in assertion["text"] or "ambiguity" in text):
        return None
    if "[待确认]" in transcript or "待确认" in transcript:
        return True, "Found [待确认] ambiguity markers in transcript"
    return False, "No [待确认] markers found in transcript"


def content_check_decision_record(assertion: dict, diff: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if "decision record" not in text:
        return None
    cr_changed = any("backlog/CR-" in f for f in _all_changed(diff))
    evidence = "CR file changed (decision records check)" if cr_changed else "No CR file changed"
    return cr_changed, evidence


def content_check_state_concise(assertion: dict, diff: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("state.md" in text and "concise" in text):
        return None
    passed = _state_changed(diff)
    evidence = (
        "state.md modified (conciseness to be verified by G3 if needed)"
        if passed
        else "state.md not modified"
    )
    return passed, evidence


KEYWORD_CONTENT_CHECKS: list[ContentCheckFn] = [
    content_check_cr_type,
    content_check_cr_status,
    content_check_cr_complexity,
    content_check_cr_severity,
    content_check_cr_intent_section,
    content_check_cr_scope_section,
    content_check_cr_event_log,
    content_check_complexity_assessed,
    content_check_acceptance_gwt,
    content_check_ambiguity_markers,
    content_check_decision_record,
    content_check_state_concise,
]


# ===================================================================
# OUTPUT CHECKS — named (from _check field)
# ===================================================================

def output_check_no_internal_ids(assertion: dict, transcript: str) -> Result | None:
    if assertion.get("_check") != "no_internal_ids":
        return None
    id_pattern = r"\b(CR|PF|BR|OBJ)-\d{3}\b"
    found = re.findall(id_pattern, transcript)
    passed = len(found) == 0
    evidence = (
        "No internal IDs exposed in output"
        if passed
        else f"Found internal IDs: {', '.join(found[:5])}"
    )
    return passed, evidence


def output_check_no_state_machine_terms(assertion: dict, transcript: str) -> Result | None:
    if assertion.get("_check") != "no_state_machine_terms":
        return None
    sm_terms = ["developing", "in_review", "verifying", "approved", "merged"]
    found = [t for t in sm_terms if re.search(rf"\b{t}\b", transcript)]
    passed = len(found) == 0
    evidence = (
        "No state machine terminology in output"
        if passed
        else f"Found state machine terms: {', '.join(found)}"
    )
    return passed, evidence


def output_check_natural_language(assertion: dict, transcript: str) -> Result | None:
    if assertion.get("_check") != "natural_language":
        return None
    has_prose = len(transcript) > 50
    evidence = (
        f"Output is {len(transcript)} chars of natural language"
        if has_prose
        else "Output too short or not natural language"
    )
    return has_prose, evidence


def output_check_concise(assertion: dict, transcript: str) -> Result | None:
    if assertion.get("_check") != "output_concise":
        return None
    lines = [line for line in transcript.split("\n") if line.strip()]
    passed = len(lines) <= 5
    evidence = f"Output has {len(lines)} non-empty lines (target: <=3)"
    return passed, evidence


NAMED_OUTPUT_CHECKS: dict[str, OutputCheckFn] = {
    "no_internal_ids": output_check_no_internal_ids,
    "no_state_machine_terms": output_check_no_state_machine_terms,
    "natural_language": output_check_natural_language,
    "output_concise": output_check_concise,
}

# ===================================================================
# OUTPUT CHECKS — keyword-based
# ===================================================================

def output_check_complexity_detected(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("complexity" in text and "detected" in text):
        return None
    complexity_refs = re.findall(
        r"(complexity|复杂度)[:\s]*(S|M|L|XL|simple|medium|large)",
        transcript,
        re.IGNORECASE,
    )
    passed = len(complexity_refs) > 0
    evidence = (
        f"Complexity detection in output: {complexity_refs[:3]}"
        if passed
        else "No complexity detection in output"
    )
    return passed, evidence


def output_check_execution_plan_steps(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("execution plan" in text and ("numbered" in text or "steps" in text)):
        return None
    step_pattern = r"(?:步骤|step|phase|\d+[\.\):])\s*\d*"
    steps = re.findall(step_pattern, transcript, re.IGNORECASE)
    passed = len(steps) >= 2
    evidence = (
        f"Found {len(steps)} step references in output"
        if passed
        else "No numbered execution plan found"
    )
    return passed, evidence


def output_check_intent_checkpoint(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("intent checkpoint" in text or "confirm scope" in text):
        return None
    checkpoint_patterns = [
        r"确认|confirm|scope|范围|方案|approach|checkpoint",
        r"\?|？",
    ]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in checkpoint_patterns)
    evidence = (
        "Intent checkpoint indicators found in transcript"
        if found
        else "No intent checkpoint detected"
    )
    return found, evidence


def output_check_solution_confirmation(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("solution confirmation" in text or "asks for user approval" in text):
        return None
    gate_patterns = [r"确认|approve|confirm|同意|proceed"]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in gate_patterns)
    evidence = "Confirmation gate detected" if found else "No confirmation gate detected"
    return found, evidence


def output_check_pause_point(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if "pause point" not in text:
        return None
    pause_patterns = [r"pause|暂停|阶段|phase|checkpoint"]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in pause_patterns)
    evidence = "Pause points referenced" if found else "No pause points found"
    return found, evidence


def output_check_risk_scan(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("risk" in text and ("pre-scan" in text or "scan" in text)):
        return None
    risk_patterns = [r"risk|风险|隐患|注意"]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in risk_patterns)
    evidence = "Risk assessment found" if found else "No risk pre-scan detected"
    return found, evidence


def output_check_gate_reflection(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("gate" in text and "reflection" in text):
        return None
    gate_patterns = [r"gate|门禁|reflection|观察|observation"]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in gate_patterns)
    evidence = "Gate reflection content found" if found else "No gate reflection detected"
    return found, evidence


def output_check_non_blocking(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("non-blocking" in text or "non blocking" in text):
        return None
    nb_patterns = [r"non.?blocking|不阻断|观察|observation|建议|suggestion"]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in nb_patterns)
    evidence = "Non-blocking language found" if found else "No non-blocking indicators"
    return found, evidence


def output_check_transparency_summary(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("transparency" in text and "summary" in text):
        return None
    summary_patterns = [r"(文件|files|决策|decisions|状态|status|变更|changes)"]
    matches = [p for p in summary_patterns if re.search(p, transcript, re.IGNORECASE)]
    passed = len(matches) >= 1
    evidence = f"Summary elements found: {len(matches)}" if passed else "No summary elements"
    return passed, evidence


def output_check_drift_detection(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("drift" in text and ("detection" in text or "triggered" in text or "warning" in text)):
        return None
    drift_patterns = [r"drift|漂移|偏离|scope.*expand|范围.*扩展"]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in drift_patterns)
    evidence = "Drift detection indicators found" if found else "No drift detection"
    return found, evidence


def output_check_split_suggestion(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("split" in text and "suggestion" in text):
        return None
    split_patterns = [r"split|拆分|分拆|independent.*CR|独立"]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in split_patterns)
    evidence = "Split suggestion found" if found else "No split suggestion"
    return found, evidence


def output_check_accelerated_path(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("accelerated" in text and "path" in text):
        return None
    accel_patterns = [r"加速|accelerat|跳过|skip.*review|紧急"]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in accel_patterns)
    evidence = "Accelerated path language found" if found else "No accelerated path"
    return found, evidence


def output_check_post_hoc(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("post-hoc" in text or "post hoc" in text):
        return None
    posthoc_patterns = [r"post.?hoc|事后|补审|approval.*after|审批"]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in posthoc_patterns)
    evidence = "Post-hoc reminder found" if found else "No post-hoc reminder"
    return found, evidence


def output_check_step_progress(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("step" in text and ("progress" in text or "completion" in text or "1-line" in text)):
        return None
    step_patterns = [r"步骤.*\d+/\d+|step.*\d+.*of.*\d+|\[\d+/\d+\]"]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in step_patterns)
    evidence = "Step progress format found" if found else "No step progress format"
    return found, evidence


def output_check_compact_suggestion(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("compact" in text and "suggestion" in text):
        return None
    compact_patterns = [r"/compact|compact|压缩|精简"]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in compact_patterns)
    evidence = "Compact suggestion found" if found else "No compact suggestion"
    return found, evidence


def output_check_gate2(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("gate2" in text or "gate 2" in text):
        return None
    g2_patterns = [r"gate.?2|门禁.?2|review|boundary|acceptance"]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in g2_patterns)
    evidence = "Gate 2 content found" if found else "No Gate 2 content"
    return found, evidence


def output_check_user_informed(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("user informed" in text or "informs user" in text):
        return None
    inform_patterns = [r"告知|通知|inform|note|提醒"]
    found = any(re.search(p, transcript, re.IGNORECASE) for p in inform_patterns)
    evidence = "User-informing language found" if found else "No user notification"
    return found, evidence


def output_check_confirm(assertion: dict, transcript: str) -> Result | None:
    text = assertion["text"].lower()
    if not ("output" in text and "confirm" in text):
        return None
    passed = len(transcript) > 20
    evidence = f"Output present ({len(transcript)} chars)" if passed else "Minimal output"
    return passed, evidence


KEYWORD_OUTPUT_CHECKS: list[OutputCheckFn] = [
    output_check_complexity_detected,
    output_check_execution_plan_steps,
    output_check_intent_checkpoint,
    output_check_solution_confirmation,
    output_check_pause_point,
    output_check_risk_scan,
    output_check_gate_reflection,
    output_check_non_blocking,
    output_check_transparency_summary,
    output_check_drift_detection,
    output_check_split_suggestion,
    output_check_accelerated_path,
    output_check_post_hoc,
    output_check_step_progress,
    output_check_compact_suggestion,
    output_check_gate2,
    output_check_user_informed,
    output_check_confirm,
]
