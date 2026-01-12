import json
from src.database.postgres_db import db
from src.database.redis_cache import redis_cache


class FeedService:
    @staticmethod
    def get_feed(user_id, page=1, limit=10):
        """
        Generates a user's feed with posts from people they follow.
        Uses Redis caching and complex SQL (CTEs + Window Functions).
        """
        cache_key = f"feed:{user_id}:p{page}"

        # 1. Try Cache
        cached_feed = redis_cache.get_cache(cache_key)
        if cached_feed:
            print(f"Feed for {user_id} served from Redis.")
            return json.loads(cached_feed)

        # 2. SQL Query with CTE and Window Function
        conn = db.get_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cursor:
                # offset = (page - 1) * limit
                start_row = (page - 1) * limit + 1
                end_row = page * limit

                query = """
                WITH followed_users AS (
                    SELECT followed_id 
                    FROM followers 
                    WHERE follower_id = %s
                ),
                paged_posts AS (
                    SELECT 
                        p.id, 
                        p.user_id, 
                        u.username,
                        p.content, 
                        p.metadata, 
                        p.created_at,
                        ROW_NUMBER() OVER (ORDER BY p.created_at DESC) as row_num
                    FROM posts p
                    JOIN followed_users f ON p.user_id = f.followed_id
                    JOIN users u ON p.user_id = u.id
                )
                SELECT id, user_id, username, content, metadata, created_at
                FROM paged_posts
                WHERE row_num BETWEEN %%s AND %%s;
                """
                # Note: %%s for escaping % in python string if needed,
                # but standard %s is fine for parameters.
                # Actually, in a multiline string it's fine.
                cursor.execute(query, (user_id, start_row, end_row))

                rows = cursor.fetchall()
                feed = []
                for row in rows:
                    feed.append(
                        {
                            "post_id": str(row[0]),
                            "user_id": str(row[1]),
                            "username": row[2],
                            "content": row[3],
                            "metadata": row[4],
                            "created_at": row[5].isoformat() if row[5] else None,
                        }
                    )

                # 3. Cache the result for 5 minutes (300s)
                redis_cache.set_cache(cache_key, json.dumps(feed), ex=300)

                return feed

        except Exception as e:
            print(f"Error generating feed: {e}")
            return []
        finally:
            db.put_connection(conn)


feed_service = FeedService()
