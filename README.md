# USA Dashboard

We're building a dashboard of key metrics for the USA because: *If you can't measure it, you can't manage it*.  When complete, you'll be able to see how well the country is doing along a number of metrics at a glance.  We strive to paint an objective, centralized picture of what's currently going on, with very timely updates.  We hope that by making this information easily visible and available that we can come to a collective understanding about whether the country is thriving or not.

**The problem that this solves** Often only pay attention to data when someone decides to perform an analysis and share it with us.  If we automated key analyses and pay attention on a regular basis, we'll all be more familiar with the health of the country and know what to prioritize.  We'll also be able to hold politicians accountable for their actions if we see the metrics change abruptly.

**Doesn't the government already do this?**  Yes the government does original data collection and produces regular reports.  We want to centralize this information and make it easier to digest for citizens.  For instance, crime data is available from each city, but only the FBI periodically merges it all and produces a *yearly* report.  We can do better than this in 2017.

## Metrics

A metric is a measurement that is made on a regular basis so that we compare it over time.  We want to measure key indicators that span a number of aspects of the USA:

- [crime and violence](https://github.com/Data4Democracy/usa-dashboard/milestone/1)
- [housing/rent prices](https://github.com/Data4Democracy/usa-dashboard/issues/22)
- [environment and climate change](https://github.com/Data4Democracy/usa-dashboard/issues/23)
- [jobs/employment](https://github.com/Data4Democracy/usa-dashboard/issues/21)
- [poverty/welfare/homelessness](https://github.com/Data4Democracy/usa-dashboard/issues/24)
- [civil rights](https://github.com/Data4Democracy/usa-dashboard/issues/25)
- [public health/healthcare](https://github.com/Data4Democracy/usa-dashboard/issues/26)
- [education](https://github.com/Data4Democracy/usa-dashboard/issues/20)
- [investment in basic science and art](https://github.com/Data4Democracy/usa-dashboard/issues/20)

This list is not meant to be exhaustive!  Any high-quality metric can be added to the dashboard.  Help us find some!

## Good metrics

Good metrics have the following characteristics:

- *Sensitivity*:  It moves regularly when things change, but does not move too randomly.
- *Timeliness*: The measurement does not lag reality too much.  Finding out that something is going wrong a month after it happens is not very useful.
- *Construct validity*: It measures something important that we care about.  It is defined well enough that we can compare over time.
- *Historically available*: Not a deal-break, but being able to measure at least a year of history is helpful.

We are striving to produce metrics that are updated at least once a week, and ideally every day.  To do that we are going to engage in original data collection and also advanced statistical modeling and [nowcasting](https://en.wikipedia.org/wiki/Nowcasting_(economics)).

## Get involved!

We have several streams of work going on right now, each attached to a milestone:

- [Scraping crime data](https://github.com/Data4Democracy/usa-dashboard/milestone/1):  We have a few cities covered, but we'd like to cover the top 
- [Exploratory data analysis](https://github.com/Data4Democracy/usa-dashboard/milestone/4): After data is collected, it needs to be validated and modeled before we will visualize it.
- [Deciding what to capture for other metrics](https://github.com/Data4Democracy/usa-dashboard/milestone/2):
- [Designing the user interface](https://github.com/Data4Democracy/usa-dashboard/milestone/3): Ultimately people will consume the dashboard through web and mobile interfaces, as well as through sharing graphics we we produce.  We need help designing all of these surfaces.

Once we have collected more data, there will be substantive data engineering tasks to automate all of this.
