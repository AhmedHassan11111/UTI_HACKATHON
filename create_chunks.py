from pypdf import PdfReader
import re
import json

PDF_PATH = "DOCUMENTS/UTI.pdf"
OUTPUT_PATH = "recommendation_chunks.json"

reader = PdfReader(PDF_PATH)

# ============================================================
# 1) قراءة صفحات Recommendations
# ============================================================

pages = []

for page_number in range(5, 11):
    text = reader.pages[page_number - 1].extract_text() or ""
    pages.append((page_number, text))

# نضع رقم الصفحة قبل نص كل صفحة
full_text = "\n".join(
    f"[[PAGE {page_number}]]\n{text}"
    for page_number, text in pages
)

# ============================================================
# 2) تنظيف Footer
# ============================================================

full_text = re.sub(
    r"Urinary tract infection \(lower\): antimicrobial prescribing \(NG109\)",
    "",
    full_text
)

full_text = re.sub(
    r"© NICE.*?notice-of-rights\).*?\.",
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
# 3) أرقام الـRecommendations المطلوبة
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

# ============================================================
# 4) العناوين والنصوص التي ليست جزءًا من Recommendation
# ============================================================

remove_lines = {
    "Treatment for women with lower UTI who are not pregnant",
    "Treatment for pregnant women and men with lower UTI",
    "Treatment for children and young people under 16 years with lower UTI",
    "Advice for all people with lower UTI when an antibiotic prescription is given",
    "Reassessment",
    "Referral",
    "1.2 Managing asymptomatic bacteriuria",
    "1.3 Self-care",
    "1.4 Choice of antibiotic",
    "For a short explanation of why the committee made these recommendations, see the evidence and committee discussion on antibiotics.",
    "For a short explanation of why the committee made these recommendations, see the evidence and committee discussion on self-care.",
    "Full details of the evidence and the committee's discussion are in the evidence review."
}

# ============================================================
# 5) تحديد بداية كل Recommendation
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

    if recommendation_id not in expected:
        continue

    start = match.start()

    if i + 1 < len(matches):
        end = matches[i + 1].start()
    else:
        end = len(full_text)

    raw_text = full_text[start:end]

    # ========================================================
    # 6) تحديد الصفحة التي بدأت فيها الـRecommendation
    #    والصفحات التي امتدت إليها
    # ========================================================

    previous_page_markers = list(
        re.finditer(
            r"\[\[PAGE\s+(\d+)\]\]",
            full_text[:start]
        )
    )

    if previous_page_markers:
        current_page = int(previous_page_markers[-1].group(1))
    else:
        current_page = None

    page_numbers = []

    if current_page is not None:
        page_numbers.append(current_page)

    for page_match in re.finditer(
        r"\[\[PAGE\s+(\d+)\]\]",
        raw_text
    ):
        page_numbers.append(int(page_match.group(1)))

    page_numbers = sorted(set(page_numbers))

    # ========================================================
    # 7) إزالة علامات الصفحات
    # ========================================================

    text = re.sub(
        r"\[\[PAGE\s+\d+\]\]",
        "",
        raw_text
    )

    # ========================================================
    # 8) إزالة Footer المتبقي
    # ========================================================

    text = re.sub(
        r"Urinary tract infection \(lower\): antimicrobial prescribing \(NG109\)",
        "",
        text
    )

    text = re.sub(
        r"© NICE.*?notice-of-rights\).*?\.",
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
    # 9) إزالة العناوين والنصوص الانتقالية
    # ========================================================

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped in remove_lines:
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # ========================================================
    # 10) تنظيف المسافات
    # ========================================================

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    # ========================================================
    # 11) حفظ الـChunk
    # ========================================================

    chunks.append({
        "recommendation_id": recommendation_id,
        "pages": page_numbers,
        "text": text
    })

# ============================================================
# 12) حفظ JSON
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
# 13) التحقق من أرقام التوصيات
# ============================================================

actual = [
    x["recommendation_id"]
    for x in chunks
]

print("عدد التوصيات الصحيح:", actual == expected)

if actual != expected:
    print("الموجود:")
    print(actual)

# ============================================================
# 14) التحقق من Footer
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
# 15) التحقق من النصوص الفارغة
# ============================================================

empty = [
    x["recommendation_id"]
    for x in chunks
    if not x["text"].strip()
]

print("النصوص الفارغة:", len(empty))

if empty:
    print(empty)