from .models import Event


def assess_attack(events: list[Event]) -> dict:
    seen: set[str] = set()
    spoofed = replayed = poisoned = 0
    actual = []
    predicted = []
    for event in events:
        is_replay = event.event_id in seen
        is_spoof = not event.signature_valid
        is_poisoned = event.trust_score < .5
        seen.add(event.event_id)
        replayed += int(is_replay)
        spoofed += int(is_spoof)
        poisoned += int(is_poisoned)
        actual.append(is_spoof or is_poisoned or is_replay)
        predicted.append(is_spoof or event.trust_score < .6 or is_replay)
    tp = sum(a and p for a, p in zip(actual, predicted))
    fp = sum(not a and p for a, p in zip(actual, predicted))
    fn = sum(a and not p for a, p in zip(actual, predicted))
    return {"spoofed": spoofed, "replayed": replayed, "poisoned": poisoned,
            "precision": tp / max(1, tp + fp), "recall": tp / max(1, tp + fn)}
