.PHONY: build validate validate-pdf clean

build:
	bash scripts/build.sh

validate:
	python3 scripts/validate.py
	python3 scripts/validate_results.py

validate-pdf:
	python3 scripts/validate_pdf.py

clean:
	rm -f paper/*.aux paper/*.bbl paper/*.blg paper/*.log paper/*.out \
	  paper/*.fdb_latexmk paper/*.fls paper/*.synctex.gz paper/*.toc \
	  paper/*.lof paper/*.lot
	rm -f dist/main.pdf dist/main-review.pdf dist/main-pdfinfo.txt dist/main-review-pdfinfo.txt
