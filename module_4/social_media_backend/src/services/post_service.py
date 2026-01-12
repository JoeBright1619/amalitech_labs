from src.database.postgres_db import db
from src.database.mongo_logger import mongo_logger


class PostService:
    @staticmethod
    def create_post(user_id, content, metadata=None):
        """
        Creates a post with JSONB metadata.
        """
        if metadata is None:
            metadata = {}

        conn = db.get_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO posts (user_id, content, metadata)
                    VALUES (%s, %s, %s)
                    RETURNING id, created_at;
                """
                # psycopg2 handles dict to JSON conversion for JSONB if passed as a string or using Json wrapper
                from psycopg2.extras import Json

                cursor.execute(query, (user_id, content, Json(metadata)))
                result = cursor.fetchone()
                post_id = result[0]

            conn.commit()

            # Log activity in MongoDB
            mongo_logger.log_activity(
                {
                    "action": "post_created",
                    "user_id": str(user_id),
                    "post_id": str(post_id),
                    "has_metadata": bool(metadata),
                }
            )

            return post_id
        except Exception as e:
            print(f"Error creating post: {e}")
            conn.rollback()
            return None
        finally:
            db.put_connection(conn)

    @staticmethod
    def create_comment(post_id, user_id, content):
        conn = db.get_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO comments (post_id, user_id, content)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """
                cursor.execute(query, (post_id, user_id, content))
                comment_id = cursor.fetchone()[0]
            conn.commit()

            # Log activity in MongoDB
            mongo_logger.log_activity(
                {
                    "action": "comment_created",
                    "user_id": str(user_id),
                    "post_id": str(post_id),
                    "comment_id": str(comment_id),
                }
            )

            return comment_id
        except Exception as e:
            print(f"Error creating comment: {e}")
            conn.rollback()
            return None
        finally:
            db.put_connection(conn)


post_service = PostService()
