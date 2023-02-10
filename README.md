# ORTEGA

ortega is a python package for analyzing and visualizing potential interactions between a pair of moving entities based on the observation of their movement using the time-geographic approach. This python package has the ability to identifying potential interaction between moving entities based on their movement data and calculating the duration of interaction.

Current version of ortega only supports inputting GPS points of a pair of moving entities. It works the best when the two entities were tracked with the same sampling rate. The results may not be desirable when the sampling rate is different.

**Citation info:**
> Dodge, S., Su, R., Johnson, J., Simcharoen, A., Goulias, K., Smith, J. L., & Ahearn, S. C. (2021). [ORTEGA: An object-oriented time-geographic analytical approach to trace space-time contact patterns in movement data](https://www.sciencedirect.com/science/article/pii/S0198971521000375). *Computers, Environment and Urban Systems*, 88, 101630.
> 
> Su, R., Dodge, S., & Goulias, K. (2022). [A classification framework and computational methods for human interaction analysis using movement data](https://onlinelibrary.wiley.com/doi/full/10.1111/tgis.12960). *Transactions in GIS*, 26(4), 1665-1682.



## Getting started
ortega can be installed through pip command. 
```bash
pip install ortega
```
## How to use ortega

Check our [example notebook](https://github.com/move-ucsb/ORTEGA/blob/main/examples/example.ipynb) to learn how to use ortega for interaction analysis using movement data of two entities.

[//]: # (```bash)

[//]: # (pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple ortega)

[//]: # (```)

## Find any issues?

You may report any issues [here](https://github.com/move-ucsb/ORTEGA/issues).

## License
ortega is licensed under the MIT license. See the [LICENSE](https://github.com/move-ucsb/ORTEGA/blob/main/LICENSE) file for details.

