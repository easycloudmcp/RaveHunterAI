from database.database import get_connection
from collectors.instagram.models import InstagramPost


class InstagramRepository:

    def save_post(self, post: InstagramPost) -> int:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO instagram_posts
            (
                post_url,
                caption,
                post_date,
                category
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                post.url,
                post.caption,
                post.post_date,
                post.category,
            ),
        )

        conn.commit()

        post_id = cursor.lastrowid

        conn.close()

        return post_id

    def get_posts(self) -> list[InstagramPost]:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM instagram_posts
            ORDER BY id DESC
            """
        )

        rows = cursor.fetchall()

        conn.close()

        posts = []

        for row in rows:
            posts.append(
                InstagramPost(
                    url=row["post_url"],
                    caption=row["caption"],
                    post_date=row["post_date"],
                    category=row["category"],
                )
            )

        return posts