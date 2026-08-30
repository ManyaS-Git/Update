# Platform access and inference limits

UPDATES uses only official, credentialed APIs. It does not scrape pages or claim unrestricted access.

## Collection

- **X API v2:** recent public Post search and conversation replies use `/2/tweets/search/recent`. Results are paginated with the API-provided token and remain subject to the product tier, query operators, rate limits and retention terms. Replies are found with the official `conversation_id` operator. See [recent search](https://docs.x.com/x-api/posts/search-recent-posts) and [conversation IDs](https://docs.x.com/x-api/fundamentals/conversation-id).
- **YouTube Data API v3:** topic discovery uses `search.list`; comments use `commentThreads.list`; missing replies are fetched through `comments.list`. Search and comment calls consume project quota, and comments may be disabled. See [commentThreads.list](https://developers.google.com/youtube/v3/docs/commentThreads/list) and [API quotas](https://developers.google.com/youtube/v3/getting-started#quota).
- **Reddit:** OAuth credentials alone do not imply permission. Reddit's 2026 Responsible Builder Policy requires explicit approval for API data access, and commercial use requires permission/contract terms. See [Developer Platform & Accessing Reddit Data](https://support.reddithelp.com/hc/en-us/articles/14945211791892-Developer-Platform-Accessing-Reddit-Data) and the [Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy).
- **Facebook:** unrestricted discovery is intentionally disabled. The connector accepts only post IDs the configured Page token/app is authorised to read. Public Page access can require Meta App Review and the relevant Page feature/permission.
- **Instagram:** unrestricted discovery is intentionally disabled. The connector reads comments only for authorised professional-account media IDs and requires the relevant Instagram comment-management access. See Meta's official [Instagram API collection](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api).

## Classification

- `airzipm/sentiment-analysis-muril-v2` is a three-class sentiment model for English, Hindi and Hinglish. Its model card reports 0.86 test accuracy and explicitly says it is not deployed by a shared Hugging Face Inference Provider. UPDATES therefore supports local Transformers inference or a separately provisioned dedicated endpoint, and exposes the active provider through `/api/models/status`.
- Sentiment, stance and hate/toxicity are separate outputs. A negative political opinion is not automatically hate speech.
- Heuristic mode exists only as a labelled offline fallback. It is not represented as MuRIL output.
- Model confidence is not factual certainty. Hindi/Hinglish spelling variation and domain shift can reduce accuracy.

## Audience and privacy

- Geography is populated only from explicit public location/place metadata. Free-text profile locations remain evidence, not verified residence.
- Age is never guessed from writing style. It is returned only when an approved source provides an explicit broad bracket; most platform comments will correctly show no age data.
- “Interests” are themes detected in the comment/community context, not verified personal interests.
- External author identifiers are one-way hashed before storage. The pipeline stores the minimum fields needed for analysis and should implement platform deletion/retention obligations before production rollout.
