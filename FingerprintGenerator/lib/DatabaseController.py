import mysql.connector
import mysql as mdb
from scikits.audiolab import wavread
import cPickle


class DataBaseController:

    """
    Default DB:
    user='user', password='', host='127.0.0.1', database='fingerprints'

    """

    # the portion size (memory char) to break each song into when stored in the database.
    # WARNING: Do Not change. Requires a complete re-add of all songs to the database.
    SUBSAMPLE_SIZE = 2000
    SUBSAMPLE_COUNT = 500  # the number of song samples to use

    # the max amount of space (in char) available for a feature on each SUBSAMPLE_SIZE of song.
    MAX_FEATURE_DATA_SIZE = 10000

    def __init__(self, user='user', password='', host='127.0.0.1', database='fingerprints'):
        self.user = user
        self.password = password
        self.host = host
        self.database = database

        """ Connect to MySQL database """

        print 'Connecting to SQL database: ' + host + " - " + database + ' ... '
        self.conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
        print 'Connected.'



        self.cur = self.conn.cursor()

        # DROPS ALL TABLES - for testing
        self.cur.execute("DROP TABLE SupportedFeatures")
        self.cur.execute("DROP TABLE Data_Features")
        self.cur.execute("DROP TABLE Data_Raw")
        self.cur.execute("DROP TABLE Genres")
        self.cur.execute("DROP TABLE IF EXISTS Metadata")

        # ADD ALL REQUIRED TABLES
        self.cur.execute("CREATE TABLE IF NOT EXISTS Metadata(\
                        song_id int AUTO_INCREMENT,\
                        song_name varchar(64),\
                        artist varchar(64),\
                        length int,\
                        PRIMARY KEY (song_id)\
                        )")

        self.cur.execute("CREATE TABLE IF NOT EXISTS Genres(\
                        song_id int,\
                        genre varchar(32),\
                        PRIMARY KEY (song_id, genre),\
                        FOREIGN KEY (song_id) REFERENCES Metadata(song_id)\
                        )")

        self.cur.execute("CREATE TABLE IF NOT EXISTS Data_Raw(\
                        song_id int,\
                        sample_index int,\
                        data varchar(" + str(DataBaseController.SUBSAMPLE_SIZE) + "),\
                        primary key (song_id, sample_index),\
                        FOREIGN KEY (song_id) REFERENCES Metadata(song_id)\
                        )")

        self.cur.execute("CREATE TABLE IF NOT EXISTS Data_Features(\
                        song_id int,\
                        sample_index int,\
                        feature_name varchar(32),\
                        data varchar(" + str(DataBaseController.MAX_FEATURE_DATA_SIZE) + "),\
                        primary key (song_id, sample_index, feature_name),\
                        FOREIGN KEY (song_id) REFERENCES Metadata(song_id),\
                        FOREIGN KEY (song_id, sample_index) REFERENCES Data_Raw(song_id, sample_index)\
                        )")

        self.cur.execute("CREATE TABLE IF NOT EXISTS SupportedFeatures(\
                        feature_name varchar(32),\
                        primary key (feature_name)\
                        )")

        self.conn.commit()

    def addSong(self, rawData, metadata):
        """

        metadata [dict] object format:
        {
            "song_name":string,   
            "artist":string,      
            "length":int,         #(seconds)
            "genres":[]
        }
        """
        # add song metadata to table
        self.cur.execute("INSERT INTO Metadata (song_name, artist, length) VALUES \
                            ( \'" + str(metadata['song_name']) + "\',\'" + str(metadata['artist']) + "\',\'" + str(metadata['length']) + "\')")

        #get the song_id
        new_song_id = self.cur.lastrowid;

        # add associated genres
        for genre in metadata['genres']:
            self.cur.execute("INSERT INTO Genres (song_id, genre) VALUES \
                            (\'" + str(new_song_id) + "\',\'" + genre + "\')")

        # split the song into appropriate samples and add to table
        for sample_index in range(len(rawData) / (DataBaseController.SUBSAMPLE_COUNT)):
            # serialize the data
            pickled = cPickle.dumps(rawData[sample_index:DataBaseController.SUBSAMPLE_COUNT])
            #print pickled

        self.conn.commit()

    # initialize required databases
    def addNewFeature(self, feature_name):
        """
        Adds a new feature and computes the feature for every song in the database.
        WARNING: this is a computationally intensive task. Set paramater computeAll to false if just for testing
        """
        pass

    def __addFeatureForSong(self, song_id):
        pass

import sys


def main(argv):
    dbControl = DataBaseController()

    ampData, fs, enc = wavread("/home/damian/Music-Genre-Classification/FingerprintGenerator/TestSongs/Rap/Eminem-Stan.wav")

    dbControl.addSong(ampData, {
        "song_name": "Eminem",
        "artist": "Stan",
        "length": 0,
        "genres": ["rap"]
    })


if __name__ == "__main__":
    main(sys.argv[1:])
