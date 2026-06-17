# Builds two test PDFs with correct xref tables.
def build(objs):
    # objs: list of (n, body_bytes). Returns full PDF bytes.
    out = bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n")
    offsets = {}
    for n, body in objs:
        offsets[n] = len(out)
        out += f"{n} 0 obj\n".encode() + body + b"\nendobj\n"
    xref_pos = len(out)
    maxn = max(n for n,_ in objs)
    out += f"xref\n0 {maxn+1}\n".encode()
    out += b"0000000000 65535 f \n"
    for n in range(1, maxn+1):
        if n in offsets:
            out += f"{offsets[n]:010d} 00000 n \n".encode()
        else:
            out += b"0000000000 65535 f \n"
    out += f"trailer\n<< /Size {maxn+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF".encode()
    return bytes(out)

# ---- benign.pdf : one page, text, a URI link annotation ----
content = b"BT /F1 18 Tf 72 700 Td (Hello - this is a benign test document.) Tj ET"
benign = build([
 (1, b"<< /Type /Catalog /Pages 2 0 R >>"),
 (2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
 (3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R /Annots [6 0 R] >>"),
 (4, b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content), content)),
 (5, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"),
 (6, b"<< /Type /Annot /Subtype /Link /Rect [72 690 300 710] /A << /Type /Action /S /URI /URI (https://example.com/legitimate) >> >>"),
])
open("benign.pdf","wb").write(benign)

# ---- malicious.pdf : OpenAction -> JavaScript, AA, embedded .exe, Launch, off-IP URI ----
js = b"app.alert('pwned'); this.exportDataObject({cName:'evil', nLaunch:2});"
payload = b"MZ\x90\x00fake-executable-bytes"
content2 = b"BT /F1 16 Tf 72 700 Td (Invoice attached - enable content to view.) Tj ET"
mal = build([
 (1, b"<< /Type /Catalog /Pages 2 0 R /OpenAction 7 0 R /AA << /WC 7 0 R >> /Names << /EmbeddedFiles << /Names [(evil.exe) 9 0 R] >> >> >>"),
 (2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
 (3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R /Annots [6 0 R 8 0 R] >>"),
 (4, b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content2), content2)),
 (5, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"),
 (6, b"<< /Type /Annot /Subtype /Link /Rect [72 690 300 710] /A << /S /URI /URI (http://192.168.13.37/login) >> >>"),
 (7, b"<< /Type /Action /S /JavaScript /JS (%s) >>" % js),
 (8, b"<< /Type /Annot /Subtype /Link /Rect [72 660 300 680] /A << /S /Launch /F (cmd.exe) >> >>"),
 (9, b"<< /Type /Filespec /F (evil.exe) /EF << /F 10 0 R >> >>"),
 (10, b"<< /Type /EmbeddedFile /Length %d >>\nstream\n%s\nendstream" % (len(payload), payload)),
])
open("malicious.pdf","wb").write(mal)
print("wrote benign.pdf", len(benign), "bytes; malicious.pdf", len(mal), "bytes")
