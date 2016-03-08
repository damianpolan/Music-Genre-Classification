import logging
import mysql.connector
import mysql
from scikits.audiolab import wavread
import os
import sys

class DatabaseService:
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

        self.__drop_all()
        self.__create_tables()
        self.commit()

    ####################################################
    #   PRIVATE METHODS
    #
    ####################################################

    def __drop_all(self):
        self.cur.execute("DROP TABLE IF EXISTS Genres")
        self.cur.execute("DROP TABLE IF EXISTS Features")
        self.cur.execute("DROP TABLE IF EXISTS Songs")

    def __create_tables(self):
        # ADD ALL REQUIRED TABLES
        self.cur.execute("CREATE TABLE IF NOT EXISTS Songs(\
                            song_id int AUTO_INCREMENT,\
                            file_path varchar(255),\
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
                            fvalue double,\
                            primary key (song_id, feature_name),\
                            FOREIGN KEY (song_id) REFERENCES Songs(song_id)\
                            )")

    def __delete_all_songs(self):
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.cur.execute("truncate table Genres")
        self.cur.execute("truncate table Songs")
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 1")

    def __delete_all_features(self):
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.cur.execute("truncate table Features")
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 1")

    ####################################################
    #   PUBLIC METHODS
    #
    ####################################################

    def commit(self):
        self.conn.commit()

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

        # we are not process features for the newly added song until they are requested by the learning algorithm.
        logging.debug("Successfully added.")




