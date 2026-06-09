import email
import quopri
import logging


logging.basicConfig(level=logging.INFO, format="%(message)s")


def ingest_all_mhtml(input_dir, output_dir):
    
    if not input_dir.exists():
        logging.warning(f"⚠️ Input directory not found: {input_dir}")
        return

    extract_count = 0
    failed_count = 0    
    output_dir.mkdir(parents=True, exist_ok=True)
    for mhtml_file in input_dir.glob("*.mhtml"):
        extract_count, failed_count = ingest_mhtml(extract_count, failed_count, mhtml_file, output_dir)
    
    total_count = len(list(input_dir.glob("*.mhtml")))
    logging.info(f"\n📊 Bronze Summary:\nTotal: {total_count} | Extracted: {extract_count} | Failed: {failed_count}")


def ingest_mhtml(extract_count, failed_count, mhtml_file, output_dir):
    
    with open(mhtml_file, "rb") as in_file:
        html_found = False
        msg = email.message_from_binary_file(in_file)
        for part in msg.walk():    
            if part.get_content_type() == "text/html":
                html_found = True
                raw = part.get_payload()
                if isinstance(raw, bytes):
                    html_str = raw.decode("utf-8", errors="replace")
                else:
                    html_str = quopri.decodestring(raw.encode()).decode("utf-8", errors="replace")

                output_path = output_dir / (mhtml_file.stem + ".html")
                with open(output_path, "w", encoding="utf-8") as out_file:
                    out_file.write(html_str)
                    logging.info(f"✅ Extracted: {mhtml_file.name}")
                    extract_count += 1
                    break

        if not html_found:
            logging.warning(f"⚠️ No HTML content found in: {mhtml_file.name}")
            failed_count += 1

    return extract_count, failed_count