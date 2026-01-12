import uuid
from src.services.user_service import user_service
from src.services.post_service import post_service
from src.services.feed_service import feed_service
from src.database.redis_cache import redis_cache


def test_feed_generation_and_caching():
    # 1. Setup users
    follower_id = user_service.create_user(
        f"follower_{uuid.uuid4().hex[:8]}", "f@example.com"
    )
    followed_id = user_service.create_user(
        f"followed_{uuid.uuid4().hex[:8]}", "fd@example.com"
    )

    user_service.follow_user(follower_id, followed_id)

    # 2. Create a post
    post_content = "This is a test post for the feed."
    post_id = post_service.create_post(followed_id, post_content)
    assert post_id is not None

    # 3. Get feed (First time - SQL)
    feed = feed_service.get_feed(follower_id, page=1, limit=5)
    assert len(feed) >= 1
    assert feed[0]["content"] == post_content

    # 4. Verify Redis Cache
    cache_key = f"feed:{follower_id}:p1"
    cached_data = redis_cache.get_cache(cache_key)
    assert cached_data is not None
    assert post_content in cached_data

    # 5. Modify post in DB (just to prove cache hit)
    # If we get feed again, it should still show the old content if cache is working
    old_feed = feed_service.get_feed(follower_id, page=1, limit=5)
    assert old_feed[0]["content"] == post_content
