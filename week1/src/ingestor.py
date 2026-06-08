import email
from email.policy import default

def ingest_all_mhtml(input_dir, output_dir):
    if not input_dir.exists():
        print(f"⚠️ Input directory not found: {input_dir}")
        return
    extract_count = 0
    failed_count = 0
    output_dir.mkdir(parents=True, exist_ok=True)
    for mhtml_file in input_dir.glob("*.mhtml"):
        with open(mhtml_file, "rb") as in_file:
            html_found = False
            msg = email.message_from_binary_file(in_file, policy=default)
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_found = True
                    try:
                        html_str = part.get_content()
                    except Exception as e:
                        print(f"⚠️ Failed to decode: {mhtml_file.name} — {e}")
                        failed_count += 1
                        break
                    output_path = output_dir / (mhtml_file.stem + ".html")
                    with open(output_path, "w", encoding="utf-8") as out_file:
                        out_file.write(html_str)
                        print(f"✅ Extracted: {mhtml_file.name}")
                        extract_count += 1
                        break
            if not html_found:
                print(f"⚠️ No HTML content found in: {mhtml_file.name}")
                failed_count += 1
    total_count = len(list(input_dir.glob("*.mhtml")))
    print(f"\n📊 Bronze Summary:\nTotal: {total_count} | Extracted: {extract_count} | Failed: {failed_count}")