from services import InstagramPostClassifier


TEST_CAPTIONS = [
    (
        "Event announcement",
        """
        Save the date: 19.07.2026
        Techno Open Air in München.
        Doors 14:00 Uhr.
        Tickets available now.
        """,
    ),
    (
        "Event recap",
        """
        Danke München. Was für eine Nacht.
        Zwei ausverkaufte Shows und unvergessliche Momente.
        Wer war dabei?
        """,
    ),
    (
        "Culture post",
        """
        Techno ist kein Hobby.
        Techno ist Lebenseinstellung.
        Mehr Bass. Weniger Hass.
        """,
    ),
    (
        "Artist promotion",
        """
        New release out now.
        Stream the new single from our favourite DJ.
        """,
    ),
    (
        "Other",
        """
        Heute scheint in München endlich wieder die Sonne.
        """,
    ),
]


def main() -> None:
    classifier = InstagramPostClassifier()

    for label, caption in TEST_CAPTIONS:
        result = classifier.classify(caption)

        print(f"\n{label}")
        print("-" * 40)
        print(f"Category  : {result.category}")
        print(f"Confidence: {result.confidence}%")
        print(f"Reason    : {result.reason}")


if __name__ == "__main__":
    main()