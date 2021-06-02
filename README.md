Text_extraction_comparison_PL - comparison of text extraction tools available in Python
===============================================================

Description
-----------
This review aims at measuring performance of popular Python text extraction tools that could be used in lingustic research, in particular for text corpus building or web scraping. This test focuses on sources in **Polish** since it was part of my research lab for a Polish scientific institution.  


Evaluation results
-----------
There have been two categories of webpages tested: news and forums.  

**News** (01.06.2021):
| Python Package | Precision | Recall | Accuracy | F-Score | Diff. |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |
| baseline (text markup) | 0.588 | 0.753 | 0.637 | 0.660 | 1x |
| justext (tweaked) | 0.764 | 0.764 | 0.779 | 0.764 | 4.16x |
| newspaper3k | 0.767 | 0.517 | 0.700 | 0.617 | 15.73x |
| readability-lxml | 0.743 | 0.618 | 0.721 | 0.675 | 4.98x |
| trafilatura | 0.797 | 0.663 | 0.763 | 0.724 | 3.27x |
| trafilatura (+ fallbacks) | 0.795 | 0.697 | 0.774 | 0.743 | 5.59x |

**Forums** (01.06.2021):
| Python Package | Precision | Recall | Accuracy | F-Score | Diff. |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |
| baseline (text markup) | 0.524 | 0.278 | 0.525 | 0.364 | 1x |
| justext (tweaked) | 0.795 | 0.392 | 0.654 | 0.525 | 8.65x |
| newspaper3k | 0.467 | 0.089 | 0.509 | 0.149 | 27.35x |
| readability-lxml | 0.577 | 0.190 | 0.537 | 0.286 | 11.60x |
| trafilatura | 0.632 | 0.304 | 0.574 | 0.410 | 12.54x |
| trafilatura (+ fallbacks) | 0.743 | 0.329 | 0.617 | 0.456 | 18.61x |

Every purpose will have their own favorites here. As for creation of text corpora one would most probably value low quantity of trash-text and therefore choose high-precision tools.

Acknowledgments und use
-------

Inspiration for this evaluation came from the authors of [Trafilatura](https://github.com/adbar/trafilatura) tool that tested on mostly German sources.  
Feel free to use my part of contribution as per license.
