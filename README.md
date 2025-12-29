# Games List Reviews - Many Players Edition

Complete database with comprehensive reviews for 199 local multiplayer games supporting many players (8+ simultaneous players).

## Overview

This repository contains detailed review summaries for games that support large player counts (8+ simultaneous local players). Each game has its own markdown file with:

- **Gameplay & Mechanics**: Detailed breakdown of core systems and controls
- **Fun Factor**: What critics and players enjoy about the game
- **Player Count Experience**: How the game performs with different group sizes
- **Overall Reception**: Critical scores, consensus, and recommendations
- **Sources**: Links to full reviews and metadata

## Interactive Visualizer

Browse and filter all games with the **[Interactive Game Browser](https://cschubiner.github.io/gamelist_manyplayers/)** hosted on GitHub Pages!

**Features:**
- Search games by name
- Filter by minimum player count (8-100+ players)
- Filter by minimum review score (0-100)
- Multi-select platform filtering (PC, PS4, Xbox, Nintendo Switch)
- Sort by name, review score, or player count
- View original game descriptions and pricing information

## Games Included

Complete review data for 199 games in `/reviews/` directory, including:

- Super Slime Arena, The Jackbox Party Pack (multiple editions)
- Mount Your Friends, PICO PARK, TowerClimb, Runbow
- Party Jousting, Regular Human Basketball, MageQuit
- Sea of Fatness, Photon Rush, Overlay, Stick Fight, and more
- Plus 183 additional games covering diverse multiplayer genres

See the **[Interactive Visualizer](https://cschubiner.github.io/gamelist_manyplayers/)** for the complete, sortable list of all 199 games.

## Review Methodology

Each review summary was compiled from multiple independent sources including:
- Professional gaming publications (GameSpot, IGN, Nintendo Life, etc.)
- Gaming community reviews (Metacritic, Steam)
- Specialized review outlets
- User feedback compilation

Reviews focus on:
- How well the game scales with player count
- Quality of local multiplayer experience
- Accessibility for different skill levels
- Value for parties and group gaming
- Longevity and replayability

## Key Findings

### Best for Large Groups (8+ players)
- **PICO PARK: Classic Edition** - Dynamic difficulty scaling up to 10 players
- **12 Orbits** - Designed specifically for up to 12 simultaneous players
- **The Jackbox Party Pack 4** - Up to 16 players with audience mode for thousands

### Best Solo-to-Group Games
- **Runbow** - Strong single-player content plus excellent multiplayer
- **TowerClimb** - Roguelike with local co-op support

### Party Game Winners
- **Mount Your Friends** - 95% Steam approval rating
- **Super Slime Arena** - Quirky charm despite limited content
- **Monumental Failure** - Excellent cooperative chaos

## Directory Structure

```
gamelist-reviews/
├── reviews/              # 199 markdown review files
├── data/                 # 199 JSON files with structured game data
├── docs/
│   └── index.html        # Interactive GitHub Pages visualizer
└── README.md
```

## Format

### Markdown Reviews (`/reviews/`)

Each review file contains:
- Gameplay & Mechanics section with detailed system breakdown
- Fun Factor section covering player experience
- Player Count Experience analysis
- Overall Reception with critical scores and consensus
- Sources with direct links to original reviews

### JSON Data Files (`/data/`)

Structured data for each game with:
- `name`: Game title
- `originalComment`: Description from source (gameslist.txt)
- `reviewScore`: 0-100 critical score
- `maxPlayers`: Maximum simultaneous players
- `platforms`: Array of platform names (PC, PS4, Xbox, Nintendo Switch, etc.)
- `price`: Listed price or "Free"/"Not specified"

Example:
```json
{
  "name": "Mount Your Friends",
  "originalComment": "Hot Seat weird multiplayer sporting event, up to 16 players offline, same screen (turn based)",
  "reviewScore": 90,
  "maxPlayers": 16,
  "platforms": ["PC", "Steam"],
  "price": "$4.99"
}
```

## Updates

Reviews were researched and compiled in December 2025. As games receive updates and new reviews are published, individual files may be updated to reflect the latest information.

## Contributing

This is a private repository maintained as a reference collection. Review files are based on published critical consensus and user reviews.

---

*Generated with Claude Code - Review research and markdown compilation*
