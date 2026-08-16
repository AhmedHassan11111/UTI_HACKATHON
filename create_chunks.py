from pypdf import PdfReader
import re
import json

PDF_PATH = "documents/UTI.pdf"
OUTPUT_PATH = "recommendation_chunks.json"

reader = PdfReader(PDF_PATH)

# ============================================================
# 1) قراءة الصفحات التي تحتوي على Recommendations
# ============================================================

pages = []

# الصفحات 5 إلى 10 من ملف الـPDF
for page_number in range(5, 11):
    text = reader.pages[page_number - 1].extract_text() or ""
    pages.append((page_number, text))

# ============================================================
# 2) تجميع النص مع الاحتفاظ برقم الصفحة
# ============================================================

full_text = "\n".join(
    f"[[PAGE {page_number}]]\n{text}"
    for page_number, text in pages
)

# ============================================================
# 3) تنظيف الـFooter الموجود في صفحات NICE
# ============================================================

# اسم الدليل
full_text = re.sub(
    r"Urinary tract infection \(lower\): antimicrobial prescribing \(NG109\)",
    "",
    full_text
)

# Copyright / Notice of rights
full_text = re.sub(
    r"© NICE.*?notice-of-rights\).*?\.",
    "",
    full_text,
    flags=re.S
)

# Page X of 41
full_text = re.sub(
    r"Page\s+\d+\s+of\s*41",
    "",
    full_text
)

# بعض الصفحات يكون فيها:
# Page 10
# of 41
full_text = re.sub(
    r"Page\s+\d+\s*[\r\n]+\s*of\s*41",
    "",
    full_text
)

# ============================================================
# 4) استخراج أرقام التوصيات
# ============================================================

matches = list(
    re.finditer(
        r"(?m)^(\d+\.\d+\.\d+)\b",
        full_text
    )
)

chunks = []

for i, match in enumerate(matches):

    recommendation_id = match.group(1)

    start = match.start()

    if i + 1 < len(matches):
        end = matches[i + 1].start()
    else:
        end = len(full_text)

    raw_text = full_text[start:end].strip()

    # ========================================================
    # 5) تحديد الصفحات التي يحتوي عليها الـChunk
    # ========================================================

    page_numbers = sorted(set(
        int(x)
        for x in re.findall(r"\[\[PAGE\s+(\d+)\]\]", raw_text)
    ))

    # ========================================================
    # 6) إزالة علامات الصفحات من النص النهائي
    # ========================================================

    text = re.sub(
        r"\[\[PAGE\s+\d+\]\]",
        "",
        raw_text
    ).strip()

    # ========================================================
    # 7) تنظيف إضافي لأي Footer متبقٍ داخل الـChunk
    # ========================================================

    text = re.sub(
        r"Urinary tract infection \(lower\): antimicrobial prescribing \(NG109\)",
        "",
        text
    )

    text = re.sub(
        r"© NICE.*?notice-of-rights\).*?(?=Page|\Z)",
        "",
        text,
        flags=re.S
    )

    text = re.sub(
        r"Page\s+\d+\s+of\s*41",
        "",
        text
    )

    text = re.sub(
        r"Page\s+\d+\s*[\r\n]+\s*of\s*41",
        "",
        text
    )

    # ========================================================
    # 8) تنظيف المسافات الزائدة
    # ========================================================

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    # ========================================================
    # 9) إضافة الـChunk
    # ========================================================

    chunks.append({
        "recommendation_id": recommendation_id,
        "pages": page_numbers,
        "text": text
    })

# ============================================================
# 10) حفظ الملف
# ============================================================

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(
        chunks,
        f,
        ensure_ascii=False,
        indent=2
    )

print("تم إنشاء", OUTPUT_PATH)
print("عدد الـChunks:", len(chunks))

# ============================================================
# 11) التحقق من أرقام التوصيات
# ============================================================

expected = [
    "1.1.1",
    "1.1.2",
    "1.1.3",
    "1.1.4",
    "1.1.5",
    "1.1.6",
    "1.1.7",
    "1.1.8",
    "1.1.9",
    "1.1.10",
    "1.1.11",
    "1.1.12",
    "1.1.13",
    "1.1.14",
    "1.1.15",
    "1.1.16",
    "1.1.17",
    "1.2.1",
    "1.2.2",
    "1.3.1",
    "1.3.2",
    "1.3.3",
    "1.4.1"
]

actual = [
    x["recommendation_id"]
    for x in chunks
]

print("عدد التوصيات الصحيح:", actual == expected)

if actual != expected:
    print("الموجود:")
    print(actual)

# ============================================================
# 12) التحقق من وجود Footer
# ============================================================

bad = []

for x in chunks:

    if (
        "© NICE" in x["text"]
        or "notice-of-rights" in x["text"]
        or "Page " in x["text"]
        or "of 41" in x["text"]
        or "Urinary tract infection (lower): antimicrobial prescribing"
        in x["text"]
    ):
        bad.append(x["recommendation_id"])

print("Chunks تحتوي Footer:", len(bad))

if bad:
    print(bad)

# ============================================================
# 13) التحقق من النصوص الفارغة
# ============================================================

empty = [
    x["recommendation_id"]
    for x in chunks
    if not x["text"].strip()
]

print("النصوص الفارغة:", len(empty))

if empty:
    print(empty)