from src.database.postgres_db import db


def run_analysis(user_id):
    conn = db.get_connection()
    if not conn:
        return

    query = """
    EXPLAIN ANALYZE
    WITH followed_users AS (
        SELECT followed_id 
        FROM followers 
        WHERE follower_id = %s
    ),
    paged_posts AS (
        SELECT 
            p.id, 
            p.user_id, 
            p.content, 
            p.metadata, 
            p.created_at,
            ROW_NUMBER() OVER (ORDER BY p.created_at DESC) as row_num
        FROM posts p
        JOIN followed_users f ON p.user_id = f.followed_id
    )
    SELECT id, user_id, content, metadata, created_at
    FROM paged_posts
    WHERE row_num BETWEEN 1 AND 10;
    """

    try:
        with conn.cursor() as cursor:
            # First run without optimization (though some indexes exist from schema.sql)
            print("--- Performance Analysis (Before Additional Optimization) ---")
            cursor.execute(query, (user_id,))
            plan = cursor.fetchall()
            for line in plan:
                print(line[0])

            # Adding Composite B-Tree Index
            print(
                "\n--- Adding Composite B-Tree Index: followers(follower_id, followed_id) ---"
            )
            # Note: This is actually already a PK in schema.sql,
            # but let's add one on posts(user_id, created_at DESC) which is crucial for feeds.
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_posts_composite_user_date ON posts(user_id, created_at DESC);"
            )
            conn.commit()

            print("\n--- Performance Analysis (After Composite Index on Posts) ---")
            cursor.execute(query, (user_id,))
            plan = cursor.fetchall()
            for line in plan:
                print(line[0])

    except Exception as e:
        print(f"Error during analysis: {e}")
    finally:
        db.put_connection(conn)


if __name__ == "__main__":
    # Use a likely user_id from seeding (or just a placeholder if not found)
    # We should search for a user first
    conn = db.get_connection()
    user_id = None
    if conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users LIMIT 1;")
            row = cursor.fetchone()
            if row:
                user_id = row[0]
        db.put_connection(conn)

    if user_id:
        run_analysis(user_id)
    else:
        print("No users found. Please run setup_data.py first.")
