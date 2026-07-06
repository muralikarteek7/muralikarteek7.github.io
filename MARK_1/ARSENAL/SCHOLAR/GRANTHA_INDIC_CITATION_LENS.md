# GRANTHA — Indic-source bibliography + IAST integrity lens (a SCHOLAR weapon)
*A domain-specialized sibling of FACTHARNESS, for Sanskrit / Indic-studies / history-of-Indian-science work.
Derived from a real bib-hardening session (2026-06-24) on a Vedāṅga-jyotiṣa IJHS manuscript. Self-contained;
an agent runs it as a Verify lens + a Components-stage gate. Honesty rails inherit MARK_1/MARK_2.*

> **One line:** when a manuscript cites Sanskrit primary texts and uses IAST, GRANTHA checks two things the
> generic citation lens misses — **(1) is the transliteration correct (matches Devanāgarī, strict IAST), and
> formatted right (italic vs roman per role), and (2) is each Indic source cited via a real, preferably Indian
> critical edition, with no fabricated imprint and no vague locator.** A weapon proposes the fix; the armor
> disposes — never fabricate, flag the unverified, abstain on what you can't ground.

---

## 0. FIRES WHEN (signature)
- The deliverable cites **Sanskrit / Indic primary texts** (a Bhāskarācārya, Varāhamihira, a Śulbasūtra, a Veda,
  an Upaniṣad, a siddhānta, …) **or** uses **IAST diacritics** (ā ī ū ṛ ṝ ḷ ṅ ñ ṭ ḍ ṇ ś ṣ ṃ ḥ) anywhere.
- A `.bib`/reference list mixes Sanskrit work-names, sage-authors, and modern editors.
- ANY history-of-Indian-science / Indology / Sanskrit-philology venue (e.g. IJHS, Gaṇita Bhāratī).

If the work has no Indic content, GRANTHA does not fire — do not convene it for a non-Indic bibliography.

---

## 1. THE κ MAP — what is mechanically checkable vs a judgment
| piece | κ | checks | verifier |
|---|---|---|---|
| **G-IAST** | ~1 | each IAST string matches its Devanāgarī (correct diacritic, correct sibilant/nasal, **strict IAST: c not ch**) | map word→Devanāgarī; deterministic diacritic table |
| **G-FORMAT** | 1 | italic vs roman is correct **for the role** AND survives the `.bst` (toggle-safe) | role table §3 + the bst behaviour §4 |
| **G-TYPE** | 1 | entry type & fields are valid (no `@article` without `journal`; editor-led classical text) | BibTeX field rules §5 |
| **G-EDITION** | 0→1 | the cited edition is **real** and (preferably) an **Indian critical edition** | retrieval; cross-check the best-known Indian-astronomy/maths reference works — else **flag/abstain** |
| **G-LOCATOR** | 1 | locators are **exact** (chapter.verse / page) or **absent** — never vague prose | string check §6 |

G-IAST/G-FORMAT/G-TYPE/G-LOCATOR are exact gates. **G-EDITION is κ=0** — confirm against a source or abstain;
never assert an unverified publisher/year/series.

---

## 2. G-IAST — transliteration correctness (match the Devanāgarī)
1. **Strict IAST by default: `c`, never `ch`.** च = *c* (Bhāskarācārya, ācārya, Pañca-, Acyutānanda — NOT
   "Bhāskarāchārya"/"Achyutananda"). **Exception:** a genuine aspirate छ *is* `ch` (Chāndogya छान्दोग्य). The
   only way to be sure is to map to Devanāgarī.
2. **Verify every diacritic against the akṣara:** ṣ (ष) vs ś (श) vs s (स); ṅ (ङ) vs ñ (ñ) vs ṇ (ण) vs n (न);
   ṛ (ऋ/ृ vocalic); ṃ (anusvāra ं) vs ṅ/m; ā/ī/ū long vowels; ṭ ḍ retroflex (ट ठ ड ढ). Common real errors caught
   this way: *Chandogya→Chāndogya* (missing long ā), *Jyotisa-Vedānga→Jyotiṣa-Vedāṅga* (missing ṣ and ṅ).
3. **Keep imprints'/publishers' own romanisation as printed** (e.g. "Chaukhambha", "Braj Bhushandas") — do not
   "correct" a proper-noun trade name to IAST.
4. **Vṛddhi / variant forms are not errors** — e.g. an edition titled *Vedāṅga Jyautiṣa* (ज्यौतिष) is correct as
   the edition's own title; do not "fix" it to Jyotiṣa.

## 3. G-FORMAT — the role → format rule (the heart of the lens)
> **Italic = Sanskrit work-names + technical terms. Roman = people names, place names, and all English text.**

- **Sanskrit work-titles** (*Bījagaṇita*, *Siddhāntaśiromaṇi*, *Bṛhatsaṃhitā*, *Vāsanā*, *Śulbasūtra*) → **italic**.
- **Sanskrit technical terms** (*varṇa*, *nakṣatra*, *Golādhyāya*, *Ādityacārādhyāya*) → **italic**.
- **People** (Bhāskarācārya, Varāhamihira, the four Śulba sages, modern editors) → **roman**, even inside an
  otherwise-italic title.
- **Place names** → **roman**, and in a published imprint use the **normal English form** (Varanasi, not
  Vārāṇasī; Benares is fine for a period imprint).
- **English words / descriptive subtitles / English book titles** → normal style (do not force-italicise English).

## 4. G-FORMAT mechanics — make the format survive the `.bst` (toggle-safe)
The format intent must match what the style actually emits. For **`sn-chicago.bst`** (verified by reading it):
- **`@book` / `@incollection` booktitle** → `format.btitle` wraps the WHOLE field in `{\em …}` (auto-italic).
  ⇒ inside a book title, `\emph{...}` **toggles to UPRIGHT** (wrong). To keep a Sanskrit work italic and pull a
  person/place to roman, use **`\textup{by Bhāskarācārya}`** / `\textup{of Āryabhaṭa …}` — the work stays italic
  by default, the `\textup` part goes roman.
- **`@article` title** → `format.title` is **roman** AND applies `change.case$` (lowercases unprotected words).
  ⇒ wrap a Sanskrit work-name in **`\emph{Vedāṅga Jyotiṣa}`** — this both italicises it AND brace-protects its
  capitals from being lowercased.
- **`journal`** → emphasized (italic) automatically; do **not** add `\emph` to a Sanskrit journal name
  (*Gaṇita Bhāratī*) — it would toggle to roman.
- **`note`** → roman context; `\emph{...}` correctly italicises a Sanskrit term there.
- Always **read the actual `.bst`/`.cls`** (and check the engine: `fontspec`+`polyglossia` ⇒ XeLaTeX/LuaLaTeX,
  Unicode IAST is safe). Never assume — the toggle direction depends on the style.

## 5. G-TYPE — entry-type & structure for classical texts
- **A classical text cited via a modern edition is editor-led:** drop the ancient sage from `author`; put
  `editor = {Modern Editor}` (the bst makes the editor the in-text label, e.g. *(Bhat 1981)*), and
  `title = {Work \textup{by AncientAuthor}}`. Having BOTH `author={{Sage}}` and `editor=` makes the bst label the
  *sage* with a modern year → anachronistic *(Bhāskarācārya 1949)*; avoid.
- **`@article` requires `journal`.** A chapter in an edited volume that carries `booktitle`/`editor`/`publisher`
  is an **`@incollection`** (or `@inbook`), never `@article` — else "no journal in <key>".
- Keep citation keys (`@book{key,`) stable when only fixing fields.

## 6. G-EDITION + G-LOCATOR — sourcing honesty (κ=0 → armor)
- **Prefer Indian Sanskrit critical editions over Western translations.** For a Sanskrit verse, cite the Sanskrit
  text (e.g. *Bījagaṇita*, ed. Acyutānanda Jhā, Varanasi 1949), not only Colebrooke 1817. A Western translation is
  a fallback / supplement, not the primary.
- **Ground editions against the best-known Indian-astronomy/mathematics reference works first** — authoritative
  critical editions and the standard scholarly literature (e.g. the bibliographies in Prof. Venketeswara Pai's
  Grahagaṇita volumes, Pingree's *CESS*, INSA/IJHS/*Gaṇita Bhāratī* articles, Sen & Bag, K. V. Sarma). Prefer the
  source the operator/domain most trusts; lead with the editor as the cite pointer.
- **Never fabricate** a publisher / year / series number / edition. If unconfirmed, omit the field or mark it
  CONFIRM — never ship a plausible-looking guess as fact. (A wrong "1888 / Braj Bhushan Das" guess is exactly the
  failure mode this rail exists to stop.)
- **Never use a vague locator** ("varṇa section, opening verse", "Golādhyāya, nakṣatra longitudes"). Give an
  **exact** chapter.verse / page (e.g. "Ādityacārādhyāya 3.1–2") **or leave it out**.

---

## 7. THE GATE (non-waivable self-tests before GRANTHA signs off)
1. **G-IAST:** produce, for each flagged Sanskrit word, `word → Devanāgarī → verdict`. Catch at least the
   c/ch and ṣ/ś/ṅ/ṇ classes. Any word you cannot map → **flag, do not silently pass**.
2. **G-FORMAT:** every Sanskrit work/term italic, every person/place roman, and the chosen markup is
   **toggle-correct for the actual `.bst`** (prove you read the style).
3. **G-TYPE:** no `@article` without `journal`; classical texts editor-led.
4. **G-EDITION:** every Indic edition is real + (preferably) Indian; any unconfirmed imprint is flagged/omitted,
   **never fabricated**.
5. **G-LOCATOR:** zero vague locators.
6. **Honest tier (Mark 2):** report what is verified vs flagged; **abstain** on the unresolved; deliver as
   BEFORE/AFTER LaTeX (the operator's standing preference), keys unchanged.

**GRANTHA is a lens, not a truth oracle.** "IAST-correct + well-formed + grounded-in-Pai" ≠ "the verse says what
the prose claims" — that is FACTHARNESS's job. Run both.
