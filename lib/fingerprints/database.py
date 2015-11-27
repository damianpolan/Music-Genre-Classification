import mysql.connector
import mysql
from scikits.audiolab import wavread
import cPickle
import MySQLdb
import features
import tools
from UserString import MutableString


class Controller:

    """
    Default DB:
    user='user', password='', host='127.0.0.1', database='fingerprints'


    Must call DataBaseController.commit() manually.
    """

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
        # self.cur.execute("DROP TABLE IF EXISTS Genres")
        # self.cur.execute("DROP TABLE IF EXISTS FeatureData")
        # self.cur.execute("DROP TABLE IF EXISTS Songs")

        # sample index is the start index of the data in the original sample data list.
        self.createTables()
        # self.cur.execute("CREATE TABLE IF NOT EXISTS SupportedFeatures(\
        #                 feature_name varchar(32),\
        #                 primary key (feature_name)\
        #                 )")

    def createTables(self):
        # ADD ALL REQUIRED TABLES
        self.cur.execute("CREATE TABLE IF NOT EXISTS Songs(\
                        song_id int AUTO_INCREMENT,\
                        song_name varchar(64),\
                        artist varchar(64),\
                        seconds int,\
                        file_path varchar(255),\
                        PRIMARY KEY (song_id)\
                        )")

        self.cur.execute("CREATE TABLE IF NOT EXISTS Genres(\
                        song_id int,\
                        genre varchar(32),\
                        PRIMARY KEY (song_id, genre),\
                        FOREIGN KEY (song_id) REFERENCES Songs(song_id)\
                        )")

        self.cur.execute("CREATE TABLE IF NOT EXISTS FeatureData(\
                        song_id int,\
                        pack_index int,\
                        feature_name varchar(32),\
                        pack_size int,\
                        data LONGBLOB,\
                        primary key (song_id, pack_index, feature_name, pack_size),\
                        FOREIGN KEY (song_id) REFERENCES Songs(song_id)\
                        )")
        self.conn.commit()

    def deleteAllEntries(self):
        print "Deleting Tables"
        # self.cur.execute("DROP TABLE IF EXISTS Genres")
        # self.cur.execute("DROP TABLE IF EXISTS FeatureData")
        # self.cur.execute("DROP TABLE IF EXISTS Songs")
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.cur.execute("truncate table Genres")
        self.cur.execute("truncate table FeatureData")
        self.cur.execute("truncate table Songs")
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        self.createTables()
        self.conn.commit()

    def commit(self):
        self.conn.commit()

    def addSong(self, file_path, song_name, artist, seconds, genres):
        """
        Adds a song to the database
        """

        print "Adding song " + file_path
        # # check if song already exists on bases of song_name and artist
        self.cur.execute("SELECT file_path FROM Songs WHERE file_path=%s", (file_path,))

        fetched = self.cur.fetchone()
        if fetched:
            print "Song already exists. Not added to database."
            return

        # INSERT INTO Songs TABLE
        self.cur.execute("INSERT INTO Songs (song_name, artist, seconds, file_path) VALUES (%s, %s, %s, %s)", (song_name, artist, seconds, file_path))

        # INSERT GENRES FOR THE SONG
        # get the newly made song_id
        new_song_id = self.cur.lastrowid  # (last mysql generated row id)
        for genre in genres:
            self.cur.execute("INSERT INTO Genres (song_id, genre) VALUES (%s, %s)", (new_song_id, genre))

        # we are not process features for the newly added song until they are requested by the learning algorithm.

        print "Successfully added."

    # initialize required databases
    def pullFeatureForSong(self, feature_name, song_id, pack_size):
        """
            Returns an array with elements of type <feature_name>.

            The song is split into n number of sample packs. Each sample pack is of size pack_size.
            The feature is evaluated on each sample pack and filled into the returned array (in same order).

            If no data is already present in the database for the given pack_size, the feature will be evaluated for the whole song and added to the database.

            @param feature_name: the feature to get
            @param song_id: the song to get the feature for
            @param pack_size: the size of the packets to split the song into. (-1 to apply the feature to the whole song)dw
        """

        # PULL IF FEATURE THAT ALREADY EXISTS
        self.cur.execute("SELECT data FROM FeatureData WHERE song_id=%s AND feature_name=%s AND pack_size=%s", (song_id, feature_name, pack_size))

        class_ = getattr(features, feature_name)  # prepare the class for instanciation
        packList = []

        row = self.cur.fetchone()

        if(row):  # RETURN THE LIST OF FEATURES
            while (row):
                feature = class_.unserialize(row[0])
                packList.append(feature)
                row = self.cur.fetchone()
        else:  # NO ELEMENTS FOUND, COMPUTE
            print "No match found. Creating ..."
            rawData = self.fetchSongData(song_id)  # fetch raw data from file on disk
            rawChunks = tools.chunks(rawData, pack_size)  # Split the song into chunks of size pack_size. this will be processed by the feature

            # iterate and create a feature for each one to save to the DB
            pack_index = 0
            for dataPack in rawChunks:
                feature = class_(dataPack)
                packList.append(feature)
                serialized = feature.serialize()
                print "Inserting feature for pack " + str(pack_index)
                self.cur.execute("INSERT INTO FeatureData (song_id, pack_index, feature_name, pack_size, data) VALUES (%s, %s, %s, %s, %s)", (song_id, pack_index, feature_name, pack_size, serialized))
                pack_index += pack_size

        return packList

    def fetchSongData(self, song_id):
        self.cur.execute("SELECT file_path FROM Songs WHERE song_id=%s", (song_id,))
        file_path = self.cur.fetchone()[0]

        ampData, fs, enc = wavread(file_path)
        return ampData


import sys
import os


def main(argv):
    """

    Required actions:
        clear database

        add
            add new song
            add batch of songs from folder

    argv:

    param 0:
        action name



    """
    print;
    if len(argv) < 1:
        print "Required paramater action"
        print
        return;

    supportedExt = [".wav"]
    action = argv[0];

    if(action == "add"):
        absPath = os.path.abspath(argv[1])
        if os.path.isfile(absPath):
            if len(argv) < 3:
                print "Required paramaters path genre0 genre1 ... genre n"
                print

            filename, extension = os.path.splitext(absPath)
            if(extension in supportedExt):
                # file is valid and we can add it to the database
                genres = argv[2:]
                dbControl = Controller()
                dbControl.addSong(absPath, "", "", "", genres)
                dbControl.commit()
                # print "Song added for genres " + ', '.join(genres) + " at:"
                print absPath
            else:
                print extension + " is not a supported file type."
        elif os.path.isdir(absPath):
            if len(argv) < 4:
                print "Required paramaters path maxcount genre0 genre1 ... genre n"
                print

            allFiles = os.listdir(absPath)
            maxCount = int(argv[2])
            genres = argv[3:]

            allWavs = []
            for file in allFiles:
                filename, extension = os.path.splitext(file)
                if(extension in supportedExt):
                    allWavs.append(file)

            count = 0
            dbControl = Controller()

            for wav in allWavs:
                if (maxCount < 0 or count < maxCount): # -1 means add all files
                    abswav = absPath + wav
                    dbControl.addSong(abswav, "", "", "", genres)
                count += 1
            dbControl.commit()

            print "FINISHED adding songs for genrese(s) " + ', '.join(genres)

        pass
    elif(action == "clear"):
        dbControl = Controller()
        dbControl.deleteAllEntries()
        dbControl.commit()
        pass
        
    print
    return
    # os.environ["MGC_DB_MUSIC_DIR"] = "/home/damian/Music-Genre-Classification/FingerprintGenerator/TestSongs/";
    # dbControl = Controller(os.environ["MGC_DB_MUSIC_DIR"])


    # ampData, fs, enc = wavread("/home/damian/Music-Genre-Classification/FingerprintGenerator/TestSongs/Rap/Eminem-Stan.wav")

    # dbControl.addSong("Rap/Eminem-Stan.wav", "Stan", "Eminem", "354", ["rap"])
    # dbControl.commit()    


    # packList = dbControl.pullFeatureForSong("Feature_FreqDom", 1, 10000)

    # print len(packList[800].freqData)

    # dbControl.commit()
    print


if __name__ == "__main__":
    main(sys.argv[1:])
