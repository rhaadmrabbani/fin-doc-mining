<h2><code>sec_form_parser</code></h2>

<code>sec_form_parser</code> is a Python library that can be used to download and parse SEC<sup>[1]</sup> forms. As of now, <code>sec_form_parser</code> is a Python 2 library. It includes parsing for only 10-K forms as well as download-related functions, and text and I/O-related utility functions.

<sup>[1]</sup> The SEC (The US Securities and Exchange Commission) requires every publicly-traded US company to file form 10-K, an annual report to shareholders, and a host of other forms.

We are a research group based at Rensselaer Polytechnic Institute in Troy, New York. We hope the <code>sec_form_parser</code> library will greatly benefit other research groups interested in textual analysis of 10-K forms and of other SEC filings, especially those who may have faced problems in reliably extracting text and sections.

<br>

<h2>Getting Started</h2>

To get started, you may run the following files in the given order:
<ol>
<li><code>examples/download_all.py</code></li>
<li><code>run examples/parse_all.py</code></li>
</ol>

<br>

<h2>Downloading 10-K forms</h2>

The 10-K forms have to be first downloaded from SEC's site before they can be parsed.
We do not provide any content downloaded from SEC's site, but our code allows the user to easily download desired 10-K content.
SEC assigns a unique id called CIK to each company.
<code>download_all.py</code> reads in CIKs from an input file and proceeds to download 10-K forms for those CIKs.

In particular, it makes use of the following function calls:

<code>download_indexes</code>
function that downloads and saves (as csv files) all quarterly filing indexes available at SEC's online archive.

<code>combine_indexes</code>
funtion that combines downloaded indexes to one file, filtering by CIK and form-type if instructed

<code>download_10K_docs</code>
function that, given the link to the giant text file containing all documents for a given form filing instance, downloads only 10-K and EX-13x documents and returns a map from doc type to doc

<br>

<h2>Parsing</h2>

<code>parse_all.py</code> expects all downloaded 10-K forms it has to process in a single directory.
You may choose to use <code>download_all.py</code> to obtain the downloads, or you may use any existing downloaded 10-K files you have in your system.

Before initiating parsing, <code>parse_all.py</code> calls the function:

<code>extract_10K_docs</code>
function that extracts relevant document(s) (of type 10-K and EX-13x) from a multi-document 10-K form or an individual 10-K or EX-13x document.

Parsing is performed on only documents of type 10-K and EX-13x (which often contains important 10-K sections that are not in their default positions).
Currently, we only provide page-parsing for EX-13x, but no section parsing.

The parsing this library currently performs can be broken into three stages:
<ol>
<li>pre-parsing,</li>
<li>parsing pages,</li>
<li>parsing sections.</li>
</ol>

In essence, the page parser extracts pages, and the section parser extracts sections. Pre-parsing produces an easy-to-read intermediate representation of a document that the page parser can parse. The section parser takes pages extracted by the page parser, and extracts sections.

The page parser relies on page separation tags. During page and section parsing respectively, the text is split into either lines or paragraphs, and we find the segments which represent page separators (page separation tag, plus additional header and footer segments per page, including page number) or those that represent section headers.

It is extremely important not to break up tables, html lists, etc when splitting the text. Otherwise, the likelihood of encountering "fake" page separators and section headers dramatically increases.

The functions <code>pre_parse</code>, <code>parse_pages</code>, and <code>parse_sections</code> can be found in <code>lib/pre_parse.py</code>, <code>lib/parse_pages.py</code>, and <code>lib/parse_sections.py</code> respectively.

<br>

<h2>Upcoming features</h2>
<ol>
<li>Additional library for performing pre-processing of text using Python's Natural Language Toolkit (NLTK)</li>
<li>Parsing table of contents, and locating 10-K sections that are not in their default positions</li>
</ol>
