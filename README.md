[![Build Status](https://travis-ci.org/Yelp/dataset-examples.svg)](https://travis-ci.org/Yelp/dataset-examples)

=============================================================
I'm using the business dataset. It's structure is given below
=============================================================
```json
{
    'type': 'business',
    'business_id': (encrypted business id),
    'name': (business name),
    'neighborhoods': [(hood names)],
    'full_address': (localized address),
    'city': (city),
    'state': (state),
    'latitude': latitude,
    'longitude': longitude,
    'stars': (star rating, rounded to half-stars),
    'review_count': review count,
    'categories': [(localized category names)]
    'open': True / False (corresponds to closed, not business hours),
    'hours': {
        (day_of_week): {
            'open': (HH:MM),
            'close': (HH:MM)
        },
        ...
    },
    'attributes': {
        (attribute_name): (attribute_value),
        ...
    },
}```

Fields which are of interest are: `business_id, name, city, stars, review_count, categories`
