from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers
from requests_aws4auth import AWS4Auth
import boto3
import csv

REGION = 'us-east-2'
HOST = 'search-songs-zcnwgrrvwmhq7hwgv22g5mjawy.us-east-2.es.amazonaws.com'
DATA_PATH = '../Data/song_data.csv'

FIELD_ID = '_id'
FIELD_SOURCE = '_source'
FIELD_ARTIST = 'artist'
FIELD_SONG = 'song'
FIELD_LYRICS = 'lyrics'


def readDataToActions():
    """
    Will read data a CSV file in DATA_PATH and convert it to actions that can be
    sent to the elasticsearch cluster.
    :return:
    """
    with open(DATA_PATH) as csv_file:
        actions = []
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader) # Skip header line

        index = 1
        for row in csv_reader:
            actions.append(createAction(row, index))
            index += 1

        print(f'Processing {index} lines.')
        return actions

def createSourceAction(csvRow, index):
    return {
        "_index": "songs",
        "_type": "_doc",
        FIELD_ID: index,
        FIELD_SOURCE: {
            FIELD_ARTIST: csvRow[0],
            FIELD_SONG: csvRow[1],
            FIELD_LYRICS: csvRow[3]
        }
    }

def createAction(csvRow, index):
    return {
        "_index": "songs",
        "_type": "_doc",
        FIELD_ID: index,
        FIELD_ARTIST: csvRow[0],
        FIELD_SONG: csvRow[1],
        FIELD_LYRICS: csvRow[3]
    }


def getEsInstance():
    """
    Will use credentials given in the AWS cli to connect to the elasicsearch cluster.
    :return: An instance of an elasticsearch object.
    """
    credentials = boto3.Session().get_credentials()
    # es specifies a connection to an elastic search cluster.
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, REGION, 'es')

    return Elasticsearch(
        hosts=[{'host': HOST, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

def bulkInsertSongData():
    """
    Inserts the data in the data folder into to cluster using a bulk insert.
    """
    # Connect to Elastic search server
    es = getEsInstance()
    print(es.info())
    # Insert data
    helpers.bulk(es, readDataToActions())
    print('DONE')

if __name__ == '__main__':
    bulkInsertSongData()
