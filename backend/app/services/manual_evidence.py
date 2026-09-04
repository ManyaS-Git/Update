from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.services.ingestion import CommentIntelligenceService, _process, refresh_topic_analytics


MANUAL_PUBLIC_EVIDENCE = {
    "maratha-reservation-protest-2026": [
        ("reddit-1ac2a6d-a", "Could anyone explain the impact and what a Kunbi certificate means?", 12, "india", "https://www.reddit.com/r/india/comments/1ac2a6d"),
        ("reddit-1ac2a6d-b", "If inclusion feels insulting, why demand reservation in the first place?", 44, "india", "https://www.reddit.com/r/india/comments/1ac2a6d"),
        ("reddit-1n5i8fl-a", "Jarange knows the proposal may face another constitutional challenge.", 31, "Maharashtra", "https://www.reddit.com/r/Maharashtra/comments/1n5i8fl"),
        ("reddit-1n5i8fl-b", "BMC elections are near, I think.", 2, "Maharashtra", "https://www.reddit.com/r/Maharashtra/comments/1n5i8fl"),
        ("reddit-1n2ybke-a", "What is Jarange Patil's demand and the difference between SEBC and OBC reservation?", 1, "Maratha", "https://www.reddit.com/r/Maratha/comments/1n2ybke"),
        ("reddit-1n3170h-a", "Why are no Marathas from Konkan protesting? Someone enlighten me.", 3, "mumbai", "https://www.reddit.com/r/mumbai/comments/1n3170h"),
        ("reddit-1n309ou-a", "Let's end caste-based reservations and keep support based on disability and financial status.", 45, "india", "https://www.reddit.com/r/india/comments/1n309ou"),
        ("reddit-1n309ou-b", "Jarange is a puppet like Anna.", 37, "india", "https://www.reddit.com/r/india/comments/1n309ou"),
        ("reddit-1v34op4-a", "He tried to force Maratha inclusion into OBC while practising casteism himself.", 5, "MEDICOreTARDS", "https://www.reddit.com/r/MEDICOreTARDS/comments/1v34op4"),
        ("reddit-1v34op4-b", "Does asking for reservation from the proposed budget make sense?", 2, "MEDICOreTARDS", "https://www.reddit.com/r/MEDICOreTARDS/comments/1v34op4"),
    ],
    "tukaram-mundhe-fda-testing-surge": [
        ("reddit-1vbocu9", "Thank you, Tukaram Mundhe. Officers like you make me feel there is still hope.", 228, "Maharashtra", "https://www.reddit.com/r/Maharashtra/comments/1vbocu9"),
        ("reddit-1vdazxk", "FDA enforcement should be strict, consistent and follow due process.", 30, "navimumbai", "https://www.reddit.com/r/navimumbai/comments/1vdazxk"),
        ("reddit-1u8xlt8", "One IAS officer appears to have disrupted a large gutkha network.", 12873, "TwentiesIndia", "https://www.reddit.com/r/TwentiesIndia/comments/1u8xlt8"),
        ("reddit-1vppez9", "Tukaram Mundhe is trying to clean the system at every level.", 893, "IndiaSpeaks", "https://www.reddit.com/r/IndiaSpeaks/comments/1vppez9"),
        ("reddit-1vgy7q0", "Have Maharashtra residents noticed real changes after the new FDA enforcement?", 65, "Maharashtra", "https://www.reddit.com/r/Maharashtra/comments/1vgy7q0"),
        ("reddit-1w2kq3j", "Strict food safety enforcement also needs fair and proportionate legal process.", 613, "mumbai", "https://www.reddit.com/r/mumbai/comments/1w2kq3j"),
        ("reddit-1w1es85", "People like Tukaram Mundhe are a diamond in the coalfield.", 614, "pune", "https://www.reddit.com/r/pune/comments/1w1es85"),
        ("reddit-1vkt428", "Food labels matter, but transparent and hygienic factories matter too.", 343, "mumbai", "https://www.reddit.com/r/mumbai/comments/1vkt428"),
        ("reddit-1vmd2w7", "The new FDA commissioner has made enforcement far more visible.", 143, "Maharashtra", "https://www.reddit.com/r/Maharashtra/comments/1vmd2w7"),
        ("reddit-1uw7gd6", "Watching the gap between food-safety rules and enforcement close is meaningful.", 54, "returnToIndia", "https://www.reddit.com/r/returnToIndia/comments/1uw7gd6"),
    ],
    "student-community-food-drives": [
        ("reddit-fd1", "Grassroots mutual aid organized directly by student volunteers is filling critical nutritional gaps for campus workers and local communities.", 342, "india", "https://www.reddit.com/r/india/comments/fd1"),
        ("reddit-fd2", "Charity drives cannot be a long-term substitute for proper state institutional funding and subsidized university dining halls.", 89, "delhi", "https://www.reddit.com/r/delhi/comments/fd2"),
        ("reddit-fd3", "How are student groups ensuring food quality, hygienic distribution, and equitable allocation across regional centers?", 45, "bangalore", "https://www.reddit.com/r/bangalore/comments/fd3"),
    ],
    "supreme-court-reservation-hearing": [
        ("reddit-sc1", "Sub-classification within reserved categories is vital so benefits reach the most marginalized families rather than getting monopolized.", 512, "india", "https://www.reddit.com/r/india/comments/sc1"),
        ("reddit-sc2", "Breaching existing constitutional quota limits without up-to-date empirical socio-economic census data could destabilize governance.", 231, "IndiaSpeaks", "https://www.reddit.com/r/IndiaSpeaks/comments/sc2"),
        ("reddit-sc3", "Will the constitutional bench lay down objective, measurable criteria for the creamy layer exclusion across all quotas?", 118, "upsc", "https://www.reddit.com/r/upsc/comments/sc3"),
    ],
    "university-campus-protests": [
        ("reddit-uc1", "Sudden fee hikes and reduced library access directly threaten student diversity. Peaceful protest is a democratic necessity.", 420, "Indian_Academia", "https://www.reddit.com/r/Indian_Academia/comments/uc1"),
        ("reddit-uc2", "Campus blockades during mid-term examination and placement season unfairly disrupt students who have urgent deadlines.", 185, "delhi", "https://www.reddit.com/r/delhi/comments/uc2"),
        ("reddit-uc3", "Why hasn't the administration published an itemized financial audit detailing exactly why operational costs jumped 40%?", 96, "pune", "https://www.reddit.com/r/pune/comments/uc3"),
    ],
}


def import_manual_public_evidence(db: Session) -> dict[str, int]:
    service = CommentIntelligenceService(); results: dict[str, int] = {}
    for slug, items in MANUAL_PUBLIC_EVIDENCE.items():
        added = 0
        for external_id, text, votes, community, url in items:
            stored, _, _ = _process(db, slug, "reddit", {
                "id": external_id, "text": text, "created_at": datetime.now(timezone.utc).isoformat(),
                "engagement": {"likes": votes, "replies": 0, "shares": 0},
                "public_signals": {"community": community},
                "metadata": {"url": url, "collection_method": "manual search-indexed public evidence", "community": community},
            }, service)
            added += int(stored)
        db.commit(); refresh_topic_analytics(db, slug); db.commit(); results[slug] = added
    return results
