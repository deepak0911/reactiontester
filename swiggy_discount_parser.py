#!/usr/bin/env python3
"""
Swiggy Restaurant Discount Parser

Fetches restaurant feed data from Swiggy's public API and analyzes
discount offers to find the most common discount type.

Usage:
    python3 swiggy_discount_parser.py [--lat LAT] [--lng LNG] [--sample]

Examples:
    python3 swiggy_discount_parser.py                          # Default: Bangalore
    python3 swiggy_discount_parser.py --lat 28.7041 --lng 77.1025  # Delhi
    python3 swiggy_discount_parser.py --sample                 # Use sample data
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from collections import Counter


SWIGGY_API_URL = (
    "https://www.swiggy.com/dapi/restaurants/list/v5"
    "?lat={lat}&lng={lng}"
    "&is-seo-homepage-enabled=true"
    "&page_type=DESKTOP_WEB_LISTING"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.swiggy.com/",
    "Origin": "https://www.swiggy.com",
}

# Sample API response snippet for offline testing / demo
SAMPLE_RESPONSE = {
    "data": {
        "cards": [
            {
                "card": {
                    "card": {
                        "@type": "type.googleapis.com/swiggy.gandalf.widgets.v2.GridWidget",
                        "gridElements": {
                            "infoWithStyle": {
                                "restaurants": [
                                    {
                                        "info": {
                                            "id": "1001",
                                            "name": "Pizza Paradise",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "60% OFF",
                                                "subHeader": "UPTO ₹120",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1002",
                                            "name": "Burger Barn",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "₹150 OFF",
                                                "subHeader": "ABOVE ₹349",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1003",
                                            "name": "Dosa House",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "20% OFF",
                                                "subHeader": "UPTO ₹50",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1004",
                                            "name": "Chinese Wok",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "60% OFF",
                                                "subHeader": "UPTO ₹120",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1005",
                                            "name": "Biryani Blues",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "₹100 OFF",
                                                "subHeader": "ABOVE ₹249",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1006",
                                            "name": "Tandoori Nights",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "ITEMS AT ₹179",
                                                "subHeader": "",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1007",
                                            "name": "Salad Story",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "FREE DELIVERY",
                                                "subHeader": "",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1008",
                                            "name": "Ice Cream Co",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "60% OFF",
                                                "subHeader": "UPTO ₹120",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1009",
                                            "name": "South Indian Cafe",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "20% OFF",
                                                "subHeader": "UPTO ₹50",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1010",
                                            "name": "Noodle Bar",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "₹100 OFF",
                                                "subHeader": "ABOVE ₹249",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1011",
                                            "name": "Chai Point",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "60% OFF",
                                                "subHeader": "UPTO ₹120",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1012",
                                            "name": "Wrap Station",
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1013",
                                            "name": "Momos Express",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "₹150 OFF",
                                                "subHeader": "ABOVE ₹349",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1014",
                                            "name": "Cake Walk",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "FLAT ₹100 OFF",
                                                "subHeader": "",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1015",
                                            "name": "Pasta Place",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "60% OFF",
                                                "subHeader": "UPTO ₹120",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1016",
                                            "name": "Kebab King",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "20% OFF",
                                                "subHeader": "UPTO ₹50",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1017",
                                            "name": "Smoothie Bowl",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "₹100 OFF",
                                                "subHeader": "ABOVE ₹249",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1018",
                                            "name": "Taco Bell",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "60% OFF",
                                                "subHeader": "UPTO ₹120",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1019",
                                            "name": "Sandwich Hub",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "₹150 OFF",
                                                "subHeader": "ABOVE ₹349",
                                            },
                                        }
                                    },
                                    {
                                        "info": {
                                            "id": "1020",
                                            "name": "Coffee House",
                                            "aggregatedDiscountInfoV3": {
                                                "header": "FREE DELIVERY",
                                                "subHeader": "",
                                            },
                                        }
                                    },
                                ]
                            }
                        },
                    }
                }
            }
        ]
    }
}


def fetch_swiggy_data(lat: float, lng: float) -> dict:
    """Fetch restaurant listing data from the Swiggy API."""
    url = SWIGGY_API_URL.format(lat=lat, lng=lng)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        print(
            "Swiggy may be blocking automated requests. "
            "Try using --sample for a demo, or run from a different network.",
            file=sys.stderr,
        )
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        print("Try using --sample for a demo run.", file=sys.stderr)
        sys.exit(1)


def extract_restaurants(data: dict) -> list[dict]:
    """Extract restaurant info objects from the Swiggy API response.

    The API response contains multiple 'cards'. Restaurant listings are
    found inside cards that have a GridWidget with an 'infoWithStyle'
    element containing a 'restaurants' array.
    """
    restaurants = []
    cards = data.get("data", {}).get("cards", [])
    for card in cards:
        inner = card.get("card", {}).get("card", {})

        # Direct restaurant list in GridWidget
        grid = inner.get("gridElements", {})
        info_style = grid.get("infoWithStyle", {})
        rest_list = info_style.get("restaurants", [])
        for r in rest_list:
            info = r.get("info", {})
            if info:
                restaurants.append(info)

        # Some responses nest restaurants under groupedCard -> cardGroupMap
        grouped = inner.get("groupedCard", {})
        card_group_map = grouped.get("cardGroupMap", {})
        for _key, group in card_group_map.items():
            for sub_card in group.get("cards", []):
                sub_inner = sub_card.get("card", {}).get("card", {})
                sub_grid = sub_inner.get("gridElements", {})
                sub_style = sub_grid.get("infoWithStyle", {})
                for r in sub_style.get("restaurants", []):
                    info = r.get("info", {})
                    if info:
                        restaurants.append(info)

    return restaurants


def extract_discounts(restaurants: list[dict]) -> list[dict]:
    """Extract discount information from restaurant info objects.

    Returns a list of dicts with keys: restaurant_name, header, subHeader, full_discount.
    """
    discounts = []
    for rest in restaurants:
        name = rest.get("name", "Unknown")
        discount_info = rest.get("aggregatedDiscountInfoV3")
        if not discount_info:
            # Also check older API field names
            discount_info = rest.get("aggregatedDiscountInfoV2")
        if not discount_info:
            discount_info = rest.get("aggregatedDiscountInfo")

        if discount_info:
            header = discount_info.get("header", "")
            sub_header = discount_info.get("subHeader", "")
            discount_tag = discount_info.get("discountTag", "")

            # Build the full discount string
            parts = [p for p in [header, sub_header] if p]
            full_discount = " | ".join(parts) if len(parts) > 1 else (parts[0] if parts else "")

            discounts.append({
                "restaurant_name": name,
                "header": header,
                "sub_header": sub_header,
                "discount_tag": discount_tag,
                "full_discount": full_discount,
            })
    return discounts


def analyze_discounts(discounts: list[dict]) -> None:
    """Analyze and print discount frequency statistics."""
    if not discounts:
        print("No discounts found in the restaurant feed.")
        return

    total_restaurants_with_discounts = len(discounts)

    # Count by full discount string (header + subHeader combined)
    full_counter = Counter(d["full_discount"] for d in discounts)

    # Count by header only (the primary discount type)
    header_counter = Counter(d["header"] for d in discounts if d["header"])

    print("=" * 65)
    print("  SWIGGY RESTAURANT DISCOUNT ANALYSIS")
    print("=" * 65)
    print(f"\nTotal restaurants with discounts: {total_restaurants_with_discounts}")

    # Most common full discount
    print("\n--- Most Common Discounts (Full: header + subHeader) ---\n")
    print(f"  {'Rank':<6}{'Discount':<35}{'Count':<8}{'%':<8}")
    print(f"  {'-'*5:<6}{'-'*33:<35}{'-'*5:<8}{'-'*5:<8}")
    for rank, (discount, count) in enumerate(full_counter.most_common(10), 1):
        pct = (count / total_restaurants_with_discounts) * 100
        print(f"  {rank:<6}{discount:<35}{count:<8}{pct:.1f}%")

    # Most common header (primary discount type)
    print("\n--- Most Common Discount Types (Header Only) ---\n")
    print(f"  {'Rank':<6}{'Discount Type':<25}{'Count':<8}{'%':<8}")
    print(f"  {'-'*5:<6}{'-'*23:<25}{'-'*5:<8}{'-'*5:<8}")
    for rank, (header, count) in enumerate(header_counter.most_common(10), 1):
        pct = (count / total_restaurants_with_discounts) * 100
        print(f"  {rank:<6}{header:<25}{count:<8}{pct:.1f}%")

    # The winner
    most_common_full = full_counter.most_common(1)[0]
    most_common_header = header_counter.most_common(1)[0]

    print("\n" + "=" * 65)
    print(f"  MOST COMMON DISCOUNT: {most_common_full[0]}")
    print(f"  Seen on {most_common_full[1]} of {total_restaurants_with_discounts} restaurants "
          f"({most_common_full[1]/total_restaurants_with_discounts*100:.1f}%)")
    print(f"\n  MOST COMMON DISCOUNT TYPE: {most_common_header[0]}")
    print(f"  Seen on {most_common_header[1]} of {total_restaurants_with_discounts} restaurants "
          f"({most_common_header[1]/total_restaurants_with_discounts*100:.1f}%)")
    print("=" * 65)

    # Per-restaurant detail
    print("\n--- Per-Restaurant Discount Details ---\n")
    print(f"  {'Restaurant':<25}{'Discount':<40}")
    print(f"  {'-'*23:<25}{'-'*38:<40}")
    for d in discounts:
        name = d["restaurant_name"][:23]
        disc = d["full_discount"][:38]
        print(f"  {name:<25}{disc:<40}")


def main():
    parser = argparse.ArgumentParser(
        description="Parse Swiggy restaurant feeds and find the most common discount."
    )
    parser.add_argument(
        "--lat", type=float, default=12.9351929,
        help="Latitude for restaurant search (default: Bangalore)",
    )
    parser.add_argument(
        "--lng", type=float, default=77.62448069999999,
        help="Longitude for restaurant search (default: Bangalore)",
    )
    parser.add_argument(
        "--sample", action="store_true",
        help="Use built-in sample data instead of fetching from the API",
    )
    parser.add_argument(
        "--json-file", type=str, default=None,
        help="Path to a local JSON file with Swiggy API response data",
    )

    args = parser.parse_args()

    # Get data
    if args.json_file:
        print(f"Loading data from file: {args.json_file}")
        with open(args.json_file) as f:
            data = json.load(f)
    elif args.sample:
        print("Using built-in sample data for demo...")
        data = SAMPLE_RESPONSE
    else:
        print(f"Fetching restaurant data from Swiggy (lat={args.lat}, lng={args.lng})...")
        data = fetch_swiggy_data(args.lat, args.lng)

    # Extract restaurants
    restaurants = extract_restaurants(data)
    print(f"Found {len(restaurants)} restaurants in feed.\n")

    if not restaurants:
        print("No restaurants found. The API response structure may have changed.")
        print("Try --sample for a demo, or save the API response to a file and use --json-file.")
        sys.exit(1)

    # Extract and analyze discounts
    discounts = extract_discounts(restaurants)
    analyze_discounts(discounts)


if __name__ == "__main__":
    main()
