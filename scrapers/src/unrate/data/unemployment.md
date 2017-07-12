# Unemployment rate

**DRAFT**

```
unrate/
    data/
        google/
            jobs.2016-01-01 2017-05-17.csv
        national/
            2010-2019.csv 
            2000-2009.csv
```

Each dataset in the `google` directory records weekly Google search trend 
data for the specified keywords over the specified period. The first week is 
normalized at 100. The data for a specific keyword, e.g. `jobs`, is formatted
 as:

```
date,jobs
2016-01-03,100
2016-01-10,89
2016-01-17,89
2016-01-24,88
...
```

Each data set in the `national` directory records the 
unemployment rate published by the Bureau of Labor Statistics in the time 
period indicated by the name of the file. The data are formatted as:

```
date,[seriesname]
2016-06-01,4.9
2016-07-01,4.9
2016-08-01,4.9
2016-09-01,4.9
...
```

