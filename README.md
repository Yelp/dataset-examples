[![Build Status](https://travis-ci.org/Yelp/dataset-examples.svg)](https://travis-ci.org/Yelp/dataset-examples)

Here are some infographics to represent the predictions:

<p align="center">
  <img src="https://github.com/saurabh21289/dataset-examples/blob/master/Charts/Chicken%20wings.png" width="350"/>
  <img src="https://github.com/saurabh21289/dataset-examples/blob/master/Charts/Sushi.png" width="350"/>
  <img src="https://github.com/saurabh21289/dataset-examples/blob/master/Charts/Noodles.png" width="350"/>
</p>

I am using the Yelp academic dataset with reviews. It's structure is given below

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
    'stars': (star rating, rounded to half - stars),
    'review_count': review count,
    'categories': [(localized category names)]
    'open': True / False(corresponds to closed, not business hours),
    'hours': {
        (day_of_week): {
            'open': (HH: MM),
            'close': (HH: MM)
        },
        ...
    },
    'attributes': {
        (attribute_name): (attribute_value),
        ...
    },
}
```

Fields which are of interest are business_id, name, city, stars, review_count, categories. Their dtypes are below:

```json
name             object
stars           float64
review_count      int64
full_address     object
city             object
state            object
latitude        float64
longitude       float64
categories       object
```
