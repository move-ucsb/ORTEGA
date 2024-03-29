# ORTEGA

ORTEGA is a Python package for analyzing and visualizing potential interactions between a pair of moving entities based on the observation of their movement using a time-geographic-based approach.
ORTEGA contributes two significant capabilities: (1) the functions to identify potential interactions (e.g., encounters, concurrent interactions, delayed interactions) from movement data of two or more entities using a time-geographic-based approach; and (2) the capacity to compute attributes of potential interaction events including start time, end time, interaction duration, and difference in movement parameters such as speed and moving direction, and also contextualize the identified potential interaction events.

Current version of ORTEGA only supports inputting GPS points of a pair of moving entities. It works the best when the two entities were tracked with the same sampling rate. The results may not be desirable when the sampling rate is different. To conduct interaction analysis for more than two individuals, the user will need to employ For loops, by considering a moving entity as a reference at each loop and running the analysis in conjunction with all other individuals in the data set. 

**Citation info:**
> Dodge, S., Su, R., Johnson, J., Simcharoen, A., Goulias, K., Smith, J. L., & Ahearn, S. C. (2021). [ORTEGA: An object-oriented time-geographic analytical approach to trace space-time contact patterns in movement data](https://www.sciencedirect.com/science/article/pii/S0198971521000375). *Computers, Environment and Urban Systems*, 88, 101630.
> 
> Su, R., Dodge, S., & Goulias, K. (2022). [A classification framework and computational methods for human interaction analysis using movement data](https://onlinelibrary.wiley.com/doi/full/10.1111/tgis.12960). *Transactions in GIS*, 26(4), 1665-1682.
>
> Su, R., Liu, Y. & Dodge, S. (2024). [ORTEGA v1.0: an open-source Python package for context-aware interaction analysis using movement data](https://doi.org/10.1186/s40462-024-00460-2). *Movement Ecology* 12, 20. 




## Getting started
ORTEGA can be installed through pip command. 
```bash
pip install ortega
```
## How to use ortega

Check our [example notebook](https://github.com/move-ucsb/ORTEGA/blob/main/examples/example.ipynb) to learn how to use ORTEGA for interaction analysis using movement data of two entities.


[//]: # (```bash)
[//]: # (pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple ortega)
[//]: # (```)

## Find any bugs?

You may report any bugs [here](https://github.com/move-ucsb/ORTEGA/issues).

## License
ORTEGA is licensed under the MIT license. See the [LICENSE](https://github.com/move-ucsb/ORTEGA/blob/main/LICENSE) file for details.

