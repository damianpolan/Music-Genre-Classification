import sys
from learner import Learner
from database import DatabaseService


def main(argv):

    db_service = DatabaseService()
    genres = [
        'dubstep',
        'house',
        'trance'
    ]
    required_features = [
        "Centroid_Avg",
        "Centroid_SD",
    ]

    learner = Learner(db_service, genres, required_features, 10)

if __name__ == "__main__":
    main(sys.argv[1:])