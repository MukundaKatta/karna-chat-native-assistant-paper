from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "paper.md"
OUTPUT = ROOT / "karna-chat-native-assistant-architecture-preprint.pdf"


def inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text


def render() -> None:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="PaperTitle", parent=styles["Title"], fontSize=18, leading=22, spaceAfter=10))
    styles.add(ParagraphStyle(name="Author", parent=styles["Normal"], alignment=1, fontSize=10, leading=13, spaceAfter=16))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontSize=13, leading=16, spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], fontSize=10, leading=14, spaceAfter=7))
    styles.add(ParagraphStyle(name="PaperBullet", parent=styles["BodyText"], fontSize=10, leading=14, leftIndent=14))

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Karna: A Chat-Native, Multi-Channel Architecture for Personal AI Chief-of-Staff Agents",
        author="Mukunda Rao Katta",
    )

    story = []
    pending_bullets: list[str] = []
    first_heading = True

    def flush_bullets() -> None:
        nonlocal pending_bullets
        if pending_bullets:
            story.append(
                ListFlowable(
                    [ListItem(Paragraph(inline(item), styles["PaperBullet"])) for item in pending_bullets],
                    bulletType="bullet",
                    start="circle",
                    leftIndent=18,
                )
            )
            story.append(Spacer(1, 4))
            pending_bullets = []

    for raw in SOURCE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            flush_bullets()
            continue
        if line.startswith("# "):
            flush_bullets()
            story.append(Paragraph(inline(line[2:]), styles["PaperTitle"]))
            continue
        if first_heading and line == "Mukunda Rao Katta":
            story.append(Paragraph("Mukunda Rao Katta<br/>Independent Researcher", styles["Author"]))
            first_heading = False
            continue
        if line.startswith("## "):
            flush_bullets()
            story.append(Paragraph(inline(line[3:]), styles["Section"]))
            continue
        if line.startswith("- "):
            pending_bullets.append(line[2:])
            continue
        if re.match(r"^\d+\. ", line):
            pending_bullets.append(re.sub(r"^\d+\. ", "", line))
            continue
        flush_bullets()
        story.append(Paragraph(inline(line), styles["Body"]))

    flush_bullets()
    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    render()
