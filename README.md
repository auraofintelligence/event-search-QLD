# Event Search QLD

<!-- github-organisation:start -->

## Project links and history

- First substantive build: 28 February 2026.
- GitHub repository: [event-search-QLD](https://github.com/auraofintelligence/event-search-QLD).
- Public site: [visit the public site](https://auraofintelligence.github.io/event-search-QLD/).

## Related public projects

Each link below reflects an evidenced family, lineage or direct connection. This project has 15 relevant public connections.

### Australian law and civic navigation

- [aus-gov-2025](https://github.com/auraofintelligence/aus-gov-2025) - [public page](https://auraofintelligence.github.io/aus-gov-2025/) - shared tooling suite.
- [australian-law-2012-lukes-relevance](https://github.com/auraofintelligence/australian-law-2012-lukes-relevance) - [public page](https://auraofintelligence.github.io/australian-law-2012-lukes-relevance/) - shared tooling suite.
- [australian-legal-engine](https://github.com/auraofintelligence/australian-legal-engine) - shared tooling suite.
- [legal-memory-workbench](https://github.com/auraofintelligence/legal-memory-workbench) - [public page](https://auraofintelligence.github.io/legal-memory-workbench/) - shared tooling suite.
- [p4a_xyz](https://github.com/auraofintelligence/p4a_xyz) - [public page](https://auraofintelligence.github.io/p4a_xyz/) - shared tooling suite.
- [UN-world-days](https://github.com/auraofintelligence/UN-world-days) - [public page](https://auraofintelligence.github.io/UN-world-days/) - explicit cross-reference, shared tooling suite.

### Australian travel, opportunity and story atlases

- [australian-sire-story-forge](https://github.com/auraofintelligence/australian-sire-story-forge) - [public page](https://auraofintelligence.github.io/australian-sire-story-forge/) - shared tooling suite.
- [Australian-visa-activity-atlas](https://github.com/auraofintelligence/Australian-visa-activity-atlas) - [public page](https://auraofintelligence.github.io/Australian-visa-activity-atlas/) - shared tooling suite.
- [Australian-world-travel](https://github.com/auraofintelligence/Australian-world-travel) - [public page](https://auraofintelligence.github.io/Australian-world-travel/) - shared tooling suite.
- [global-founder-atlas](https://github.com/auraofintelligence/global-founder-atlas) - [public page](https://auraofintelligence.github.io/global-founder-atlas/) - shared tooling suite.
- [strange-but-true-desire-atlas](https://github.com/auraofintelligence/strange-but-true-desire-atlas) - [public page](https://auraofintelligence.github.io/strange-but-true-desire-atlas/) - shared tooling suite.
- [strange-but-true-travel-oracle](https://github.com/auraofintelligence/strange-but-true-travel-oracle) - [public page](https://auraofintelligence.github.io/strange-but-true-travel-oracle/) - shared tooling suite.

### Direct and other supported connections

- [gajra-earth-public-hub](https://github.com/auraofintelligence/gajra-earth-public-hub) - [public page](https://auraofintelligence.github.io/gajra-earth-public-hub/) - explicit cross-reference.

### Event and calendar tools

- [fishing-calendar](https://github.com/auraofintelligence/fishing-calendar) - shared tooling suite.
- [quandamooka-country-events-engine](https://github.com/auraofintelligence/quandamooka-country-events-engine) - [public page](https://auraofintelligence.github.io/quandamooka-country-events-engine/) - explicit cross-reference, shared tooling suite.

<!-- github-organisation:end -->

A static Greater South East Queensland event-triage page for finding university and public events related to AI, robotics, governance, law, public policy, emergency response and neighbouring topics.

**Public page:** <https://auraofintelligence.github.io/event-search-QLD/>

## Repository contents

- `index.html` - searchable event cards with browser-local saved and dismissed lists.
- `data/events.json` - the currently published event snapshot.
- `scraper.py` - a small collector for UQ event links and a narrow web-search fallback.
- `requirements.txt` - Python packages used by the collector.

## Use the public page

Open the public page or open `index.html` locally. Saved and dismissed event IDs are kept in the current browser's `localStorage`; there is no account or shared database.

## Refresh the data

From this repository folder:

```powershell
python -m pip install -r requirements.txt
python scraper.py
```

The script writes `data/events.json`. Review the resulting records before publishing them.

## Current limitations

The data is a discovery snapshot, not an authoritative calendar. The current collector treats all UQ results as a university dragnet and records the collection time in the `date` field rather than reliably extracting each event's scheduled date. Links, venues and event details can change or disappear, so confirm every event with its host page.

## Related public pages

- [Quandamooka Country Events Engine](https://auraofintelligence.github.io/quandamooka-country-events-engine/) - a separate source-led public event atlas focused on Quandamooka Country.
- [GAJRA Earth Public Hub](https://auraofintelligence.github.io/gajra-earth-public-hub/) - a neighbouring project that links events into a wider public participation pathway.

## Licence

See the [Strange But True Public Source Licence](LICENCE.md).
