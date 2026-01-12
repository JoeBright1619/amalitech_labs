import uuid
from src.services.user_service import user_service
from src.database.postgres_db import db


def test_follow_transaction_atomicity():
    # 1. Create two test users
    u1_id = user_service.create_user(
        f"test_{uuid.uuid4().hex[:8]}", "test1@example.com"
    )
    u2_id = user_service.create_user(
        f"test_{uuid.uuid4().hex[:8]}", "test2@example.com"
    )

    assert u1_id is not None
    assert u2_id is not None

    # 2. Perform follow
    success, msg = user_service.follow_user(u1_id, u2_id)
    assert success is True

    # 3. Verify PostgreSQL counts
    conn = db.get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT following_count FROM users WHERE id = %s;", (u1_id,))
        u1_following = cursor.fetchone()[0]

        cursor.execute("SELECT followers_count FROM users WHERE id = %s;", (u2_id,))
        u2_followers = cursor.fetchone()[0]

        cursor.execute(
            "SELECT count(*) FROM followers WHERE follower_id = %s AND followed_id = %s;",
            (u1_id, u2_id),
        )
        follow_record_exists = cursor.fetchone()[0] == 1

    db.put_connection(conn)

    assert u1_following == 1
    assert u2_followers == 1
    assert follow_record_exists is True


def test_prevent_self_follow():
    u_id = user_service.create_user(f"test_{uuid.uuid4().hex[:8]}", "test3@example.com")
    success, msg = user_service.follow_user(u_id, u_id)
    assert success is False
    assert "Cannot follow yourself" in msg
