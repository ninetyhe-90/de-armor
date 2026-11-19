#!/usr/bin/env python3
"""Offline response audit v2. Exit 0: no blockers; 1: contract blocked; 2: invalid input."""

import argparse
import json
from pathlib import Path
import re
import sys
import unicodedata

VERSION = "2.2.0"
MAX_BYTES = 1_000_000
KINDS = {"fact", "condition", "uncertainty", "boundary", "output"}
RULES = [
    ("A01", "身份替代回答", r"作为(?:一[个名位])?\s*(?:AI|人工智能|语言模型|大模型)",
     "确认身份说明是否与当前任务有关；若无关，改为具体能力边界。"),
    ("A02", "通用免责", r"仅供参考|不构成(?:任何)?(?:专业|投资|医疗|法律)?建议|风险自担",
     "检查是否属于用户要求的原文/条款；否则保留具体风险，压缩套话。"),
    ("A03", "社交填充", r"这是个(?:很|非常)?好的问题|希望(?:这些|以上|我的|这个)[^。！？\n]{0,12}对你有帮助|欢迎继续(?:提问|追问)|如果你还想了解更多[^。！？\n]{0,12}继续问",
     "若没有新增信息，删掉；不要删除真正的情绪回应。"),
    ("A04", "答案延后", r"^(?:关于(?:这个|你提到的)问题|为了给你更准确的建议|首先需要说明)",
     "核对开头是否可以直接给答案或真实阻塞原因。"),
    ("A05", "确定性过强", r"百分之百|毫无疑问|绝对不会|肯定没有问题",
     "核对证据与适用条件；有证明的确定判断不必改。"),
    ("A06", "假中立或无差别清单", r"多个维度综合考虑|多维度综合考虑|需要综合考虑|从多个(?:维度|方面)考虑|视情况而定|具体情况具体分析|各有(?:优劣|利弊)|没有一刀切|见仁见智|因(?:情况|项目|团队)而异",
     "若确实取决于条件，写明触发条件并给出首选；若信息已足够，收敛为有条件的选择。"),
    ("E01", "英文身份前置", r"\b(?:as|being)\s+an?\s+(?:ai|artificial intelligence|large language model|language model)\b",
     "英文仅基础模式覆盖：确认身份说明是否与当前任务有关；未命中不代表已审查。"),
    ("E02", "英文通用免责", r"for reference only|at your own risk|not (?:constitute|to be construed as)[^.\n]{0,40}advice|cannot provide (?:professional|legal|medical|financial) advice|please consult a (?:professional|specialist)",
     "英文仅基础模式覆盖：保留具体风险，压缩无信息免责。"),
    ("E03", "英文社交填充", r"(?:great|good) question|hope (?:this|that|it) helps|feel free to (?:ask|reach out)|let me know if you (?:have|need)",
     "英文仅基础模式覆盖：若没有新增信息，删掉；不要删除真正的情绪回应。"),
    ("E04", "英文假中立", r"it (?:really )?depends|each (?:option )?has its (?:pros and cons|trade-?offs)|there are (?:pros and cons|no one-size-fits-all)|multiple factors|case by case",
     "英文仅基础模式覆盖：是否给出有条件的选择与会使选择反转的条件。"),
    ("E05", "英文答案延后", r"^(?:that'?s a (?:great|good) question|before (?:i|we) (?:answer|dive in)|first(?:ly)?,?\s+(?:it'?s important to note|i (?:need|should|must) (?:note|mention|clarify)))",
     "英文仅基础模式覆盖：核对首句能否直接给答案或真实阻塞原因。"),
]
FIRST_SENTENCE_RULES = {"A04", "E05"}
COMPILED = [(rid, label, re.compile(pattern, re.IGNORECASE), fix) for rid, label, pattern, fix in RULES]
NUMBER = re.compile(r"[0-9]+(?:\.[0-9]+)?")
LIST_NUMBER = re.compile(r"(?m)^[ \t]{0,3}(?:[#*>-]{1,6}[ \t]*)?\(?(\d{1,3})\)?[.)、](?=[ \t]|$)")
STEP_NUMBER = re.compile(r"第[ \t]*(\d{1,3})[ \t]*[步条项点章节]")
NEAREST_THRESHOLD = 0.5
_ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\ufeff\u00a0"), None)
_ZERO_WIDTH_SPACE = {ord(c): " " for c in "\u200b\u200c\u200d\ufeff\u00a0"}
_CJK = r"\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef"
_SPACE_AROUND_CJK = re.compile(
    r"(?<=[" + _CJK + r"])[ \t]*\r?\n[ \t]*(?=[" + _CJK + r"])|[ \t]+(?=[" + _CJK + r"])|(?<=[" + _CJK + r"])[ \t]+")
_MARKUP = re.compile(r"[*_`~\"'\u2018\u2019\u201c\u201d\u300c\u300d\u300e\u300f]+")
_SENTENCE_SPLIT = re.compile(r"(?<=[。！？!?；;])|\n+")


def mask_protected(text):
    chars = list(text)

    def mask(start, end):
        for index in range(start, end):
            if chars[index] not in "\r\n":
                chars[index] = " "

    offset = 0
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence is not None:
            mask(offset, offset + len(line))
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence) and not line[marker.end():].strip():
                fence = None
        elif marker:
            fence = marker.group(1)
            mask(offset, offset + len(line))
        elif re.match(r"^ {0,3}(?:>|#{1,6}\s)", line) or line.startswith(("    ", "\t")):
            mask(offset, offset + len(line))
        offset += len(line)
    masked = "".join(chars)
    for match in re.finditer(r"(?<!`)(`+)(?!`)[\s\S]*?(?<!`)\1(?!`)", masked):
        mask(*match.span())
    return "".join(chars)


def number_scan_text(text):
    """Blank out list and step numbering so C03 does not report them as new numbers."""
    text = fold_width(text)
    chars = list(text)
    for regex in (LIST_NUMBER, STEP_NUMBER):
        for match in regex.finditer(text):
            for index in range(*match.span(1)):
                chars[index] = " "
    return "".join(chars)


def fold_width(value):
    """Length-preserving NFKC: fullwidth letters, digits and punctuation become ASCII; offsets stay valid."""
    return "".join(c if len(unicodedata.normalize("NFKC", c)) != 1 else unicodedata.normalize("NFKC", c) for c in value)


def fold_text_for_scan(value):
    """Length-preserving fold used to locate forbidden phrases: width and case only, nothing is deleted."""
    return fold_width(value).translate(_ZERO_WIDTH_SPACE).casefold()


def normalize(value):
    """Fold width, case and zero-width characters; drop Markdown emphasis, quotes, spaces next to CJK text, and a single soft line break between CJK characters (blank lines are kept).

    Sentence punctuation and spaces between ASCII tokens are kept on purpose: removing them
    would let an anchor match across sentence boundaries or turn 'v1 2' into 'v1.2'.
    """
    folded = _MARKUP.sub("", fold_width(value).translate(_ZERO_WIDTH).casefold())
    return _SPACE_AROUND_CJK.sub("", folded)


def anchor_match(text, normalized_text, alternatives):
    for value in alternatives:
        if value in text:
            return True, "literal", value
    for value in alternatives:
        folded = normalize(value)
        if folded and folded in normalized_text:
            return True, "normalized", value
    return False, "none", None


def nearest_sentence(alternatives, text):
    """Candidate sentence most similar to a missing anchor, so a reviewer can judge rewrite vs deletion."""
    best, best_sentence = 0.0, None
    for sentence in (s.strip() for s in _SENTENCE_SPLIT.split(text)):
        folded_sentence = normalize(sentence)
        if not folded_sentence:
            continue
        for value in alternatives:
            folded = normalize(value)
            grams = {folded[i:i + 2] for i in range(len(folded) - 1)}
            if not grams:
                continue
            overlap = sum(1 for gram in grams if gram in folded_sentence) / len(grams)
            if overlap > best:
                best, best_sentence = overlap, sentence
    return (best, best_sentence) if best >= NEAREST_THRESHOLD else (best, None)


EDGE_PUNCTUATION = set("\u3002\uff0c\uff1b\uff1a\uff01\uff1f\u3001.,;:!? ")
QUOTE_PAIRS = [("\u201c", "\u201d"), ("\u2018", "\u2019"), ("\u300c", "\u300d"), ("\u300e", "\u300f"), ('"', '"')]


def quoted_spans(text):
    """Character spans inside paired quotes, inline code, fenced code and block quotes."""
    spans = []
    protected = mask_protected(text)
    run = None
    for index, (original, kept) in enumerate(zip(text, protected)):
        hidden = kept == " " and original not in " \t\r\n"
        if hidden and run is None:
            run = index
        elif not hidden and run is not None:
            spans.append((run, index))
            run = None
    if run is not None:
        spans.append((run, len(text)))
    for open_q, close_q in QUOTE_PAIRS:
        body = "[^" + re.escape(close_q) + "\\n]{1,200}"
        for match in re.finditer(re.escape(open_q) + body + re.escape(close_q), text):
            spans.append(match.span())
    return spans


def normalize_with_origin(text):
    """Normalize the full text once and return (normalized, origin) where origin[i] is the source index of char i.

    Normalization is applied in the same order as normalize(): fold width/zero-width/case, strip markup,
    then drop CJK-adjacent spaces and a single soft line break. Positions are tracked through every deletion.
    """
    chars = [(c, i) for i, c in enumerate(text)]
    folded = []
    for c, i in chars:
        piece = fold_width(c).translate(_ZERO_WIDTH).casefold()
        for q in piece:
            folded.append((q, i))
    current = folded
    for regex in (_MARKUP, _SPACE_AROUND_CJK):
        string = "".join(c for c, _ in current)
        doomed = set()
        for match in regex.finditer(string):
            doomed.update(range(match.start(), match.end()))
        current = [item for idx, item in enumerate(current) if idx not in doomed]
    return "".join(c for c, _ in current), [i for _, i in current]


def normalized_occurrences_all_quoted(text, phrase, spans):
    """Third-layer check: every normalized occurrence of the phrase must lie completely inside ONE quoted span.

    An assertion that starts outside a quote and only ends inside one (root cause is "the database") is bare.
    """
    target = normalize(phrase)
    if not target:
        return False
    flat, origin = normalize_with_origin(text)
    owner_of = {}
    for number, (a, b) in enumerate(spans):
        for index in range(a, b):
            owner_of.setdefault(index, number)
    start = flat.find(target)
    while start >= 0:
        core = [k for k in range(start, start + len(target)) if flat[k] not in EDGE_PUNCTUATION]
        owners = {owner_of.get(origin[k], -1) for k in core} if core else {-1}
        if len(owners) != 1 or -1 in owners:
            return False
        start = flat.find(target, start + 1)
    return True


def all_occurrences_quoted(text, phrase, spans):
    """True when every occurrence of the phrase lies inside a quoted span."""
    start = text.find(phrase)
    while start >= 0:
        end = start + len(phrase)
        if not any(a <= start and end <= b for a, b in spans):
            return False
        start = text.find(phrase, start + 1)
    return True


def finding(text, rule, category, severity, start, end, hint):
    return {
        "rule": rule, "category": category, "severity": severity,
        "offset": start, "end": end,
        "match": "" if start is None else text[start:end],
        "snippet": "" if start is None else text[max(0, start - 12):min(len(text), end + 12)],
        "hint": hint, "fix": hint,
    }


def collect(text):
    masked = mask_protected(text)
    first = re.search(r"\S[^。！？\n]*", masked)
    hits = []
    for rule, label, regex, fix in COMPILED:
        if rule in FIRST_SENTENCE_RULES:
            if first is None:
                continue
            window, base = first.group(), first.start()
        else:
            window, base = masked, 0
        for match in regex.finditer(window):
            hits.append(finding(text, rule, label, "review", base + match.start(), base + match.end(), fix))
    return sorted(hits, key=lambda hit: hit["offset"])


def summarize(text, hits):
    return {
        "chars": len(re.sub(r"\s", "", text)),
        "counts": {kind: sum(h["severity"] == kind for h in hits) for kind in ("blocker", "review")},
        "score": None,
    }


def nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def validate_contract(contract):
    if not isinstance(contract, dict) or set(contract) != {"schema_version", "required", "forbidden"}:
        raise ValueError("contract requires exactly schema_version, required, forbidden")
    if type(contract["schema_version"]) is not int or contract["schema_version"] != 2:
        raise ValueError("contract schema_version must be 2")
    required = contract["required"]
    if not isinstance(required, list) or not 1 <= len(required) <= 100:
        raise ValueError("contract.required must contain 1..100 anchors")
    seen = set()
    for item in required:
        if not isinstance(item, dict) or set(item) != {"id", "kind", "label", "source", "any_of"}:
            raise ValueError("anchor requires id, kind, label, source, any_of")
        if not all(nonempty_string(item[key]) for key in ("id", "kind", "label", "source")):
            raise ValueError("anchor fields must be nonempty strings")
        if item["id"] in seen or item["kind"] not in KINDS:
            raise ValueError("anchor id must be unique and kind must be supported")
        seen.add(item["id"])
        alternatives = item["any_of"]
        if not isinstance(alternatives, list) or not 1 <= len(alternatives) <= 20 or not all(nonempty_string(s) for s in alternatives):
            raise ValueError("any_of requires 1..20 nonempty literal strings")
    forbidden = contract["forbidden"]
    if not isinstance(forbidden, list) or len(forbidden) > 100 or not all(nonempty_string(s) for s in forbidden):
        raise ValueError("forbidden must be a list of nonempty literal strings")
    return contract


def audit(text, baseline=None, contract=None):
    if not nonempty_string(text):
        raise ValueError("candidate must be nonempty text")
    if baseline is not None and not nonempty_string(baseline):
        raise ValueError("baseline must be nonempty text")
    if contract is not None:
        validate_contract(contract)
    hits = collect(text)
    checks = []
    normalized_text = normalize(text)
    if contract is not None:
        for item in contract["required"]:
            matched, matched_by, evidence = anchor_match(text, normalized_text, item["any_of"])
            checks.append({"id": item["id"], "kind": item["kind"], "label": item["label"],
                           "matched": matched, "matched_by": matched_by,
                           "evidence": [evidence] if matched else [], "source": item["source"]})
            if not matched:
                overlap, nearest = nearest_sentence(item["any_of"], text)
                hint = "核对是否遗漏或改写了：" + item["label"] + "。同义改写需人工核实后更新合同。"
                if nearest:
                    hint += "最接近的原句：「" + nearest[:60] + "」。若语义确实等价，把它加入 any_of；若含义相反或更弱，保持阻断。"
                hit = finding(text, "C01", "声明锚点缺失", "blocker", None, None, hint)
                hit["anchor_id"] = item["id"]
                hit["nearest"] = nearest
                hits.append(hit)
        spans = quoted_spans(text)
        folded_text = fold_text_for_scan(text)
        folded_spans = quoted_spans(folded_text) if len(folded_text) == len(text) else spans
        for phrase in contract["forbidden"]:
            # Layer 1: exact; layer 2: width/case folded (positions preserved, quote-aware);
            # layer 3: full normalization (markup, soft wraps) - no position, always a blocker.
            if text.find(phrase) >= 0:
                scan_text, scan_phrase, scan_spans, via = text, phrase, spans, ""
            elif folded_text.find(fold_text_for_scan(phrase)) >= 0:
                scan_text, scan_phrase, scan_spans = folded_text, fold_text_for_scan(phrase), folded_spans
                via = "（经全角或大小写归一化命中）"
            elif normalize(phrase) in normalized_text:
                if normalized_occurrences_all_quoted(text, phrase, spans):
                    hits.append(finding(text, "C02", "引用内出现禁用断言", "review", None, None,
                                        "归一化后，该断言只出现在引号、反引号或块引用内。确认是在纠正或转述，"
                                        "而不是借引用表达同意；若是同意，改写为明确否定。"))
                else:
                    hits.append(finding(text, "C02", "命中声明禁用断言", "blocker", None, None,
                                        "归一化后命中禁用断言（强调符号、引号、软换行或空白差异）：" + phrase + "。核对后处理。"))
                continue
            else:
                continue
            start = scan_text.find(scan_phrase)
            quoted_only = (all_occurrences_quoted(scan_text, scan_phrase, scan_spans)
                           and normalized_occurrences_all_quoted(text, phrase, spans))
            if quoted_only:
                hits.append(finding(text, "C02", "引用内出现禁用断言", "review", start, start + len(scan_phrase),
                                    "该断言只出现在引号、反引号或块引用内" + via + "。确认是在纠正或转述（如“这句话不成立”），"
                                    "而不是借引用表达同意；若是同意，改写为明确否定。"))
            else:
                hits.append(finding(text, "C02", "命中声明禁用断言", "blocker", start, start + len(scan_phrase),
                                    "核对合同禁止的断言" + via + "，不要自动删除引用中的内容。"))
    added = []
    if baseline is not None:
        sources = "" if contract is None else "\n".join(item["source"] for item in contract["required"])
        known = set(NUMBER.findall(number_scan_text(baseline) + "\n" + fold_width(sources)))
        scan_text = number_scan_text(text)
        added = sorted(set(NUMBER.findall(scan_text)) - known)
        for number in added:
            match = next(m for m in NUMBER.finditer(scan_text) if m.group() == number)
            hits.append(finding(text, "C03", "新增数字待核实", "review", match.start(), match.end(),
                                "基线和声明来源中没有该数字；确认是否是有依据的新信息或步骤编号。"))
    stats = summarize(text, hits)
    blocked = stats["counts"]["blocker"] > 0
    verdict = "BLOCKED" if blocked else ("REVIEW" if hits or contract is None else "CHECKED")
    return {
        "schema_version": 2, "engine_version": VERSION,
        "passed": not blocked, "verdict": verdict,
        "scope": "literal-contract-and-surface-review",
        "semantic_review_required": True,
        "stats": stats, "violations": hits,
        "anchors": {"total": len(checks), "matched": sum(c["matched"] for c in checks), "items": checks},
        "numbers": {"checked": baseline is not None, "added": added},
    }


def render_report(report):
    anchors = report["anchors"]
    lines = ["de-armor v%s | %s | anchors=%s/%s | blockers=%s | review=%s" % (
        VERSION, report["verdict"], anchors["matched"], anchors["total"],
        report["stats"]["counts"]["blocker"], report["stats"]["counts"]["review"])]
    for hit in report["violations"]:
        lines.append("[%s][%s] %s: %s" % (hit["rule"], hit["severity"], hit["category"], hit["hint"]))
    lines.append("Scope: literal checks only; semantic review is still required. No quality score.")
    return "\n".join(lines)


def read_text(source):
    if source == "-":
        data = sys.stdin.buffer.read(MAX_BYTES + 1)
    else:
        with Path(source).open("rb") as stream:
            data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("input exceeds 1 MB")
    return data.decode("utf-8-sig")


def main():
    parser = argparse.ArgumentParser(description="de-armor v2: offline, non-generative response audit")
    parser.add_argument("source", help="UTF-8 file path, or - for stdin")
    parser.add_argument("--baseline", help="original answer file")
    parser.add_argument("--contract", help="v2 information contract JSON file")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--min-score", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.min_score is not None:
        parser.error("v2 removes --min-score; use --contract and review verdict/violations")
    if args.baseline == "-" or args.contract == "-":
        parser.error("only source may read stdin")
    try:
        text = read_text(args.source)
        baseline = None if args.baseline is None else read_text(args.baseline)
        contract = None if args.contract is None else json.loads(read_text(args.contract))
        if args.contract is not None:
            validate_contract(contract)
        report = audit(text, baseline, contract)
    except (OSError, UnicodeError, ValueError) as exc:
        print("input error: %s" % exc, file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render_report(report))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
