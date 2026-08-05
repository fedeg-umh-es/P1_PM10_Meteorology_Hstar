# Remaining Issues and Post-Audit Recommendations

The following are non-blocking operational steps for the author to perform prior to final upload on the journal's editorial portal:

## 1. Local PDF Compilation & Review
- Overleaf uses `pdfLaTeX` as the default compiler.
- Compile `manuscript_ijer_package.zip` on Overleaf and confirm that:
  - Table references render cleanly without `??` markers.
  - Figure references render cleanly.
  - The bibliography from `references.bib` compiles completely and citations are active.

## 2. Cover Letter PDF Conversion
- Compile `manuscripts/cover_letter.tex` using any standard LaTeX editor (e.g., pdfLaTeX) to generate a professional PDF.
- Review the generated PDF to ensure contact info and date are accurate.
- Upload this PDF to the editorial system as the **Cover Letter** submission item.

## 3. Supplementary Information File
- The manuscript has an exhaustive DM-HLN table in `tables/ijer/table_s1_dm_all_tests.tex`.
- If the journal requires a separate Supplementary Information file, place Table S1 (and optionally the absolute error metrics table) into a separate simple document using the same document class wrapper.

## 4. Final Submission Checklist
- Ensure you upload the `manuscript_ijer_package.zip` as the **Manuscript Source Files**.
- Do not include internal diagnostic scripts, python code, or intermediate CSV files in the zip.
