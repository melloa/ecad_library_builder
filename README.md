# ECAD Library Builder

## Summary
The goal of the project is to automatically parse symbols and footprints from electronic component datasheets

## Components of the Application
- Collect datasheets that have not been processed before and send them to the parser
- Parse PDFs in an efficient way
- Find approximate location of symbol and footprint
- Parse symbol and footprint into generic format
- Create libraries on-the-fly to fit user needs (support all major ECAD software)

### MVP
 - Given link to datasheet download PDF
 - Parse into objects
 - Give semi-accurate coordinates of footprint and symbol
 - Parse symbol / footprint
 - Visualize output or support one ECAD software file format