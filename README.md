# Effects of the Paris' Cycling Policies on Vehicular Flow - An Empirical Analysis

This repository contains the code and data accompanying the publication "Effects of the Paris’ Cycling Policies on Vehicular Flow – An Empirical Analysis", published in Transportation Research Record:
https://journals.sagepub.com/doi/full/10.1177/03611981251356507 

In this study, we investigate how major transformations in Paris’ road network since 2010 have influenced vehicular flow. The Network Fundamental Diagram (NFD) is a crucial tool in evaluating the effectiveness of policy interventions. According to its principles, modifications in transportation options, particularly those favoring more sustainable modes such as cycling and walking, significantly impact a network’s capacity and critical density. We employ a re-sampling methodology for NFDs, which provides a robust estimation of the flow and occupancy in Paris’ road network even under real-world traffic conditions, despite potentially inaccurate or faulty empirical data. 

This repository offers a Python implementation of the re-sampling methodology [^1] for Network Fundamental Diagrams (NFDs) measured in lane-kilometers. Additionally, we provide a tool for mapping loop detector data from any city to (historical) OpenStreetMap (OSM) data, available in the 'network-matching' folder. This functionality can be leveraged for analysis in other cities.

[^1]: L. Ambuehl, A. Loder, M. C. Bliemer, M. Menendez, and K. W. Axhausen, “Introducing a Re-Sampling Methodology for the Estimation of Empirical Macroscopic Fundamental Diagrams,” Transportation Research Record, vol. 2672, pp. 239–248, 2018.
