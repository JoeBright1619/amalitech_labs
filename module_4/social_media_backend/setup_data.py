from src.services.user_service import user_service
from src.services.post_service import post_service
from src.database.postgres_db import db


def seed_data(num_users=50, posts_per_user=10, follows_per_user=5):
    print(f"Seeding {num_users} users...")
    user_ids = []
    for i in range(num_users):
        uid = user_service.create_user(f"user_{i}", f"user_{i}@example.com")
        if uid:
            user_ids.append(uid)

    print(f"Creating {num_users * posts_per_user} posts...")
    for uid in user_ids:
        for j in range(posts_per_user):
            post_service.create_post(
                uid,
                f"Hello from user {uid}, post number {j}",
                {"location": "Accra", "tags": ["amaliTech", "coding"]},
            )

    import random

    print("Creating follows...")
    for uid in user_ids:
        # Each user follows random unique users
        to_follow = random.sample(user_ids, min(follows_per_user, len(user_ids)))
        for target_id in to_follow:
            if uid != target_id:
                user_service.follow_user(uid, target_id)

    print("Seeding complete.")


if __name__ == "__main__":
    # Ensure tables exist
    import os

    schema_path = os.path.join(os.path.dirname(__file__), "src", "models", "schema.sql")
    db.init_db(schema_path)
    seed_data()
