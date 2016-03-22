import logging
import mysql.connector
import mysql
from scikits.audiolab import wavread
import os
import sys
import feature
from mgc.tools import logs
from training import TrainingSet
import re


class DatabaseService:
    """
    Default DB:
    user='user', password='', host='127.0.0.1', database='fingerprints'


    Must call DataBaseController.commit() manually.
    """

    ####################################################
    #   CONSTRUCTORS
    ####################################################

    def __init__(self, user='user', password='', host='127.0.0.1', database='features'):
        self.user = user
        self.password = password
        self.host = host
        self.database = database

        """ Connect to MySQL database """

        logging.debug('Connecting to SQL database: ' + host + ":" + database + '.')
        self.conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
        self.cur = self.conn.cursor()

        self.cached_song = dict()
        self.cached_song['file_path'] = None
        self.cached_song['pcm_data'] = None

        # self.__drop_all()
        self.__create_tables()
        self.__commit()

    ####################################################
    #   PRIVATE METHODS
    ####################################################

    def __drop_all(self):
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.cur.execute("DROP TABLE IF EXISTS Genres")
        self.cur.execute("DROP TABLE IF EXISTS Songs")
        self.cur.execute("DROP TABLE IF EXISTS Features")
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 1")

    def __create_tables(self):
        # ADD ALL REQUIRED TABLES
        self.cur.execute("CREATE TABLE IF NOT EXISTS Songs(\
                            song_id int AUTO_INCREMENT,\
                            file_path varchar(1024),\
                            PRIMARY KEY (song_id)\
                            )")

        self.cur.execute("CREATE TABLE IF NOT EXISTS Genres(\
                            song_id int,\
                            genre varchar(32),\
                            PRIMARY KEY (song_id, genre),\
                            FOREIGN KEY (song_id) REFERENCES Songs(song_id)\
                            )")

        self.cur.execute("CREATE TABLE IF NOT EXISTS Features(\
                            song_id int,\
                            feature_name varchar(32),\
                            version int,\
                            f_value double,\
                            primary key (song_id, feature_name),\
                            FOREIGN KEY (song_id) REFERENCES Songs(song_id)\
                            )")

    def __commit(self):
        self.conn.commit()

    def __get_training_song_ids(self, genres, max_set_size):
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
        :param genres:
        :param max_set_size:
        :return:
        """

        if not isinstance(genres, list):
            raise "Genres must be a list of strings. i.e: ['house', 'trance']"

        song_dict = {}

        query = "SELECT song_id FROM Genres WHERE genre=%s"

        for genre in genres:
            if(max_set_size >= 0):
                self.cur.execute(query + " LIMIT %s", (genre, max_set_size))
            else:
                self.cur.execute(query, (genre,))

            song_dict[genre] = []
            results = self.cur.fetchall()
            for result in results:
                song_dict[genre].append(result[0])

        return song_dict

    ####################################################
    #   PUBLIC METHODS
    ####################################################

    def delete_all_songs(self):
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.cur.execute("truncate table Genres")
        self.cur.execute("truncate table Songs")
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        self.__commit()

    def delete_all_features(self):
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.cur.execute("truncate table Features")
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        self.__commit()

    def add_song(self, file_path, genres):
        """
        Adds a song to the database
        :param file_path:
        :param genres:
        :return:
        """
        if not file_path.endswith(".wav"):
            logging.warning("File type not supported. Must be .wav")
            return

        logging.debug("Adding song:\t" + os.path.basename(file_path)[:50])
        # check if song already exists on bases of song_name and artist
        self.cur.execute("SELECT file_path FROM Songs WHERE file_path=%s", (file_path,))

        fetched = self.cur.fetchone()
        if fetched:
            logging.warning("Song already exists. Not added to database.")
            return

        # INSERT INTO Songs TABLE
        self.cur.execute("INSERT INTO Songs (file_path) VALUES (%s)", (file_path,))

        # INSERT GENRES FOR THE SONG
        # get the newly made song_id
        new_song_id = self.cur.lastrowid  # (last mysql generated row id)
        for genre in genres:
            self.cur.execute("INSERT INTO Genres (song_id, genre) VALUES (%s, %s)", (new_song_id, genre))

        self.__commit()
        # we are not process features for the newly added song until they are requested by the learning algorithm.
        logging.debug("Successfully added.")

    def get_song_pcm_data(self, song_id):
        """
        Gets the raw song data from the .wav file.
        :param song_id:
        :return:
        """
        self.cur.execute("SELECT file_path FROM Songs WHERE song_id=%s", (song_id,))
        file_path = self.cur.fetchone()[0]

        if self.cached_song['file_path'] != file_path:
            pcm_data, fs, enc = wavread(file_path)

            if len(pcm_data) == 0:
                raise "Could not read pcm data from wave file."

            self.cached_song['file_path'] = file_path
            self.cached_song['pcm_data'] = pcm_data

            if fs != 44100:
                raise "Sample rate not 44100."
            return pcm_data
        else:
            return self.cached_song['pcm_data']

    def get_training_set(self, genres, feature_names, max_set_size, verbose=False):
        genre_song_ids = self.__get_training_song_ids(genres, max_set_size)

        classes = []
        feature_sets = []
        for genre, song_ids in genre_song_ids.iteritems():
            logging.debug("Getting songs for " + genre)
            feature_sets_for_genre = []
            for song_id in song_ids:
                features_for_song = []
                for feature_name in feature_names:
                    f_value = self.get_feature_value(feature_name, song_id, verbose=verbose)
                    features_for_song.append(f_value)
                feature_sets_for_genre.append(features_for_song)

            classes.append(genre)
            feature_sets.append(feature_sets_for_genre)

        return TrainingSet(classes, feature_sets)

    def get_feature_value(self, feature_name, song_id, verbose=False):
        """

        :param feature_name:
        :param song_id:
        :return:
        """

        class_ = getattr(feature, feature_name)  # prepare the class for instantiation
        feature_instance = class_()

        self.cur.execute("SELECT version, f_value FROM Features WHERE song_id=%s AND feature_name=%s",
                         (song_id, feature_name))
        row = self.cur.fetchone()

        if row and row[0] == feature_instance.version:
            f_value = row[1]

            if verbose:
                logging.debug("song_id " + str(song_id) + ": Getting " + feature_name + " = " + str(f_value))
            return f_value
        else:
            # compute the feature and replace the existing row if there is one

            if verbose:
                logging.debug("song_id " + str(song_id) + ": " +
                          feature_name + " not found for current version. Calculating...")

            pcm_data = self.get_song_pcm_data(song_id)
            f_value = feature_instance.calculate(pcm_data)

            if verbose:
                logging.debug("song_id " + str(song_id) + ": " + feature_name + " = " + str(f_value))

            self.cur.execute("INSERT INTO Features (song_id, feature_name, version, f_value) VALUES (%s, %s, %s, %s) \
                              ON DUPLICATE KEY UPDATE version=%s, f_value=%s",
                             (song_id, feature_name, feature_instance.version, float(f_value),
                              feature_instance.version, float(f_value)))
            self.__commit()

    def delete_song(self, song_id):
        self.cur.execute("DELETE FROM Features WHERE song_id=%s", (song_id,))
        self.cur.execute("DELETE FROM Genres WHERE song_id=%s", (song_id,))
        self.cur.execute("DELETE FROM Songs WHERE song_id=%s", (song_id,))
        self.__commit()

    def get_features_for_song(self, file_path, feature_list):
        """
        Computes each of the features (must be full_song features) for the song recording.
        This method is used for one shot computation of a songs features.
        :param file_path:
        :param feature_list:
        :return: a tuple of values with length = len(features). Each item is the resulting feature value corresponding to features[].
        """

        # will hold the evaluated feature values
        feature_values = []

        pcm_data, fs, enc = wavread(file_path)

        for feature_name in feature_list:
            # print "Computing " + feature_name
            class_ = getattr(feature, feature_name)
            feature_instance = class_()
            f_value = feature_instance.calculate(pcm_data)
            feature_values.append(f_value)

        return tuple(feature_values)


def main(argv):
    """
    Executes an action on the database

    Required actions:
        clear database

        add
            add new song
            add batch of songs from folder

    argv:

    param 0:
        action name

    # EXAMPLES:
    # python database.py clear songs

    # python database.py add ~/Music/Dubstep/somesong.wav dubstep
    # python database.py add ~/Music/Dubstep/ -1 dubstep
    #
    # Multi genre:
    # python database.py add ~/Music/Dubstep/somesong.wav dubstep dnb progressive
    #
    :param argv:
    :return:

    """
    # logging.basicConfig(level=logging.DEBUG)
    logs.enable_default_log()

    if len(argv) < 1:
        print "Required parameter action"
        print
        return

    supported_ext = [".wav"]
    action = argv[0]

    if action == "add":
        abs_path = os.path.abspath(argv[1])
        if os.path.isfile(abs_path):
            if len(argv) < 3:
                print "Required parameters path genre0 genre1 ... genre n"
                print

            filename, extension = os.path.splitext(abs_path)
            if extension in supported_ext:
                # file is valid and we can add it to the database
                genres = argv[2:]
                db_control = DatabaseService()
                db_control.add_song(abs_path, genres)
                print "Song added for genres " + ', '.join(genres) + " at:"
                print abs_path
            else:
                print extension + " is not a supported file type."
        elif os.path.isdir(abs_path):

            if len(argv) < 4:
                print "Required parameters path maxcount genre0 genre1 ... genre n"
                print

            all_files = os.listdir(abs_path)
            max_count = int(argv[2])
            genres = argv[3:]

            all_wavs = []
            for file in all_files:
                filename, extension = os.path.splitext(file)
                if extension in supported_ext:
                    # rename the file to remove special characters
                    oldpath = abs_path + '/' + filename + extension
                    newpath = abs_path + '/' + re.sub('[^\w\.\-]+', ' ', filename) + extension
                    os.rename(oldpath, newpath)
                    all_wavs.append(newpath)

            count = 0
            db_control = DatabaseService()

            for wav in all_wavs:
                if max_count == -1 or count < max_count: # -1 means add all files
                    abswav = os.path.join(abs_path, wav)
                    db_control.add_song(abswav, genres)
                count += 1

            print "FINISHED adding " + str(count) + " songs for genre(s) " + ', '.join(genres)
    elif action == "clear":
        if len(argv) < 2:
            print "required param type for clear. Types: 'songs', 'features'"
            return

        db_control = DatabaseService()

        ctype = argv[1]
        if ctype == "songs":
            db_control.delete_all_songs()
        elif ctype == "features":
            db_control.delete_all_features()
        else:
            db_control.delete_song(ctype)

    return

if __name__ == "__main__":
    # main(['add', '/media/damian/Windows7_OS/Users/Damian/OneDrive/Music/ClassicalOutput', '-1', 'classical'])
    # main(['add', '/media/damian/Windows7_OS/Users/Damian/OneDrive/Music/JazzOutput', '-1', 'jazz'])
    # main(['add', '/media/damian/Windows7_OS/Users/Damian/OneDrive/Music/OperaOutput', '-1', 'opera'])
    # main(['add', '/media/damian/Windows7_OS/Users/Damian/OneDrive/Music/ReggaeOutput', '-1', 'reggae'])
    # main(['add', '/media/damian/Windows7_OS/Users/Damian/OneDrive/Music/ClassicRockOutput', '-1', 'rock'])
    # main(['add', '/media/damian/Windows7_OS/Users/Damian/OneDrive/Music/HouseOutput', '-1', 'house'])
    # main(['add', '/media/damian/Windows7_OS/Users/Damian/OneDrive/Music/HipHopOutput', '-1', 'hip hop'])


    # main (['clear', 'features'])
    # main (['clear', 'songs'])
    #main (['clear', '4389'])
    main(sys.argv[1:])


