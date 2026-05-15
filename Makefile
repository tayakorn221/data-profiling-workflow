# Pipeline runner — สำหรับ macOS / Linux / Windows (Git Bash)
# Windows ที่ไม่มี make ใช้ make.ps1 แทน

PY ?= python
INPUT ?= data/student_fixed_report.xlsx
OUTDIR ?= outputs
K ?= 5

SCHEMA  := $(OUTDIR)/schema_summary.json
PROFILE := $(OUTDIR)/profile_stats.json
PII     := $(OUTDIR)/pii_scan_report.txt
SCORE   := $(OUTDIR)/data_quality_scorecard.html

.PHONY: all help schema scan profile scorecard verify-pii clean install check-help

help:
	@echo ""
	@echo "Data Profiling Workflow — Pipeline targets"
	@echo "==========================================="
	@echo "  make install      ติดตั้ง dependencies"
	@echo "  make all          รัน pipeline ทั้งสาย (schema -> scan -> profile -> scorecard)"
	@echo "  make schema       สร้าง schema summary"
	@echo "  make scan         PII scan (strict mode)"
	@echo "  make profile      สร้าง profile statistics"
	@echo "  make scorecard    สร้าง scorecard HTML"
	@echo "  make verify-pii   รัน PII scan แบบ strict (fail ถ้าพบ)"
	@echo "  make check-help   ทดสอบ --help ของทุก script"
	@echo "  make clean        ลบ outputs/"
	@echo ""
	@echo "Variables (override ได้):"
	@echo "  INPUT=$(INPUT)"
	@echo "  OUTDIR=$(OUTDIR)"
	@echo "  K=$(K)  (k-anonymity threshold)"
	@echo ""

install:
	$(PY) -m pip install -r requirements.txt

$(SCHEMA): $(INPUT)
	$(PY) scripts/01_extract_schema.py --input $(INPUT) --output $(SCHEMA) -k $(K)

$(PII): $(SCHEMA)
	$(PY) scripts/02_scan_pii.py --input $(SCHEMA) --report $(PII) --strict

$(PROFILE): $(INPUT)
	$(PY) scripts/03_profile_stats.py --input $(INPUT) --output $(PROFILE) -k $(K)

$(SCORE): $(SCHEMA) $(PROFILE)
	$(PY) scripts/04_build_scorecard.py --schema $(SCHEMA) --profile $(PROFILE) --output $(SCORE)

schema:    $(SCHEMA)
scan:      $(PII)
profile:   $(PROFILE)
scorecard: $(SCORE)

all: $(SCHEMA) $(PII) $(PROFILE) $(SCORE)
	@echo ""
	@echo "✅ Pipeline เสร็จ — outputs อยู่ที่ $(OUTDIR)/"

verify-pii: $(PII)
	@echo "✅ PII scan ผ่าน (strict mode)"

check-help:
	@for s in scripts/01_extract_schema.py scripts/02_scan_pii.py scripts/03_profile_stats.py scripts/04_build_scorecard.py .github/scripts/scan_committed_files.py; do \
		echo "--- $$s --- "; \
		$(PY) "$$s" --help > /dev/null 2>&1 && echo "OK" || echo "FAIL"; \
	done

clean:
	rm -rf $(OUTDIR)/*.json $(OUTDIR)/*.html $(OUTDIR)/*.txt
	@echo "Cleaned $(OUTDIR)/"
