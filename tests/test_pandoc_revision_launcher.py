from pathlib import Path
import json

import pytest

from citeproc_endnote_uv.pandoc_revision_launcher import (
    AGENT_WORKFLOW_PASSES,
    PANDOC_FROM,
    PANDOC_TO,
    ensure_inside_run_dir,
    pandoc_docx_to_markdown,
    pandoc_markdown_to_docx,
    sha256,
    validate_agent_workflow,
    write_agent_workflow_tasks,
)


def test_pandoc_docx_to_markdown_preserves_styles_and_extracts_media(tmp_path):
    source = tmp_path / "source.docx"
    markdown = tmp_path / "source.md"
    media = tmp_path / "media"

    command = pandoc_docx_to_markdown(source, markdown, media)

    assert command == [
        "pandoc",
        "-f",
        PANDOC_FROM,
        "-t",
        PANDOC_TO,
        "--wrap=none",
        f"--extract-media={media}",
        str(source),
        "-o",
        str(markdown),
    ]


def test_pandoc_markdown_to_docx_uses_saved_reference_doc(tmp_path):
    markdown = tmp_path / "revised.md"
    output = tmp_path / "output.docx"
    reference = tmp_path / "style-reference.docx"

    command = pandoc_markdown_to_docx(markdown, output, reference)

    assert command == [
        "pandoc",
        "-f",
        PANDOC_TO,
        "-t",
        "docx",
        "--wrap=none",
        f"--reference-doc={reference}",
        str(markdown),
        "-o",
        str(output),
    ]


def test_finalize_inputs_must_remain_inside_run_dir(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    inside = run_dir / "revised.md"
    outside = tmp_path / "outside.md"

    assert ensure_inside_run_dir(inside, run_dir, "revised markdown") == inside.resolve()
    with pytest.raises(SystemExit, match="must be inside the run directory"):
        ensure_inside_run_dir(outside, run_dir, "revised markdown")


def agent_manifest(tmp_path):
    revised = tmp_path / "draft.revised.md"
    revised.write_text("Revised text.\n", encoding="utf-8")
    return revised, {
        "workflow": "pandoc-word-revision",
        "source_docx": "source.docx",
        "source_sha256": "source-hash",
        "comments": {"markdown": "draft.comments.md", "json": "draft.comments.json", "count": 1},
        "citation_policy": {"metadata_overlay_ris": "citation_metadata.ris"},
        "generated_artifacts": {
            "source_markdown": "draft.source.md",
            "revised_markdown": revised.name,
            "media_dir": "media",
            "raw_docx": "draft.raw.docx",
            "final_docx": "draft.docx",
            "ris": "draft.ris",
        },
    }


def completed_agent_audit(manifest, revised):
    return {
        "workflow": "pandoc-word-revision-agent-workflow",
        "source_sha256": manifest["source_sha256"],
        "revised_markdown": manifest["generated_artifacts"]["revised_markdown"],
        "revised_markdown_sha256": sha256(revised),
        "passes": [
            {
                "name": workflow_pass["name"],
                "status": "completed",
                "report": f"agent_workflow/reports/{workflow_pass['report']}",
                "checks": {check: True for check in workflow_pass["required_checks"]},
            }
            for workflow_pass in AGENT_WORKFLOW_PASSES
        ],
        "overall": {
            "all_comments_addressed": True,
            "modified_claims_have_adjacent_citation_or_resolution": True,
            "uncommented_changes_justified": True,
            "citation_integrity_reviewed": True,
            "ready_for_finalize": True,
        },
    }


def test_agent_workflow_scaffold_creates_tasks_and_template(tmp_path):
    _revised, manifest = agent_manifest(tmp_path)

    workflow = write_agent_workflow_tasks(tmp_path, manifest)

    assert workflow["required"] is True
    assert len(workflow["task_files"]) == 4
    assert len(workflow["required_reports"]) == 4
    assert (tmp_path / workflow["audit_template"]).exists()
    first_task = (tmp_path / workflow["task_files"][0]).read_text(encoding="utf-8")
    assert "Required Checks" in first_task
    assert "draft.revised.md" in first_task


def test_agent_workflow_validation_requires_audit(tmp_path):
    revised, manifest = agent_manifest(tmp_path)
    manifest["agent_workflow"] = write_agent_workflow_tasks(tmp_path, manifest)

    with pytest.raises(SystemExit, match="Missing required agent workflow audit"):
        validate_agent_workflow(tmp_path, manifest, revised)


def test_agent_workflow_validation_accepts_complete_audit(tmp_path):
    revised, manifest = agent_manifest(tmp_path)
    manifest["agent_workflow"] = write_agent_workflow_tasks(tmp_path, manifest)
    for report in manifest["agent_workflow"]["required_reports"]:
        report_path = tmp_path / report
        report_path.write_text("completed\n", encoding="utf-8")
    audit_path = tmp_path / manifest["agent_workflow"]["audit_file"]
    audit = completed_agent_audit(manifest, revised)
    audit_path.write_text(json.dumps(audit), encoding="utf-8")

    assert validate_agent_workflow(tmp_path, manifest, revised) == audit


def test_agent_workflow_validation_hashes_revised_markdown(tmp_path):
    revised, manifest = agent_manifest(tmp_path)
    manifest["agent_workflow"] = write_agent_workflow_tasks(tmp_path, manifest)
    for report in manifest["agent_workflow"]["required_reports"]:
        (tmp_path / report).write_text("completed\n", encoding="utf-8")
    audit = completed_agent_audit(manifest, revised)
    revised.write_text("Changed after review.\n", encoding="utf-8")
    (tmp_path / manifest["agent_workflow"]["audit_file"]).write_text(json.dumps(audit), encoding="utf-8")

    with pytest.raises(SystemExit, match="hash does not match"):
        validate_agent_workflow(tmp_path, manifest, revised)
