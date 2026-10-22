
import datetime
import html
import requests
from bs4 import BeautifulSoup

USERNAME = "Vedanti-0417"
OUTPUT_FILE = "contrib-heatmap.svg"

URL = f"https://github.com/users/{USERNAME}/contributions"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html"
}

COLORS = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353"
]

CELL = 11
GAP = 3
STEP = CELL + GAP
LEFT = 38
TOP = 38

def main():
    print(f"Fetching contributions for {USERNAME}...")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # GitHub's contribution calendar uses td elements.
    cells = soup.select("td[data-date][data-level]")

    if not cells:
        with open("github_response.html", "w", encoding="utf-8") as file:
            file.write(response.text)

        raise RuntimeError(
            "Contribution cells nahi mile. "
            "github_response.html save hui hai. "
            "Use inspect karne ke liye mujhe error bhejo."
        )

    contributions = {}

    for cell in cells:
        date_text = cell.get("data-date")
        level_text = cell.get("data-level", "0")

        try:
            day = datetime.date.fromisoformat(date_text)
            level = max(0, min(4, int(level_text)))
            contributions[day] = level
        except (ValueError, TypeError):
            continue

    if not contributions:
        raise RuntimeError("Valid contribution dates nahi mili.")

    first_day = min(contributions)
    last_day = max(contributions)

    # GitHub calendar columns represent weeks, starting Sunday.
    first_day -= datetime.timedelta(
        days=(first_day.weekday() + 1) % 7
    )

    total_days = (last_day - first_day).days + 1
    weeks = (total_days + 6) // 7

    width = LEFT + weeks * STEP + 8
    height = TOP + 7 * STEP + 20

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" '
        'rx="8" fill="#0d1117"/>',
        '<text x="8" y="20" fill="#e6edf3" '
        'font-size="13" font-family="Arial" '
        'font-weight="bold">GitHub Contributions</text>'
    ]

    # Month labels
    previous_month = None
    day = first_day

    while day <= last_day:
        if day.month != previous_month:
            week = (day - first_day).days // 7
            x = LEFT + week * STEP

            parts.append(
                f'<text x="{x}" y="{TOP - 8}" '
                f'fill="#8b949e" font-size="9" '
                f'font-family="Arial">'
                f'{html.escape(day.strftime("%b"))}</text>'
            )
            previous_month = day.month

        day += datetime.timedelta(days=1)

    # Weekday labels
    for weekday, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = TOP + weekday * STEP + 9

        parts.append(
            f'<text x="4" y="{y}" fill="#8b949e" '
            f'font-size="9" font-family="Arial">'
            f'{label}</text>'
        )

    # Draw the contribution squares
    day = first_day

    while day <= last_day:
        week = (day - first_day).days // 7
        weekday = (day.weekday() + 1) % 7

        level = contributions.get(day, 0)

        x = LEFT + week * STEP
        y = TOP + weekday * STEP

        parts.append(
            f'<rect x="{x}" y="{y}" '
            f'width="{CELL}" height="{CELL}" '
            f'rx="2" fill="{COLORS[level]}">'
            f'<title>{day.isoformat()} - '
            f'Contribution level {level}</title>'
            f'</rect>'
        )

        day += datetime.timedelta(days=1)

    parts.append("</svg>")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(parts))

    print(f"Success! Created {OUTPUT_FILE}")
    print(f"Contribution days loaded: {len(contributions)}")
    print("Open contrib-heatmap.svg in your browser.")

if __name__ == "__main__":
    main()
