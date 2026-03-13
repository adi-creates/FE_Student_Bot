import argparse
from pathlib import Path

from kb_engine import KnowledgeBaseBot


def main() -> None:
    parser = argparse.ArgumentParser(description="Build FAQ knowledge base from DOCX")
    parser.add_argument(
        "--docx",
        default="TCET_FE_faq.docx",
        help="Path to source DOCX file",
    )
    parser.add_argument(
        "--out",
        default="artifacts",
        help="Output directory for model and reports",
    )
    args = parser.parse_args()

    docx_path = Path(args.docx)
    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")

    bot = KnowledgeBaseBot.train_from_docx(str(docx_path))
    bot.save(args.out)

    report_path = Path(args.out) / "validation_report.json"
    print(f"Knowledge base built with {len(bot.faqs)} FAQ entries.")
    print(f"Validation report: {report_path}")


if __name__ == "__main__":
    main()
