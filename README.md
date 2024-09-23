# Week 2 lab work


### Milestone 8 work

Used OpenAI GPT 3.5 Turbo and Claude 3.5 Sonnet as LLMs. Alternated between them as query LLM and LLM-as-a-judge.

Dataset consists of 267 QnA pairs off the "Codepath" document. 

With GPT3.5 as query LLM and Claude as judge:
248 answers with a zero score. 19 with a 1 score. Giving an accuracy of 7.1 percent.

With Claude as query LLM and GPT3.5 as judge: 
231 Answer with zero score. 36 with a 1 score. Giving an accuracy of 13.4 percent.


With Claude as query LLM and judge:
230 answers with zero score, 37 with a 1 score. Giving an accuracy of 13.8 percent.

With GPT3.5 as query LLM and judge:
250 answers with a zero score. 17 with a 1 score. Giving an accuracy of 6.3 percent.


### Conclusion:

Based on this limited experiment, GPT3.5 is worse off than Claude for a query LLM purpose, but quite similar to Claude for the
LLM-as-a-judge role.