from collectors.shotgun import ShotgunCollector


class DiscoveryEngine:

    def __init__(self):

        self.collectors = [
            ShotgunCollector(),
        ]

    def discover(self):

        events = []

        for collector in self.collectors:

            print(f"\nRunning {collector.__class__.__name__}")

            events.extend(
                collector.collect()
            )

        return events