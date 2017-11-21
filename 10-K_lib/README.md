BACKGROUND

In the world of financial analytics, SEC (The US Securities and Exchange Commission) filings are receiving an increasing level of attention in recent times. Especially the 10-K form, which US public companies are required to file yearly by the SEC, is becoming a popular item for text mining research. In particular, sections 1A (risk factors) and 7 (management's discussion & analysis of financial condition & results of operations - MDA for short) of the 10K form carry risk-related and forward-looking statements that are of significant interest to reseachers.

SEC filings of US public companies can be easily accessed, by researchers, online at SEC's EDGAR archive. 10-K form submissions are almost always available in plain text or in HTML-marked up form. The filing company has to adhere to a general document structure, but it has full freedom to choose, for instance, how it wants to embellish its section ans subsection headers, which information it wants to present as a table or in an HTML list, etc, and, most importantly, what HTML markup it should use. As a result, text extraction, especially at the section or subsection level, is not trivial, and may serve as a roadblock to new researchers.

Most research work in this area follow in the footsteps of Loughran and McDonald, the preeminent pioneers at applying textual analytics to SEC filings. Their approach of text extraction [1], removing all HTML markup and all tables identified as data tables, is simple and suffices for a simple extraction of all words from a document's text. However, to reliably extract sections, numerous checks (some based on HTML markup) need to be in place to eliminate false positives for section start and end markers, and simplistic approaches tend not to work in a large percentage of cases. Also,  For extracting unnumbered subsections, HTML markup information, that widely varies firm-to-firm and year-to-year, is a necessity. For sentence extraction, intelligent paragraph separation and merging is required while removing tags.

Many research groups have to come up with their own solutions to address such problems. Good solutions should address a variety of actual cases. Also, a good solution is one where the code is viewable and can be easily customized.

This project is an open-source Python 2 library, started at Rensselaer Polytechnic Institute, Troy, NY, where we wish to keep adding a few solutions at a time to help in text extraction, preprocessing and postprocessing of SEC forms. We hope that the solutions are general in scope and can also be successfully applied to other kinds of texts.  


[1] Tim Loughran and Bill McDonald, "Textual Analysis in Accounting and Finance: A Survey", Journal of Accounting Research, June 2016.
Text extraction techniques are detailed at https://research.chicagobooth.edu/~/media/8CF9E95E14144F52B32A687C33CD1557.pdf .



THIS PROJECT

Coming soon