"""
PROJECT NEXUS — Document Export Tool (.docx)
Exports Final Reports into Styled Word Documents (.docx)
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import os
import io
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from config import REPORTS_DIR, SYSTEM_ATTRIBUTION, PROJECT_NAME


def export_to_docx(
    title: str,
    executive_summary: str,
    sections: list[Any],
    conclusion: str = "",
    filename: str | None = None,
) -> str:
    """
    Exports a structured research report into a .docx document.
    Attempts python-docx if installed; otherwise generates valid OpenXML docx.
    """
    if not filename:
        clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).rstrip()
        clean_title = clean_title.replace(" ", "_")[:40]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{clean_title}_{timestamp}.docx"

    file_path = Path(REPORTS_DIR) / filename

    try:
        import docx
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = Document()

        # Document Header
        header = doc.sections[0].header
        hp = header.paragraphs[0]
        hp.text = f"{PROJECT_NAME} — Autonomous Multi-Agent Intelligence System"
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # Document Footer
        footer = doc.sections[0].footer
        fp = footer.paragraphs[0]
        fp.text = SYSTEM_ATTRIBUTION
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Title
        p_title = doc.add_paragraph()
        run_title = p_title.add_run(title)
        run_title.font.size = Pt(24)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(15, 23, 42)
        p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # Metadata subtitle
        p_sub = doc.add_paragraph()
        r_sub = p_sub.add_run(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')} | {SYSTEM_ATTRIBUTION}")
        r_sub.font.italic = True
        r_sub.font.size = Pt(9.5)
        r_sub.font.color.rgb = RGBColor(100, 116, 139)

        doc.add_paragraph("─" * 45)

        # Executive Summary
        h_exec = doc.add_heading("Executive Summary", level=1)
        p_exec = doc.add_paragraph(executive_summary)
        p_exec.style.font.size = Pt(11)

        # Sections
        for sec in sections:
            sec_title = sec.title if hasattr(sec, "title") else sec.get("title", "Section")
            sec_content = sec.content if hasattr(sec, "content") else sec.get("content", "")
            
            doc.add_heading(sec_title, level=2)
            doc.add_paragraph(sec_content)

        # Conclusion
        if conclusion:
            doc.add_heading("Conclusion & Strategic Outlook", level=1)
            doc.add_paragraph(conclusion)

        # Attribution box
        doc.add_paragraph()
        p_box = doc.add_paragraph()
        r_box = p_box.add_run(f"Project Nexus Verification Completed • {SYSTEM_ATTRIBUTION}")
        r_box.font.bold = True
        r_box.font.size = Pt(9)
        r_box.font.color.rgb = RGBColor(79, 70, 229)

        doc.save(str(file_path))
        return str(file_path)

    except Exception:
        # Pure Python OpenXML fallback package
        return _export_openxml_fallback(title, executive_summary, sections, conclusion, file_path)


def _export_openxml_fallback(
    title: str,
    executive_summary: str,
    sections: list[Any],
    conclusion: str,
    file_path: Path,
) -> str:
    """Creates a basic standard .docx (ZIP/OpenXML) directly without external dependencies."""
    body_xml = [
        f'<w:p><w:pPr><w:jc w:val="left"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="48"/><w:color w:val="0F172A"/></w:rPr><w:t>{_escape(title)}</w:t></w:r></w:p>',
        f'<w:p><w:r><w:rPr><w:i/><w:sz w:val="18"/><w:color w:val="64748B"/></w:rPr><w:t>{_escape(SYSTEM_ATTRIBUTION)} - {datetime.now().strftime("%Y-%m-%d %H:%M")}</w:t></w:r></w:p>',
        f'<w:p><w:r><w:rPr><w:b/><w:sz w:val="32"/><w:color w:val="1E293B"/></w:rPr><w:t>Executive Summary</w:t></w:r></w:p>',
        f'<w:p><w:r><w:sz w:val="22"/><w:t>{_escape(executive_summary)}</w:t></w:r></w:p>',
    ]

    for sec in sections:
        sec_title = sec.title if hasattr(sec, "title") else sec.get("title", "Section")
        sec_content = sec.content if hasattr(sec, "content") else sec.get("content", "")
        body_xml.append(f'<w:p><w:r><w:rPr><w:b/><w:sz w:val="28"/><w:color w:val="334155"/></w:rPr><w:t>{_escape(sec_title)}</w:t></w:r></w:p>')
        body_xml.append(f'<w:p><w:r><w:sz w:val="22"/><w:t>{_escape(sec_content)}</w:t></w:r></w:p>')

    if conclusion:
        body_xml.append(f'<w:p><w:r><w:rPr><w:b/><w:sz w:val="32"/><w:color w:val="1E293B"/></w:rPr><w:t>Conclusion</w:t></w:r></w:p>')
        body_xml.append(f'<w:p><w:r><w:sz w:val="22"/><w:t>{_escape(conclusion)}</w:t></w:r></w:p>')

    body_xml.append(f'<w:p><w:r><w:rPr><w:i/><w:sz w:val="18"/><w:color w:val="4F46E5"/></w:rPr><w:t>{_escape(SYSTEM_ATTRIBUTION)}</w:t></w:r></w:p>')

    doc_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {''.join(body_xml)}
  </w:body>
</w:document>'''

    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''

    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

    with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", doc_xml)

    return str(file_path)


def _escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
