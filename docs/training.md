# Continuous learning

UPDATES keeps three learning tracks separate so their metrics remain meaningful.

## Supervised learning

`POST /api/learning/train` evaluates word and character TF-IDF logistic-regression candidates against a majority baseline and only saves a checkpoint when macro-F1 improves by at least 0.05. Text is normalized and deduplicated before a stratified held-out split.

Current reproducible baselines:

- Sentiment: SentiHin-2500 plus the MIT-licensed `Abhishek4896/hindi-english-code-mixed-tweets-sentiment` sample. The accepted character model achieved 0.9179 held-out macro-F1 on 632 unique examples. The small Hinglish sample is highly templated, so this score must not be treated as a production estimate.
- Safety benchmark: MIT-licensed PRISM Hinglish hate-speech train/validation/test splits. The accepted word model achieved 0.7084 macro-F1 on the independent 8,852-example test split. Its binary labels are not silently mapped onto the product's distinct `normal/toxic/hate` policy.

Raw third-party datasets and trained artifacts are intentionally excluded from source control. Their source pages and licenses must be reviewed before redistribution.

## Unsupervised learning

Topic clustering uses only actual collected comments and feed titles. A run requires at least 60 unique texts and a silhouette score of at least 0.08. Failed candidates are deleted rather than shown in the product. The current local database has insufficient text, so this track is correctly waiting for data.

## Reinforcement feedback

Reviewer feedback is stored through `POST /api/learning/feedback` as a bounded reward in `[-1, 1]`. A UCB multi-armed bandit learns which reviewed action works best for each context after at least 20 feedback events. The model never generates rewards for itself.

## Human review API

- `POST /api/learning/labels` adds a reviewed sentiment, stance, safety, or language label.
- `POST /api/learning/feedback` records a reviewer reward for a decision.
- `POST /api/learning/train` runs all eligible tracks.
- `GET /api/learning/status` returns data counts, metrics, rejection reasons, and saved artifacts.

When continuous learning is enabled, the server compares dataset counts hourly and retrains only when new labels, feedback, comments, or stories exist.
