import sys

from collectors.instagram import InstagramCollector


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "python -m collectors.instagram.test_instagram "
            "https://www.instagram.com/account/"
        )
        raise SystemExit(1)

    profile_url = sys.argv[1]

    posts = InstagramCollector(profile_url).collect(limit=12)

    print(f"\nParsed {len(posts)} Instagram posts.\n")

    for number, post in enumerate(posts, start=1):
        print(f"{number:02}. {post.url}")
        print(f"    Published: {post.published_at or 'Not found'}")
        print(f"    Image    : {'Yes' if post.image_url else 'No'}")

        caption_preview = post.caption.replace("\n", " ").strip()

        if len(caption_preview) > 180:
            caption_preview = caption_preview[:177] + "..."

        print(f"    Caption  : {caption_preview or 'Not found'}")
        print()


if __name__ == "__main__":
    main()