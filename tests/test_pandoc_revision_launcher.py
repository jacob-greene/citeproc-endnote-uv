from pathlib import Path

import pytest

from citeproc_endnote_uv.pandoc_revision_launcher import (
    PANDOC_FROM,
    PANDOC_TO,
    ensure_inside_run_dir,
    pandoc_docx_to_markdown,
    pandoc_markdown_to_docx,
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
