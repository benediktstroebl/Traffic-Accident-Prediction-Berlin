High-resolution traffic accident prediction in Berlin
=====================================================

<H1 align="center">
    <img href="" src="https://github.com/aneleh-cikab/distill-template/blob/225f9230b6ecdac949d736864ca72fc4f59d762b/figures/berlin_accident.jpg" width="450px">
</H1>
    
Traffic accidents are one of the leading causes of death and injuries globally, and in Germany they cause over 3,000 deaths and 300,000 injuries yearly. Studying traffic accidents and where and why they happen can help policy makers make our roads safer. Therefore, we built and trained several machine learning models to predict the risk of occurrence of a traffic accident on a road segment for a given hour and day in Berlin. Form this analysis, local policy-makers can derive valuable insights into which factors determine dangerous road segments and when and where collisions are more likely to happen.

**Take a look our project presentation slides** to get a better overview about the project <a href="https://github.com/benediktstroebl/Machine-Learning-Project-Group-F/blob/5b21e6ebf7b6df23e150918128c9aa951f85235b/project%20presentation%20slides/Group%20F_presentation_slides_Arbo_Bakic_Str%C3%B6bl.pdf">**here!**</a>

## Data

We conducted this study using the example of accidents in Berlin using the following data sources:

* **Records of traffic accidents in Berlin**: Open Data Berlin shares records of all traffic accidents that happened between 2018 and 2020; a total of 38,851 occurrences. For this study we used data on GPS-coordinates, year, month, day of the week, and hour of the accident.

* **Berlin road segment data**: We used two datasets provided by the Open Data Informationsstelle (ODIS):

  * To match locations of traffic accidents (Figure 1a) to road segments in Berlin (Figure 1b) we used the existing geometric information dataset on road segments in   Berlin. From here we also used data on the length of the road segment.
  * We used road segment surface dataset to extract the information on whether a road segment is a main road or a side street.

<H1 align="center">
    <img href="" src="https://github.com/aneleh-cikab/distill-template/blob/225f9230b6ecdac949d736864ca72fc4f59d762b/figures/1a.png" width="300px">
</H1>
<H1 align="center">
    <img href="" src="https://github.com/aneleh-cikab/distill-template/blob/225f9230b6ecdac949d736864ca72fc4f59d762b/figures/1b.png" width="300px">
</H1>

* **Weather data**: Using the Wetterdienst API we collected data on temperature, humidity, precipitation duration, precipitation height, and visibility for every accident location, day of the week, and hour of the day between 2018 and 2020 from 5 Berlin weather stations.

* **Sun elevation**: We used the Python API PySolar to collect data on sun elevation angles per date and location in Berlin.

## Authors

- [@benediktstroebl](https://www.github.com/benediktstroebl)
- [@adellegia](https://www.github.com/adellegia)
- [@aneleh-cikab](https://www.github.com/aneleh-cikab)
  

