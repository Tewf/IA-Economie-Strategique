# Homo silicus

Horton, Filippas and Manning (2023) argue that a language model, because of how
it is trained, is an implicit computational model of a person, and can be used
the way economists use homo economicus: give it an endowment, information and
preferences, put it in a scenario, and see what it does. They replay classic
behavioural experiments this way and get qualitatively similar results, and they
argue the disagreements are the interesting part.

This is not new reading. It is reference 5 of the internship's own bibliography,
summarised in
[`WhatCanWeLearnFromHomolicus.pdf`](../../original/Litterature/Summary/WhatCanWeLearnFromHomolicus.pdf),
and named in the report at §3.1 and in the conclusion. The internship read the
method and did not run it. That is the gap this folder is for.

## What it cannot show

Worth writing down first, because the failure mode of this method is a result
that reads as a finding about people.

- **It is not evidence about humans.** A model that reproduces an experimental
  result reproduces a pattern in its training data, which contains the write-ups
  of that experiment. Agreement is weak evidence and disagreement is more
  informative, which is Horton's own position.
- **The prompt is a treatment, not a container.** Fish, Gonczarowski and Shorrer
  (2024) found that phrasing changes in a pricing instruction moved how
  supracompetitive the prices got. Any single-prompt result is a result about
  that prompt.
- **Sampling is not a population.** Running one model five times with a
  temperature above zero gives five draws from one disposition, not five
  subjects. The panel in `models.py` exists so that variation across models can
  be reported as what it is: variation across models.
- **These are small models.** Horton used GPT-3, Bauer et al. used GPT-3.5 and
  GPT-4. The largest here is 8B and runs on an 8 GB card. Where results differ
  from the papers, model scale is a live explanation and cannot be ruled out
  from inside this repository.

## Why it is worth doing anyway

The internship's question is whether AI agents sustain cooperation. Bauer et al.
answered it for GPT-3.5 and GPT-4 through an API, in 2023. Whether it holds for
open-weight models small enough to run on a laptop is a different question, it
is not answered in the literature the internship reviewed, and it can be answered
here for free and offline.

Calvano, Calzolari, Denicolò and Pastorello (2020) is the baseline the answer has
to be read against: Q-learning agents in repeated price competition learn
supracompetitive prices with no communication at all. If a language model
cooperates, the question is whether it does so for a reason a Q-learner does not
have, and that is what the reasoning captured in `transcript` is for.

## References

- Horton, J. J., Filippas, A. and Manning, B. S. (2023). *Large Language Models
  as Simulated Economic Agents: What Can We Learn from Homo Silicus?* NBER
  Working Paper 31122. <https://arxiv.org/abs/2301.07543>
- Fish, S., Gonczarowski, Y. A. and Shorrer, R. I. (2024). *Algorithmic Collusion
  by Large Language Models.* <https://arxiv.org/abs/2404.00806>
- Calvano, E., Calzolari, G., Denicolò, V. and Pastorello, S. (2020). *Artificial
  Intelligence, Algorithmic Pricing, and Collusion.* American Economic Review
  110(10), 3267-97.

The first is the internship's own. The other two are later reading.
