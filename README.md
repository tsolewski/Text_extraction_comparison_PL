Text_extraction_comparison_PL - comparison of text extraction tools available in Python
===============================================================

Description
-----------
This review aims at measuring performance of popular Python text extraction tools that could be used in lingustic research, in particular for text corpus building or web scraping. This test focuses on sources in **Polish** since it was part of my research lab for a Polish scientific institution.  


Evaluation results & remarks
-----------
There have been two categories of webpages tested: news and forums. This is to show that some tools are focused on one-main-text webpages while others are all-purpose extractors. Use should always depend on one's needs.  
Every purpose will have their own favorites here. As for creation of text corpora one would most probably value low quantity of trash-text and therefore choose high-precision tools.

**News** (01.06.2021):
| Python Package | Precision | Recall | Accuracy | F-Score | Time* |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |
| baseline (text markup) | 0.588 | 0.753 | 0.637 | 0.660 | 1x |
| justext (tweaked) | 0.764 | 0.764 | 0.779 | 0.764 | 4.16x |
| newspaper3k | 0.767 | 0.517 | 0.700 | 0.617 | 15.73x |
| readability-lxml | 0.743 | 0.618 | 0.721 | 0.675 | 4.98x |
| trafilatura | 0.797 | 0.663 | 0.763 | 0.724 | 3.27x |
| trafilatura (+ fallbacks) | 0.795 | 0.697 | 0.774 | 0.743 | 5.59x |

**Forums** (01.06.2021):
| Python Package | Precision | Recall | Accuracy | F-Score | Time* |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |
| baseline (text markup) | 0.524 | 0.278 | 0.525 | 0.364 | 1x |
| justext (tweaked) | 0.795 | 0.392 | 0.654 | 0.525 | 8.65x |
| newspaper3k | 0.467 | 0.089 | 0.509 | 0.149 | 27.35x |
| readability-lxml | 0.577 | 0.190 | 0.537 | 0.286 | 11.60x |
| trafilatura | 0.632 | 0.304 | 0.574 | 0.410 | 12.54x |
| trafilatura (+ fallbacks) | 0.743 | 0.329 | 0.617 | 0.456 | 18.61x |

* Time - time difference versus baseline. E.g. 8.65x means a given tool was 8.65 times slower than the baseline.

The evaluation works in the following way: each tool extracts the pure texts from the .html's provided. Meanwhile, in the evaldata files there is indication for each webpage which elements (words, phrases) should be included and which are 'negatives' and shall be filtered out. Then there is a comparison carried out between the extracted text and the list of 'positives' and 'negatives'. As a result confusion matrix is built, which gives opportunity to calculate precision, recall, accuracy and f1-score printed above.  

The particular data used, i.e. websites for analysis, had been chosen by myself and it waas used within the frames provided with [adbar's research](https://github.com/adbar/trafilatura). If you want to replicate this test you should choose your own selection of webpages and indicate them in evaldata files as well as save their .html's in the *eval* directory.

Acknowledgments und use
-------

Inspiration for this evaluation came from the authors of [Trafilatura](https://github.com/adbar/trafilatura) tool that tested on mostly German sources.  
Feel free to use my part of contribution as per license.
