from __future__ import annotations

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
            ORDER BY id
            """
        )

        rows = cursor.fetchall()

        conn.close()

        return [
            InstagramPost(
                url=row["post_url"],
                caption=row["caption"],
                post_date=row["post_date"],
                category=row["category"],
            )
            for row in rows
        ]

    def get_pending_posts(self) -> list[InstagramPost]:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM instagram_posts
            WHERE ai_processed = 0
            ORDER BY id
            """
        )

        rows = cursor.fetchall()

        conn.close()

        return [
            InstagramPost(
                url=row["post_url"],
                caption=row["caption"],
                post_date=row["post_date"],
                category=row["category"],
            )
            for row in rows
        ]

    def mark_processed(self, post_id: int) -> None:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE instagram_posts
            SET ai_processed = 1
            WHERE id = ?
            """,
            (post_id,),
        )

        conn.commit()
        conn.close()