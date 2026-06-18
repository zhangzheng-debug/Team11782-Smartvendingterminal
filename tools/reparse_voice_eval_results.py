# -*- coding: utf-8 -*-
"""Re-parse voice_eval_results.csv with V2.5.4 rules without re-running RKNN Whisper."""
import argparse, csv
from collections import Counter, defaultdict
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import parse_speech_intent

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--out', default='voice_eval_reparse_report.md')
    args = ap.parse_args()
    rows = list(csv.DictReader(open(args.csv, encoding='utf-8-sig')))
    total = ok = 0
    by = defaultdict(lambda: [0, 0])
    conf = Counter()
    failures = []
    for r in rows:
        total += 1
        exp = r.get('expected_intent', '')
        text = r.get('asr_text', '') or ''
        parsed = parse_speech_intent(text)
        pred = parsed['intent']
        good = pred == exp
        ok += int(good)
        by[exp][1] += 1
        by[exp][0] += int(good)
        conf[(exp, pred)] += 1
        if not good:
            failures.append((r.get('file', ''), exp, text, parsed.get('normalized', ''), pred, parsed.get('reason', '')))
    lines = ['# V2.5.4 Reparse Report', '', f'- Total: {ok}/{total} = {ok/total if total else 0:.3f}', '']
    lines += ['## Accuracy by command', '', '| expected_intent | correct | total | accuracy |', '|---|---:|---:|---:|']
    for k in sorted(by):
        c, t = by[k]
        lines.append(f'| {k} | {c} | {t} | {c/t if t else 0:.3f} |')
    lines += ['', '## Confusion', '', '| expected | predicted | count |', '|---|---|---:|']
    for (e, p), n in sorted(conf.items()):
        lines.append(f'| {e} | {p} | {n} |')
    lines += ['', '## Remaining failures', '', '| file | expected | asr_text | normalized | predicted | reason |', '|---|---|---|---|---|---|']
    for f, e, t, norm, p, reason in failures:
        lines.append(f'| {Path(f).name} | {e} | {t} | {norm} | {p} | {reason} |')
    Path(args.out).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines[:20]))
    print('wrote', args.out)
if __name__ == '__main__':
    main()
