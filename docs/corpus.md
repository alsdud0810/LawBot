# Official Corpus Plan

## Collected source documents

The current local corpus is downloaded from the Korean National Law Information Center (`law.go.kr`) official current-law pages and their official body endpoint. Files ending in `본문.html` are generated from the body response, not manually authored legal text.

| Document | Official source | Main use |
|---|---|---|
| 근로기준법 | https://www.law.go.kr/법령/근로기준법 | wages, dismissal, working hours, leave, workplace harassment, accident compensation |
| 근로기준법 시행령 | https://www.law.go.kr/법령/근로기준법시행령 | delegated definitions, calculation rules, implementation details |
| 산업안전보건법 | https://www.law.go.kr/법령/산업안전보건법 | workplace safety, occupational accidents, foreign-worker safety education |
| 근로자퇴직급여 보장법 | https://www.law.go.kr/법령/근로자퇴직급여보장법 | severance and retirement benefits |
| 외국인근로자의 고용 등에 관한 법률 | https://www.law.go.kr/법령/외국인근로자의고용등에관한법률 | foreign-worker employment, insurance, workplace changes, protection |

## Excluded

`최저임금법` was identified as an official source, but the fetched page currently reports a 2020-05-26 effective version. It is excluded from the current corpus until the current effective text and its annual minimum-wage notices are verified.

The supplied `이주노동자.pdf` is a 2023 planning presentation, not an official legal source, and is excluded.

## Reproducibility

The local files are ignored by Git. Recollect the current body response from the URLs above, then run:

```powershell
python scripts/ingest.py --strategy legal
python scripts/build_index.py
```

The collection date and effective date should be recorded with each evaluation run because laws change.
