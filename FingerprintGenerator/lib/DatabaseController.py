import mysql.connector
import mysql
from scikits.audiolab import wavread
import cPickle
import MySQLdb
import features
from UserString import MutableString

class DataBaseController:

    """
    Default DB:
    user='user', password='', host='127.0.0.1', database='fingerprints'


    Must call DataBaseController.commit() manually.
    """

    # WARNING: Do Not change. Requires a complete re-add of all songs to the database.
    # SUBSAMPLE_MEM = 70000  # the portion of memory to allocate for a data pack. should be at least 70xSUBSAMPLE_COUNT to be safe
    SUBSAMPLE_COUNT = 10000  # the number of song samples to use in one data item

    # The portion of memory allocated for a feature on each SUBSAMPLE_COUNT of song.
    # FEATURE_DATA_MEM = 100000

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
        # print "Droping all tables..."
        # self.cur.execute("DROP TABLE IF EXISTS SupportedFeatures")
        # self.cur.execute("DROP TABLE IF EXISTS Data_Features")
        # self.cur.execute("DROP TABLE IF EXISTS Data_Raw")
        # self.cur.execute("DROP TABLE IF EXISTS Genres")
        # self.cur.execute("DROP TABLE IF EXISTS Metadata")

        print "Creating all tables..."
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
                        data blob,\
                        primary key (song_id, sample_index),\
                        FOREIGN KEY (song_id) REFERENCES Metadata(song_id)\
                        )")

        self.cur.execute("CREATE TABLE IF NOT EXISTS Data_Features(\
                        song_id int,\
                        sample_index int,\
                        feature_name varchar(32),\
                        data blob,\
                        primary key (song_id, sample_index, feature_name),\
                        FOREIGN KEY (song_id) REFERENCES Metadata(song_id),\
                        FOREIGN KEY (song_id, sample_index) REFERENCES Data_Raw(song_id, sample_index)\
                        )")
        # sample index is the start index of the data in the original sample data list.

        self.cur.execute("CREATE TABLE IF NOT EXISTS SupportedFeatures(\
                        feature_name varchar(32),\
                        primary key (feature_name)\
                        )")
        print "Commiting..."
        self.conn.commit()
        print "Done"

    def commit(self):
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

        print "Adding song " + metadata['song_name'] + " - " + metadata['artist'] + " ..."
        # check if song already exists on bases of song_name and artist
        self.cur.execute("SELECT song_name, artist FROM Metadata WHERE song_name=%s AND artist=%s", (metadata['song_name'], metadata['artist']))

        if self.cur.fetchone():
            print "Song " + metadata['song_name'] + " - " + metadata['artist'] + " already exists. Not added to database."
            return
        # add song metadata to table
        self.cur.execute("INSERT INTO Metadata (song_name, artist, length) VALUES \
                            ( \'" + str(metadata['song_name']) + "\',\'" + str(metadata['artist']) + "\',\'" + str(metadata['length']) + "\')")

        # get the song_id
        new_song_id = self.cur.lastrowid  # (last mysql generated row id)

        # add associated genres
        for genre in metadata['genres']:
            self.cur.execute("INSERT INTO Genres (song_id, genre) VALUES \
                            (\'" + str(new_song_id) + "\',\'" + genre + "\')")

        # split the song into appropriate samples and add to table
        for sample_index in range(0, len(rawData), (DataBaseController.SUBSAMPLE_COUNT)):
            # sample_index will always be the start index of the data

            data = rawData[sample_index:(sample_index + DataBaseController.SUBSAMPLE_COUNT)]
            pickled = cPickle.dumps(data)  # serialize the data
            # insert into DB
            self.cur.execute("INSERT INTO Data_Raw (song_id, sample_index, data) VALUES (\'" + str(new_song_id) + "\',\'" + str(sample_index) + "\',%s)", (pickled,))

        # process features for song
        print "Successfully added."

    # initialize required databases
    def addNewFeature(self, feature_name):
        """
        Adds a new feature and computes the feature for every song in the database.
        WARNING: this is a computationally intensive task. Set paramater computeAll to false if just for testing
        """

        self.cur.execute("SELECT feature_name FROM SupportedFeatures WHERE feature_name=%s", (feature_name,))
        if self.cur.fetchone():
            print "Feature " + feature_name + " already exists. Doing Nothing."
            return

        # Insert the new feature into SupportedFeatures table.
        self.cur.execute("INSERT INTO SupportedFeatures (feature_name) VALUES (%s)", (feature_name,))

        # process all songs
        self.reComputeFeature(feature_name)

    def reComputeFeature(self, feature_name):
        """
        Recomputes a feature for all songs in the DB.
        """

        print "Calculating " + feature_name + " for all songs..."

        # delete all existing
        self.cur.execute("DELETE FROM Data_Features WHERE feature_name=%s", (feature_name,))

        self.cur.execute("SELECT song_id, artist, song_name FROM Metadata")
        song_ids = self.cur.fetchall()

        # We split this up on a per-song_id basis so that only one song is in memory at a time.
        for song_id, artist, song_name in song_ids:
            print "Computing " + feature_name + " for " + artist + " - " + song_name
            self.__addFeatureForSong(song_id, feature_name)

        print "Done."

    def __addFeatureForSong(self, song_id, feature_name):

        self.cur.execute("SELECT sample_index, data from Data_Raw WHERE song_id=%s", (song_id,))

        songData = self.cur.fetchall()

        count = 0;
        for (sample_index, data) in songData:
            # print str(song_id) + ": sample_index " + str(sample_index)
            # Gets the feature class for instanciation.
            class_ = getattr(features, feature_name)
            feature = class_(data)

            count += 1;
            sys.stdout.write('\r')
            sys.stdout.write("[%i" % (float(count) / float(len(songData)) * 100,) + "%]")
            sys.stdout.flush()

            # insert serialized data to Data_Features
            self.cur.execute("INSERT INTO Data_Features (song_id, sample_index, feature_name, data) VALUES (%s, %s, %s, %s)", (song_id, sample_index, feature_name, data))  
        print ""


def method6():
    return ''.join([`num` for num in xrange(loop_count)])


import sys


def main(argv):
    dbControl = DataBaseController()

    ampData, fs, enc = wavread("/home/damian/Music-Genre-Classification/FingerprintGenerator/TestSongs/Rap/Eminem-Stan.wav")

    # dbControl.addSong(ampData, {
    #     "song_name": "Eminem",
    #     "artist": "Stan",
    #     "length": 0,
    #     "genres": ["rap"]
    # })

    dbControl.addNewFeature("Feature_FreqDom")
    dbControl.commit()


if __name__ == "__main__":
    main(sys.argv[1:])
