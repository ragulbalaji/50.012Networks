# SUTD 50.012 Networks Project Fall 2021 - Group 02 <a name="top"></a>

Netiquette - Does It Pay To Be Selfish? A Study of Congestion Control Abuse and Countermeasures

![Powered By: Look Mom, It Works!](https://img.shields.io/badge/Powered%20By-Look%20Mom%2C%20It%20Works!-brightgreen?style=for-the-badge)

## Table of Contents <a name="toc"></a>

- [Networks Netiquette Project](#top)
  - [Table of Contents](#toc)
  - [Introduction](#introduction)
  - [Repository Details](#description)
  - [Acknowledgements](#acknowledgements)
  - [Additional Relevant Resources](#resources)

## Introduction <a name="introduction"></a>

In our project, we conducted research to find the maximum threshold of selfishness in a network that benefits the adversary without causing major disruptions to other users. We explored 3 different attack methods:

1. Opening up multiple parallel TCP connections
2. Aggressively sending packets
3. Strategically abuse TCP ACK packets as a misbehaving receiver

The topic or theme of focus of our project is on netiquette, TCP congestion control, and selfish behavior via network abuse.

## Repository Details <a name="description"></a>

All of the relevant files are parked under the [`project`](./project) directory. General setup script can be found under the [`setup`](./project/setup) subfolder, while all of the experiments and results can be found under the [`experiments`](./project/experiments) subfolder. Other auxiliary files can be found under the [`assets`](./assets) folder.

## Acknowledgements <a name="acknowledgements"></a>

To cite our results, you can include the following citation in your work:

```bibtex
@misc{NetiquetteProject,
    author = {Balaji, Velusamy Sathiakumar Ragul and Han, Xing Yi and Huang, He and Qiao, Yingjie and Tiovalen, James Raphael and Zhang, Peiyuan},
    title = {Netiquette - Does It Pay To Be Selfish? A Study of Congestion Control Abuse and Countermeasures},
    year = {2021},
    publisher = {GitHub},
    journal = {GitHub repository},
    howpublished = {\url{https://github.com/ragulbalaji/50.012Networks}}
}
```

## Additional Relevant Resources <a name="resources"></a>

- [Final Presentation Video Recording](https://youtu.be/62V0TDXmmlM)
- [Project Proposal Presentation Slides](./assets/proposal_presentation.pdf)
- [Final Project Presentation Slides](./assets/final_presentation.pdf)
- [Final Project Report](./assets/final_report.pdf)
- [Proposed Final Exam Questions](./assets/final_exam_questions.pdf)
