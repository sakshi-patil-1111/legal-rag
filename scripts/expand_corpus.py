"""Expand the demo statute corpus with central acts missing from IL-PCSR.

Source: HF `geekyrakshit/indian-legal-acts` -> central_acts.parquet
(883 central acts, India Code text). Filter to a canonical ~130-act
list covering modern codes (BNS/BNSS/BSA), CPC, property, family,
consumer, finance, digital, labour, environment, health, rights,
security and IP law. Each act is split into per-section documents:

    doc_id   = ext_<slug>_<secno>
    title    = "Section <n> of <Act Short Title>"
    raw_text = section body (title line included)

Output: data/raw/extra_corpus/statutes.jsonl
Demo server merges these into the statute leg automatically.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "extra_corpus" / "statutes.jsonl"
SRC = Path("/tmp/central_acts.parquet")

# IL-PCSR already covers these comprehensively — skip to avoid dupes
SKIP = {
    "indian penal code 1860",
    "code of criminal procedure 1973",
    "indian evidence act 1872",
    "constitution of india",
    "income tax act 1961",
    "industrial disputes act 1947",
}

# Canonical target titles (normalised: lowercase, "the" dropped,
# parentheses flattened, non-alnum collapsed)
TARGETS = {
    # new criminal codes
    "bharatiya nyaya sanhita 2023",
    "bharatiya nagarik suraksha sanhita 2023",
    "bharatiya sakshya adhiniyam 2023",
    # civil procedure & courts
    "code of civil procedure 1908",
    "commercial courts act 2015",
    "gram nyayalayas act 2008",
    "family courts act 1984",
    "administrative tribunals act 1985",
    "armed forces tribunal act 2007",
    "national green tribunal act 2010",
    "contempt of courts act 1971",
    "court fees act 1870",
    "suits valuation act 1887",
    "oaths act 1969",
    "notaries act 1952",
    "judges protection act 1985",
    "judicial officers protection act 1850",
    "judges inquiry act 1968",
    "advocates act 1961",
    "delhi rent control act 1958",
    # ADR
    "arbitration and conciliation act 1996",
    "mediation act 2023",
    "legal services authorities act 1987",
    "lokpal and lokayuktas act 2013",
    # property
    "indian easements act 1882",
    "real estate regulation and development act 2016",
    "right to fair compensation and transparency in land acquisition "
    "rehabilitation and resettlement act 2013",
    "registration act 1908",
    "indian stamp act 1899",
    "prohibition of benami property transactions act 1988",
    "transfer of property act 1882",
    "limitation act 1963",
    "specific relief act 1963",
    "indian treasure trove act 1878",
    # commercial / contract / corporate
    "indian contract act 1872",
    "sale of goods act 1930",
    "indian partnership act 1932",
    "limited liability partnership act 2008",
    "companies act 2013",
    "societies registration act 1860",
    "indian trusts act 1882",
    "general clauses act 1897",
    "micro small and medium enterprises development act 2006",
    "competition act 2002",
    "consumer protection act 2019",
    "legal metrology act 2009",
    "bureau of indian standards act 2016",
    "essential commodities act 1955",
    "public examinations prevention of unfair means act 2024",
    "multi state cooperative societies act 2002",
    "multi state co operative societies act 2002",
    # insolvency & finance
    "insolvency and bankruptcy code 2016",
    "securitisation and reconstruction of financial assets and "
    "enforcement of security interest act 2002",
    "recovery of debts due to banks and financial institutions act 1993",
    "recovery of debts and bankruptcy act 1993",
    "securities and exchange board of india act 1992",
    "securities contracts regulation act 1956",
    "depositories act 1996",
    "reserve bank of india act 1934",
    "banking regulation act 1949",
    "payment and settlement systems act 2007",
    "credit information companies regulation act 2005",
    "deposit insurance and credit guarantee corporation act 1961",
    "national housing bank act 1987",
    "pension fund regulatory and development authority act 2013",
    "insurance act 1938",
    "insurance regulatory and development authority act 1999",
    "foreign exchange management act 1999",
    "prevention of money laundering act 2002",
    "banning of unregulated deposit schemes act 2019",
    "chit funds act 1982",
    "prize chits and money circulation schemes banning act 1978",
    "negotiable instruments act 1881",
    "interest act 1978",
    "usurious loans act 1918",
    "fiscal responsibility and budget management act 2003",
    "fugitive economic offenders act 2018",
    "black money undisclosed foreign income and assets and imposition "
    "of tax act 2015",
    "conservation of foreign exchange and prevention of smuggling "
    "activities act 1974",
    "central goods and services tax act 2017",
    "integrated goods and services tax act 2017",
    "customs act 1962",
    "foreign trade development and regulation act 1992",
    "foreign contribution regulation act 2010",
    # digital / telecom / media
    "information technology act 2000",
    "digital personal data protection act 2023",
    "indian telegraph act 1885",
    "indian wireless telegraphy act 1933",
    "telecom regulatory authority of india act 1997",
    "aadhaar targeted delivery of financial and other subsidies "
    "benefits and services act 2016",
    "cable television networks regulation act 1995",
    "press and registration of books act 1867",
    "cinematograph act 1952",
    "prasar bharati broadcasting corporation of india act 1990",
    "post office act 1898",
    "indian post office act 1898",
    "post office act 2023",
    "young persons harmful publications act 1956",
    "prize competitions act 1955",
    "delivery of books and newspapers public libraries act 1954",
    # family & personal law
    "hindu marriage act 1955",
    "hindu succession act 1956",
    "hindu adoptions and maintenance act 1956",
    "hindu minority and guardianship act 1956",
    "special marriage act 1954",
    "indian succession act 1925",
    "guardians and wards act 1890",
    "parsi marriage and divorce act 1936",
    "divorce act 1869",
    "indian divorce act 1869",
    "foreign marriage act 1969",
    "anand marriage act 1909",
    "muslim personal law shariat application act 1937",
    "dissolution of muslim marriages act 1939",
    "muslim women protection of rights on divorce act 1986",
    "muslim women protection of rights on marriage act 2019",
    "maintenance and welfare of parents and senior citizens act 2007",
    "prohibition of child marriage act 2006",
    "dowry prohibition act 1961",
    "commission of sati prevention act 1987",
    # women & children
    "protection of women from domestic violence act 2005",
    "sexual harassment of women at workplace prevention prohibition "
    "and redressal act 2013",
    "indecent representation of women prohibition act 1986",
    "protection of children from sexual offences act 2012",
    "juvenile justice care and protection of children act 2015",
    "immoral traffic prevention act 1956",
    "child and adolescent labour prohibition and regulation act 1986",
    "right of children to free and compulsory education act 2009",
    "commissions for protection of child rights act 2005",
    "infant milk substitutes feeding bottles and infant foods "
    "regulation of production supply and distribution act 1992",
    "equal remuneration act 1976",
    # labour
    "code on wages 2019",
    "industrial relations code 2020",
    "code on social security 2020",
    "occupational safety health and working conditions code 2020",
    "apprentices act 1961",
    "contract labour regulation and abolition act 1970",
    "maternity benefit act 1961",
    "payment of wages act 1936",
    "minimum wages act 1948",
    "payment of bonus act 1965",
    "payment of gratuity act 1972",
    "employees provident funds and miscellaneous provisions act 1952",
    "employees state insurance act 1948",
    "employees compensation act 1923",
    "trade unions act 1926",
    "industrial employment standing orders act 1946",
    "industrial employmnet standing orders act 1946",  # dataset typo
    "factories act 1948",
    "bonded labour system abolition act 1976",
    "unorganised workers social security act 2008",
    "building and other construction workers regulation of employment "
    "and conditions of service act 1996",
    "building and other construction workers welfare cess act 1996",
    "inter state migrant workmen regulation of employment and "
    "conditions of service act 1979",
    "plantations labour act 1951",
    "mines act 1952",
    "motor transport workers act 1961",
    "street vendors protection of livelihood and regulation of street "
    "vending act 2014",
    "prohibition of employment as manual scavengers and their "
    "rehabilitation act 2013",
    "public liability insurance act 1991",
    # environment & animals
    "environment protection act 1986",
    "wild life protection act 1972",
    "forest conservation act 1980",
    "indian forest act 1927",
    "air prevention and control of pollution act 1981",
    "water prevention and control of pollution act 1974",
    "biological diversity act 2002",
    "scheduled tribes and other traditional forest dwellers "
    "recognition of forest rights act 2006",
    "panchayats extension to scheduled areas act 1996",
    "provisions of panchayats extension to scheduled areas act 1996",
    "prevention of cruelty to animals act 1960",
    "mines and minerals development and regulation act 1957",
    "dam safety act 2021",
    "inter state river water disputes act 1956",
    # health & food
    "drugs and cosmetics act 1940",
    "drugs and magic remedies objectionable advertisements act 1954",
    "drugs and magic remedies objectionable advertisement act 1954",
    "medical termination of pregnancy act 1971",
    "pre conception and pre natal diagnostic techniques prohibition "
    "of sex selection act 1994",
    "mental healthcare act 2017",
    "clinical establishments registration and regulation act 2010",
    "transplantation of human organs and tissues act 1994",
    "surrogacy regulation act 2021",
    "assisted reproductive technology regulation act 2021",
    "human immunodeficiency virus and acquired immune deficiency "
    "syndrome prevention and control act 2017",
    "transgender persons protection of rights act 2019",
    "food safety and standards act 2006",
    "cigarettes and other tobacco products prohibition of "
    "advertisement and regulation of trade and commerce production "
    "supply and distribution act 2003",
    "prohibition of electronic cigarettes production manufacture "
    "import export transport sale distribution storage and "
    "advertisement act 2019",
    "national trust for welfare of persons with autism cerebral palsy "
    "mental retardation and multiple disabilities act 1999",
    "rights of persons with disabilities act 2016",
    "rehabilitation council of india act 1992",
    "national food security act 2013",
    "pharmacy act 1948",
    "dentists act 1948",
    "indian nursing council act 1947",
    "national medical commission act 2019",
    "national commission for indian system of medicine act 2020",
    "national commission for homoeopathy act 2020",
    "national nursing and midwifery commission act 2023",
    "allied and healthcare professions act 2021",
    "national commission for allied and healthcare professions act 2021",
    "homeopathy central council act 1973",
    "homoeopathy central council act 1973",
    "indian medicine central council act 1970",
    "epidemic diseases act 1897",
    "disaster management act 2005",
    # drugs
    "narcotic drugs and psychotropic substances act 1985",
    "prevention of illicit traffic in narcotic drugs and psychotropic "
    "substances act 1988",
    # rights & governance
    "right to information act 2005",
    "whistle blowers protection act 2014",
    "whistle blowers protection act 2011",
    "prevention of corruption act 1988",
    "protection of human rights act 1993",
    "scheduled castes and scheduled tribes prevention of atrocities "
    "act 1989",
    "protection of civil rights act 1955",
    "national commission for women act 1990",
    "national commission for minorities act 1992",
    "national commission for backward classes act 1993",
    "central vigilance commission act 2003",
    "official languages act 1963",
    "prevention of insults to national honour act 1971",
    "emblems and names prevention of improper use act 1950",
    "census act 1948",
    "registration of births and deaths act 1969",
    # security & investigation
    "unlawful activities prevention act 1967",
    "national security act 1980",
    "national investigation agency act 2008",
    "official secrets act 1923",
    "delhi special police establishment act 1946",
    "public gambling act 1867",
    "arms act 1959",
    "explosives act 1884",
    "explosive substances act 1908",
    "police act 1861",
    "private security agencies regulation act 2005",
    "criminal procedure identification act 2022",
    "intelligence organisations restriction of rights act 1985",
    "national security guard act 1986",
    "special protection group act 1988",
    "armed forces special powers act 1958",
        "coast guard act 1978",
    "civil defence act 1968",
    "national cadet corps act 1948",
    "probation of offenders act 1958",
    "repatriation of prisoners act 2003",
    # IP
    "copyright act 1957",
    "patents act 1970",
    "designs act 2000",
    "geographical indications of goods registration and protection "
    "act 1999",
    "protection of plant varieties and farmers rights act 2001",
    "trade marks act 1999",
    "semiconductor integrated circuits layout design act 2000",
    # transport & energy
    "railways act 1989",
    "indian railways act 1989",
    "railway claims tribunal act 1987",
    "metro railways operation and maintenance act 2002",
    "motor vehicles act 1988",
    "electricity act 2003",
    "energy conservation act 2001",
    "atomic energy act 1962",
    "aircraft act 1934",
    "airports economic regulatory authority act 2008",
    "airports economic regulatory authority of india act 2008",
    "national highways act 1956",
    "national highways authority of india act 1988",
    "carriage by air act 1972",
    "carriage by road act 2007",
    "carriage of goods by road act 2007",
    "indian carriage of goods by sea act 1925",
    "major port authorities act 2021",
    "inland vessels act 2021",
    "petroleum act 1934",
    "oilfields regulation and development act 1948",
    "petroleum and natural gas regulatory board act 2006",
    "boilers act 1923",
    # citizenship / borders / delhi
    "citizenship act 1955",
    "passports act 1967",
    "foreigners act 1946",
    "registration of foreigners act 1939",
    "extradition act 1962",
    "emigration act 1983",
    "immigration and foreigners act 2025",
    "places of worship special provisions act 1991",
    "government of national capital territory of delhi act 1991",
    "government of union territories act 1963",
    "jammu and kashmir reorganisation act 2019",
    "delhi municipal corporation act 1957",
    "new delhi municipal council act 1994",
    "cantonments act 2006",
    "wakf act 1995",
    "waqf act 1995",
    "unified waqf management empowerment efficiency and development act 1995",
    "religious endowments act 1863",
    "charitable endowments act 1890",
    "charitable and religious trusts act 1920",
    "ancient monuments and archaeological sites and remains act 1958",
    "antiquities and art treasures act 1972",
    "public records act 1993",
    # elections / education / welfare
    "representation of people act 1950",
    "representation of people act 1951",
    "delimitation act 2002",
    "university grants commission act 1956",
    "all india council for technical education act 1987",
    "national council for teacher education act 1993",
    "architects act 1972",
    "company secretaries act 1980",
    "chartered accountants act 1949",
    "mahatma gandhi national rural employment guarantee act 2005",
    "all india services act 1951",
    "seeds act 1966",
    "insecticides act 1968",
    "destructive insects and pests act 1914",
    "warehousing development and regulation act 2007",
    "special economic zones act 2005",
}

SLUG_RE = re.compile(r"[^a-z0-9]+")
PAREN_DROP = re.compile(r"\(act no[^)]*\)|\(as amended[^)]*\)", re.I)


def normalize(title: str) -> str:
    t = re.sub(r"[()]", " ", PAREN_DROP.sub(" ", title.lower()))
    t = SLUG_RE.sub(" ", t)
    t = re.sub(r"\bthe\b", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def slugify(title: str) -> str:
    return SLUG_RE.sub("_", normalize(title))[:45].strip("_")


LEGAL_WORDS = frozenset(
    "the of and to in shall act section or any be for a is that as by "
    "on act government india state person offence provided may such "
    "this every who which not with under".split())


def english_score(text: str) -> float:
    """Density of common English legal words (defeats Kruti-Dev Hindi,
    which is ASCII-garbage that passes a Devanagari-range check)."""
    if not text:
        return 0.0
    words = re.findall(r"[a-z]+", text[:4000].lower())
    if not words:
        return 0.0
    return sum(w in LEGAL_WORDS for w in words) / len(words)


def is_english(text: str) -> bool:
    return english_score(text) > 0.12


SEC_MARK = re.compile(r"(?m)^\s*\*{0,2}(\d+[A-Z]{0,4})\.\s+")
SEC_WORD = re.compile(
    r"(?m)^\s*(?:SECTION|Section)\s+(\d+[A-Z]{0,4})\s*[\.\-–—:)]?")


def split_sections(text: str, title: str, slug: str) -> list[dict]:
    """Split act text into per-section docs at body section markers.

    Tries '^N.' (markdown) then 'Section N'. TOCs list the same markers,
    so we locate the second occurrence of section 1 (body start) and
    only split on markers at/after it.
    """
    for pattern in (SEC_MARK, SEC_WORD):
        marks = list(pattern.finditer(text))
        if len(marks) >= 3:
            break
    else:
        return [{"doc_id": f"ext_{slug}_whole", "title": title,
                 "raw_text": f"{title}\n\n{text[:30000]}"}]

    body_start = 0
    ones = [m.start() for m in marks if m.group(1) == "1"]
    if len(ones) >= 2:
        body_start = ones[1]

    body = [m for m in marks if m.start() >= body_start]
    out = []
    for i, m in enumerate(body):
        sec = m.group(1)
        # '2023.' at line-start in prose is a year, not a section —
        # no Indian act exceeds ~600 sections
        if sec.isdigit() and int(sec) > 950:
            continue
        end = body[i + 1].start() if i + 1 < len(body) else len(text)
        chunk = text[m.start():end].strip()
        if len(chunk) < 80:
            continue
        first_line = chunk.split("\n", 1)[0].strip().strip("*")
        out.append({
            "doc_id": f"ext_{slug}_{sec}",
            "title": f"Section {sec} of {title}",
            "section_heading": first_line[:120],
            "raw_text": f"{title}\n\n{chunk[:24000]}",
        })
    return out


def collect(df: pd.DataFrame, title_col: str, text_col: str,
            wanted: set[str], docs: list, matched: set) -> None:
    """Match rows to wanted canonical titles; split into section docs."""
    df = df[[title_col, text_col]].copy()
    df["_norm"] = df[title_col].map(lambda t: normalize(str(t)))
    df["_escore"] = df[text_col].fillna("").map(
        lambda t: english_score(str(t)))
    df["_len"] = df[text_col].fillna("").astype(str).str.len()
    df = df[df["_norm"].isin(wanted)]
    # best version = highest english-legal density, then longest
    df = df.sort_values(["_escore", "_len"])
    df = df.drop_duplicates("_norm", keep="last")
    for norm, title, text in zip(df["_norm"], df[title_col],
                               df[text_col]):
        if not is_english(str(text)):
            continue
        t = str(title).strip().rstrip(".")
        docs.extend(split_sections(str(text), t, slugify(t)))
        matched.add(norm)
        wanted.discard(norm)


def main() -> int:
    docs, matched = [], set()

    # pass 1: clean central-acts parquet
    df1 = pd.read_parquet(SRC)
    wanted = set(TARGETS) - SKIP
    collect(df1, "Short Title", "Markdown", wanted, docs, matched)
    print(f"pass1 (india-code): +{len(matched)} acts, {len(docs):,} docs")

    # pass 2: KanoonGPT fallback for missing titles
    if wanted:
        import glob
        frames = [
            pd.read_parquet(
                f, columns=["document_title", "document_type", "text"])
            for f in sorted(glob.glob("/tmp/kgpt*.parquet"))]
        df2 = pd.concat(frames, ignore_index=True)
        df2 = df2[df2["document_type"].isin(
            ["Act", "Legislation (Act)", "Legislation", "Ordinance"])]
        collect(df2, "document_title", "text", wanted, docs, matched)
        print(f"pass2 (kanoon): total {len(matched)} acts, "
              f"{len(docs):,} docs; {len(wanted)} still missing")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    missing = sorted(set(TARGETS) - matched - SKIP)
    print(f"acts indexed: {len(matched)} | docs: {len(docs):,} -> {OUT}")
    if missing:
        print(f"still missing ({len(missing)}):",
              ", ".join(missing[:25]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
