from pypdf import PdfReader
import re
import json

PDF_PATH = "documents/UTI.pdf"
OUTPUT_PATH = "table_chunks.json"

reader = PdfReader(PDF_PATH)

# ============================================================
# 1) قراءة الصفحات التي تحتوي على جداول المضادات الحيوية
# ============================================================

pages = []

# الصفحات 10 إلى 16 من ملف الـPDF
for page_number in range(10, 17):
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
# 3) تنظيف الـFooter
# ============================================================

full_text = re.sub(
    r"Urinary tract infection \(lower\): antimicrobial prescribing \(NG109\)",
    "",
    full_text
)

full_text = re.sub(
    r"© NICE.*?notice-of-rights\).*?(?=Page|\Z)",
    "",
    full_text,
    flags=re.S
)

full_text = re.sub(
    r"Page\s+\d+\s+of\s*41",
    "",
    full_text
)

full_text = re.sub(
    r"Page\s+\d+\s*[\r\n]+\s*of\s*41",
    "",
    full_text
)

# ============================================================
# 4) تحديد بداية كل جدول
# ============================================================

table_patterns = [
    (
        "TABLE_1",
        r"Table 1 Antibiotics for non-pregnant women aged 16 years and over"
    ),
    (
        "TABLE_2",
        r"Table 2 Antibiotics for pregnant women aged 12 years and over"
    ),
    (
        "TABLE_3",
        r"Table 3 Antibiotics for men aged 16 years and over"
    ),
    (
        "TABLE_4",
        r"Table 4 Antibiotics for children and young people under 16 years"
    )
]

matches = []

for table_id, pattern in table_patterns:
    match = re.search(pattern, full_text)

    if match:
        matches.append({
            "table_id": table_id,
            "start": match.start(),
            "title": match.group(0)
        })
    else:
        print("تحذير: لم يتم العثور على", table_id)

# ترتيب الجداول حسب مكانها في النص
matches.sort(key=lambda x: x["start"])

# ============================================================
# 5) استخراج كل جدول حتى بداية الجدول التالي
# ============================================================

tables = []

for i, item in enumerate(matches):

    start = item["start"]

    if i + 1 < len(matches):
        end = matches[i + 1]["start"]
    else:
        end = len(full_text)

    raw_text = full_text[start:end].strip()

    # ========================================================
    # تحديد الصفحات التي ظهر فيها الجدول
    # ========================================================

    page_numbers = sorted(set(
        int(x)
        for x in re.findall(
            r"\[\[PAGE\s+(\d+)\]\]",
            raw_text
        )
    ))

    # ========================================================
    # إزالة علامات الصفحات
    # ========================================================

    text = re.sub(
        r"\[\[PAGE\s+\d+\]\]",
        "",
        raw_text
    ).strip()

    # ========================================================
    # تنظيف إضافي
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

    text = re.sub(r"\n{3,}", "\n\n", text)

    text = text.strip()

    tables.append({
        "table_id": item["table_id"],
        "title": item["title"],
        "pages": page_numbers,
        "text": text
    })

# ============================================================
# 6) حفظ الملف
# ============================================================

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(
        tables,
        f,
        ensure_ascii=False,
        indent=2
    )

print("تم إنشاء", OUTPUT_PATH)
print("عدد الجداول:", len(tables))

# ============================================================
# 7) التحقق
# ============================================================

expected_tables = [
    "TABLE_1",
    "TABLE_2",
    "TABLE_3",
    "TABLE_4"
]

actual_tables = [
    x["table_id"]
    for x in tables
]

print(
    "الجداول الأربعة موجودة:",
    actual_tables == expected_tables
)

# ============================================================
# 8) فحص الـFooter
# ============================================================

bad = []

for x in tables:

    if (
        "© NICE" in x["text"]
        or "notice-of-rights" in x["text"]
        or "Urinary tract infection (lower): antimicrobial prescribing"
        in x["text"]
        or re.search(r"Page\s+\d+", x["text"])
    ):
        bad.append(x["table_id"])

print("الجداول التي تحتوي Footer:", len(bad))

if bad:
    print(bad)

# ============================================================
# 9) فحص النصوص الفارغة
# ============================================================

empty = [
    x["table_id"]
    for x in tables
    if not x["text"].strip()
]

print("الجداول الفارغة:", len(empty))

if empty:
    print(empty)