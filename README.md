# Music-Genre-Classification
##Project Topic
The project will explore the following general topics: signal processing and analysis, machine learning, data extraction.

##Objective
Research, Design, and Implement a method for identifying the musical genre of a recorded audio sample.
####Sub-objectives:
- develop an effective approach to creating an acoustic fingerprint from a sample of music
- research an appropriate algorithm to use for classification
- collect a large training set for effective classification
		

##Significance

The information age has brought all forms of media to the online world. In terms of music, a number of websites exist which are used to share, store, organize, and manage songs from all over the world. For a person searching for new songs it can be hard to discover songs appealing to the specific musical genres they are interested in. For example, the online audio sharing platform, soundcloud.com, allows a user to explore new music based on the genre and the popularity of songs. Currently, soundcloud only covers about 30 categories of genre out of over 300 readily known genres. Many songs distributed into these genres are poorly classified and can lead to frustration when users try to find new songs they might like. It can be speculated that genre misclassification is caused by soundcloud’s reliance on genre tags, which are often mis-tagged by users of the system.

It is hoped that by creating an effective music genre classification algorithm, users will be able to make more meaningful genre and subgenre searches on sites like soundcloud.

Since this project is ultimately an academic one, the creators of this project look forward to the learning experience as well as gaining a more in-depth understanding of the topics of audio signal processing and analysis, machine learning, and data extraction. In doing so, the creators hope to develop knowledge and skills that will also be useful in the workplace.

In my individual part I will be focusing on the research/implementation of the acoustic fingerprint generator and the classification algorithm. The success of the system relies heavily on the design of both of the components. The classification algorithm effectiveness is dependent on how well the acoustic fingerprint represents a given song. Both components are completely decoupled and can be developed independently.

##Method

The entire project is broken down into a few key components which will eventually be brought together as a working system. 

The first component deals with analyzing the raw data of a sound input file and building a condensed digital summary known as an acoustic fingerprint. Each sound will have its own unique fingerprint, such that songs that sound similar to humans will also have similar fingerprints. A good acoustic fingerprint is key for the chosen classification algorithm to function properly, therefore developing the acoustic fingerprint generator will involve doing substantial research in order to determine the most appropriate set of methods to generate the footprint.

The second component will be responsible for training on a large set of musical songs such that it can be used for independent classification of other songs. Many possible algorithms exist that can be used for classification of this kind including Neural Networks (NN), Recurrent Neural Networks (RNN), Naive Bayesian classification, and Dependence Tree classification. Some research will have to be made in selecting the best algorithm for this task. If the time permits it, more than one of these algorithms can be used and compared. Once selected, the algorithm can be trained using an n-fold cross validation technique with all preprocessing for each song done by the acoustic fingerprint generator. A set of non-trained songs will be used to verify the trained algorithms hit rate as well. Depending on the coverage of the data set, training will be done on two different musical genres at first and then possibly scaled up to more.

For the classification algorithm to work properly, a large training set is needed. A minimum goal of five thousand songs in each chosen genre will be needed, although more would be prefered. In order to reach this goal of songs, an online music website scraper will be used as the third component. A number of websites such as jango, songza, soundcloud have millions of available songs, all with musical tags. The websites each have songs which are licensed to download for personal use and therefore the scraper will have to be built to exclusively download these songs. The scraper will search through lists of songs on the websites and download them based on preset genre tags. A subset of the downloaded songs can be inspected to ensure the correct genres were tagged by the website users.

