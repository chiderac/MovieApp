import mysql.connector
from config import USER, HOST, PASSWORD
from flask_mysqldb import MySQL
import MySQLdb.cursors


# Exception
class DbConnectionError(Exception):
    pass


# Connect to the database
def _connect_to_db(db_name):
    cnx = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=db_name
    )
    return cnx




# mycursor = cnx.cursor()

# mycursor.execute("CREATE TABLE customers (name VARCHAR(255), address VARCHAR(255))")
            


# CREATE USER TABLE 
# def create_user_table():
#     try:
#         db_name = 'movie_database'  # DB NAME
#         db_connection = _connect_to_db(db_name)  # CONNECT TO DATBASE FUNCTION
#         cur = db_connection.cursor()  # CURSOR OBJECT THAT WILL EXECUTE QUERIES THAT WE WANT
#         print(f"Connected to DB: {db_name}")

#         query = "CREATE TABLE User (id Integer primary key, fullname VARCHAR(255) NOT NULL, username VARCHAR(255) NOT NULL, email VARCHAR(255), password VARCHAR(255) NOT NULL) "
#         cur.execute(query)

#         cur.close()

#     except Exception:
#         raise DbConnectionError("Failed to read data from DB")

#     finally:
#         if db_connection:
#             db_connection.close()
#             print("DB connection is closed")
            
def save_data(change):
    result = None
    db_connection = None
    
    db_name = 'movieapp'
    db_connection = _connect_to_db(db_name)
    cur = db_connection.cursor(dictionary=True)
    print("Connected to DB: %s" % db_name)
    #query = ('INSERT INTO Movies VALUES (% s, % s, % s, % s, % s, % s, % s)', (id, title, release_year, genre, user_rating, poster, language, trailer))
    query = ("INSERT INTO movies (id, title, year, genre, user_rating, poster, original_language, trailer) VALUES (% s, % s, % s, % s, % s, % s, % s, % s)")
    #data = (id, title, year, genre, user_rating, poster, original_language, trailer)
    
    cur.execute(query, change)
    # for data in change:
    #     cur.execute(query)
    result = cur.fetchall() 
    cnx.commit()
    print("its saved")
    #mysql.connection.commit()
    result = cur.fetchall()  # this is a list with db records where each record is a tuple
    cur.close()
    return result
        
    # except Exception:
    #     raise DbConnectionError("Failed to read data from DB")
    
    # finally:
    #     if db_connection:
    #         db_connection.close()
    #         print("DB connection is closed")
    #     return result           



# if __name__ == '__main__':
#     save_data()
    