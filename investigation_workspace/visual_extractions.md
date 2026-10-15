# Visual/OCR Extractions

This file records facts extracted from image-based source documents where embedded text extraction was incomplete or absent. These entries should be treated as evidence notes, not as a substitute for the original filing.

## VE001 - QCIL Shareholding Pattern Scan

Source document: `source_pdfs/aster_qcil_qcil_shareholding_pattern.pdf`, downloaded from Aster DM Healthcare's official Aster-QCIL merger page on June 4, 2026.

Extraction method: rendered pages 1-8 using `pdftoppm` and reviewed page images; ran `tesseract` OCR on selected rendered pages. The PDF contains scanned/image table content and `pdftotext` produced no usable embedded text.

High-confidence facts:

- The document is titled "Format of disclosure of shareholding pattern of Quality Care India Limited".
- Table I summary shows promoter and promoter group: 1 shareholder, 273,663,300 fully paid equity shares, 71.84% shareholding.
- Table I summary shows public: 81 shareholders, 107,257,252 fully paid equity shares, 28.16% shareholding.
- Table I summary shows total shares: 380,920,552.
- Table II identifies the promoter/promoter-group shareholder as BCP Asia II Topco IV Pte. Ltd. with 273,663,300 shares and 71.84%.
- The declaration table marks "No" for partly paid shares, convertible securities/warrants, depositary receipts, locked-in shares, and pledged/encumbered promoter shares.

Confidence: High for the summary totals and BCP Asia II Topco IV Pte. Ltd. promoter row; lower for smaller public-shareholder names because the public table is dense and visually/OCR noisy.
