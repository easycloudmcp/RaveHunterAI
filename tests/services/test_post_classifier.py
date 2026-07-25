import pytest

from services import InstagramPostClassifier
from services.post_classifier import PostCategory


@pytest.mark.parametrize(
    ("caption", "expected"),
    [
        (
            "Save the date: 19.07.2026. Doors 14:00 Uhr. Tickets now.",
            PostCategory.EVENT_ANNOUNCEMENT,
        ),
        (
            "Danke München. Was für eine Nacht. Wer war dabei?",
            PostCategory.EVENT_RECAP,
        ),
        (
            "Techno ist Lebenseinstellung. Mehr Bass. Weniger Hass.",
            PostCategory.MEME_OR_CULTURE,
        ),
        (
            "New release out now from our favourite DJ.",
            PostCategory.VENUE_OR_ARTIST_PROMOTION,
        ),
        (
            "Heute scheint in München endlich wieder die Sonne.",
            PostCategory.OTHER,
        ),
    ],
)
def test_classifies_caption(caption: str, expected: PostCategory) -> None:
    result = InstagramPostClassifier().classify(caption)

    assert result.category is expected
    assert 0 <= result.confidence <= 100
