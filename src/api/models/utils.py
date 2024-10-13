from api.models import Sneaker, SneakerBase, SneakerPublic


def sneaker_to_public(sneakers: list[Sneaker]) -> list[SneakerPublic]:
    results = []
    for sneaker in sneakers:
        sneaker_public = SneakerPublic(
            id=sneaker.id,
            links=sneaker.get_links(),
            images=sneaker.get_images(),
            sizes=sneaker.get_sizes(),
        )
        for key in SneakerBase.model_fields:
            value = getattr(sneaker, key, None)
            if value:
                setattr(sneaker_public, key, value)
        results.append(sneaker_public)
    return results
