import mysql.connector
import mysql
from scikits.audiolab import wavread
import cPickle
import MySQLdb
import features
import tools
from UserString import MutableString
import logging

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

        logging.debug('Connecting to SQL database: ' + host + ":" + database + '.')
        self.conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
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
        logging.debug("Clearing Tables")
        # self.cur.execute("DROP TABLE IF EXISTS Genres")
        # self.cur.execute("DROP TABLE IF EXISTS FeatureData")
        # self.cur.execute("DROP TABLE IF EXISTS Songs")
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.cur.execute("truncate table Genres")
        self.cur.execute("truncate table FeatureData")
        self.cur.execute("truncate table Songs")
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        # self.createTables()
        self.conn.commit()

    def deleteAllFeatureData(self):
        logging.debug("Clearing table FeatureData")
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.cur.execute("truncate table FeatureData")
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        self.conn.commit()

    def commit(self):
        self.conn.commit()

    def addSong(self, file_path, song_name, artist, seconds, genres):
        """
        Adds a song to the database
        """

        logging.debug("Adding song:\t" + os.path.basename(file_path)[:50])
        # # check if song already exists on bases of song_name and artist
        self.cur.execute("SELECT file_path FROM Songs WHERE file_path=%s", (file_path,))

        fetched = self.cur.fetchone()
        if fetched:
            logging.warning("Song already exists. Not added to database.")
            return

        # INSERT INTO Songs TABLE
        self.cur.execute("INSERT INTO Songs (song_name, artist, seconds, file_path) VALUES (%s, %s, %s, %s)", (song_name, artist, seconds, file_path))

        # INSERT GENRES FOR THE SONG
        # get the newly made song_id
        new_song_id = self.cur.lastrowid  # (last mysql generated row id)
        for genre in genres:
            self.cur.execute("INSERT INTO Genres (song_id, genre) VALUES (%s, %s)", (new_song_id, genre))

        # we are not process features for the newly added song until they are requested by the learning algorithm.

        logging.debug("Successfully added.")

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

        logging.debug("song_id " + str(song_id) + ":  " + feature_name + " with pack size " + str(pack_size) + " searching...")
        # PULL IF FEATURE THAT ALREADY EXISTS
        self.cur.execute("SELECT data FROM FeatureData WHERE song_id=%s AND feature_name=%s AND pack_size=%s", (song_id, feature_name, pack_size))

        class_ = getattr(features, feature_name)  # prepare the class for instantiation
        packList = []

        row = self.cur.fetchone()

        if row:  # RETURN THE LIST OF FEATURES

            # in the case that class_.requireFullSong == True, their should only be one row. But is returned in the same
            # way.

            while row:
                feature = class_.unserialize(row[0])
                packList.append(feature)
                row = self.cur.fetchone()

        else:  # NO ELEMENTS FOUND, COMPUTE
            raw_data = self.fetchSongData(song_id)  # fetch raw data from file on disk
            raw_chunks = []

            if pack_size == -1:
                raise "pack_size == -1 not yet supported."
            else:
                raw_chunks = tools.chunks(raw_data, pack_size)  # Split the song into chunks of size pack_size. this will be processed by the feature

            logging.debug("Feature Data not found. Generating feature data for " +
                          str(len(raw_data) / pack_size) + " packs...")


            if class_.requireFullSong: # single feature creation for full song
                feature = class_(raw_chunks)
                packList.append(feature)
                serialized = feature.serialize()
                logging.debug(feature_name + ".value = " + str(feature.value))
                self.cur.execute("INSERT INTO FeatureData (song_id, pack_index, feature_name, pack_size, data) VALUES (%s, %s, %s, %s, %s)",
                                 (song_id, 0, feature_name, pack_size, serialized))

            else: # feature creation for single sample pack
                # iterate and create a feature for each one to save to the DB
                pack_index = 0
                for dataPack in raw_chunks:
                    feature = class_(dataPack)
                    packList.append(feature)
                    serialized = feature.serialize()
                    self.cur.execute("INSERT INTO FeatureData (song_id, pack_index, feature_name, pack_size, data) VALUES (%s, %s, %s, %s, %s)",
                                     (song_id, pack_index, feature_name, pack_size, serialized))
                    pack_index += pack_size

            self.commit()  # commit the insertions

        return packList



    def fetchSongData(self, song_id):
        self.cur.execute("SELECT file_path FROM Songs WHERE song_id=%s", (song_id,))


        amp_data, fs, enc = wavread(file_path)
        return amp_data


    def getTrainingSet(self, genres, maxSetSize):
        """
            Gets a list of database song_id's which match at least one genre in genres.

            genres: array of genre names.
            maxSetSize: the maximum amount of training samples per genre. -1 for no limit.

            returns:
                dict object with format: 
                {
                    genre0: [ song_id list for genre0] 
                    genre1: [ song_id list for genre1]
                    ...
                    genreN: [ song_id list for genreN]
                }

            Example:
                database.getTrainingSet(['dubstep', 'house'], 100)
                ^ will return a list containing 50 elements of each genre
        """

        if not isinstance(genres, list):
            raise "Genres must be a list of strings."

        songDict = {}

        query = "SELECT song_id FROM Genres WHERE genre=%s"

        for genre in genres:
            if(maxSetSize >= 0):
                self.cur.execute(query + " LIMIT %s", (genre, maxSetSize))
            else:
                self.cur.execute(query, (genre,))

            songDict[genre] = []
            results = self.cur.fetchall()
            for result in results:
                songDict[genre].append(result[0])

        return songDict




import sys
import os

def main(argv):
    """
    Exectues an action on the database 

    Required actions:
        clear database

        add
            add new song
            add batch of songs from folder

    argv:

    param 0:
        action name

    # EXAMPLES: 
    # python database.py clear

    # python database.py add ~/Music/Dubstep/somesong.wav dubstep
    # python database.py add ~/Music/Dubstep/ -1 dubstep
    #
    # Multi genre:
    # python database.py add ~/Music/Dubstep/somesong.wav dubstep dnb progressive 
    # 

    """
    # logging.basicConfig(level=logging.DEBUG)
    tools.defaultLog()

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
                print "Required parameters path maxcount genre0 genre1 ... genre n"
                print

            allFiles = os.listdir(absPath)
            maxCount = int(argv[2])
            genres = argv[3:]

            allWavs = []
            for file in allFiles:
                filename, extension = os.path.splitext(file)
                print extension
                if(extension in supportedExt):
                    allWavs.append(file)

            count = 0
            dbControl = Controller()

            for wav in allWavs:
                if maxCount == -1 or count < maxCount: # -1 means add all files
                    abswav = os.path.join(absPath, wav)
                    dbControl.addSong(abswav, "", "", "", genres)
                count += 1
            dbControl.commit()

            print "FINISHED adding " + str(count) + " songs for genre(s) " + ', '.join(genres)

        pass
    elif(action == "clear"):
        if(len(argv) < 2):
            print "required param type for clear. Types: 'all', 'features'"
            return

        ctype = argv[1]
        if(ctype == "all"):
            dbControl = Controller()
            dbControl.deleteAllEntries()
        elif(ctype == "features"):
            dbControl = Controller()
            dbControl.deleteAllFeatureData()
        else:
            print "unknown clear param " + ctype
        pass

        
    print
    return


if __name__ == "__main__":
    main(sys.argv[1:])


"""

python database.py add ~/Music/House -1 house
python database.py add ~/Music/Dubstep -1 dubstep
python database.py add ~/Music/Trance -1 trance

"""