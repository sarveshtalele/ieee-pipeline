.PHONY: build validate clean
build:
	bash scripts/build.sh
validate:
	python3 scripts/validate.py
clean:
	rm -rf dist paper/*.aux paper/*.bbl paper/*.blg paper/*.log paper/*.out paper/*.fdb_latexmk paper/*.fls
