import psycopg2
from src.database.postgres_db import db
from src.database.mongo_logger import mongo_logger


class UserService:
    @staticmethod
    def create_user(username, email):
        conn = db.get_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cursor:
                query = (
                    "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id;"
                )
                cursor.execute(query, (username, email))
                user_id = cursor.fetchone()[0]
            conn.commit()

            # Log activity in MongoDB
            mongo_logger.log_activity(
                {
                    "action": "user_created",
                    "username": username,
                    "user_id": str(user_id),
                }
            )

            return user_id
        except Exception as e:
            print(f"Error creating user: {e}")
            conn.rollback()
            return None
        finally:
            db.put_connection(conn)

    @staticmethod
    def follow_user(follower_id, followed_id):
        """
        Transactional follow action.
        Updates 'followers' table and 'users' table (counts) atomically.
        """
        if follower_id == followed_id:
            return False, "Cannot follow yourself."

        conn = db.get_connection()
        if not conn:
            return False, "Database connection error."

        try:
            with conn.cursor() as cursor:
                # 1. Insert into followers
                cursor.execute(
                    "INSERT INTO followers (follower_id, followed_id) VALUES (%s, %s);",
                    (follower_id, followed_id),
                )

                # 2. Increment following_count for follower
                cursor.execute(
                    "UPDATE users SET following_count = following_count + 1 WHERE id = %s;",
                    (follower_id,),
                )

                # 3. Increment followers_count for followed
                cursor.execute(
                    "UPDATE users SET followers_count = followers_count + 1 WHERE id = %s;",
                    (followed_id,),
                )

            # Atomic commit
            conn.commit()

            # Log activity in MongoDB (non-transactional across DBs, but PostgreSQL is ACID)
            mongo_logger.log_activity(
                {
                    "action": "follow",
                    "follower_id": str(follower_id),
                    "followed_id": str(followed_id),
                }
            )

            return True, "Followed successfully."
        except psycopg2.IntegrityError:
            conn.rollback()
            return False, "Already following or user does not exist."
        except Exception as e:
            conn.rollback()
            return False, f"Error during follow transaction: {e}"
        finally:
            db.put_connection(conn)


user_service = UserService()
