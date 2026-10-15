# Carbon-intensity data

This directory is for **external electricity carbon-intensity data**. Keep it separate from the compiler energy-training dataset.

## Recommended source for an India-focused project

Ember publishes India monthly and yearly electricity data, including carbon intensity. Its India dataset covers 36 states/UTs, starts in 2019, and is released under CC BY 4.0. The current page is:

https://ember-energy.org/data/india-electricity-data/

Download with:

```bash
python tools/fetch_carbon_dataset.py
```

The downloader defaults to Ember's India monthly CSV and stores the raw file here:

```text
data/carbon/ember_india_monthly.csv
```

## Higher-frequency option

For hourly carbon-intensity experiments, an academic project can use Electricity Maps historical carbon-intensity data/API subject to its academic access and terms. The API exposes historical carbon intensity by zone and supports hourly granularity. See:

https://app.electricitymaps.com/docs/reference/carbon-intensity

https://help.electricitymaps.com/en/articles/13168512-academic-data-access-and-availability

## Great Britain hourly option

The official Great Britain Carbon Intensity API provides historical and forecast carbon-intensity endpoints:

https://api.carbonintensity.org.uk/

## Do not use these data to train the compiler energy model

Grid carbon intensity is a **multiplier/context variable**. Your compiler-energy model should be trained from measurements of the compiler/program workload on a specified hardware/software environment.
