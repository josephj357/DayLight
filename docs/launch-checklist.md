# Launch checklist (for the maintainer)

This is the post-build seeding plan — the "one focused afternoon" that
decides whether DayLight reaches 50 stars or 5,000.

The premise: DayLight is a gift. There's no launch marketing budget. The
only way it spreads is through one focused round of distribution, then
letting the project find its people.

## Before launch — quality bar

Confirm these one more time:

- [ ] `bash scripts/seed.sh` runs end-to-end against a clean clone.
- [ ] `cd src/web && npm install && npm run dev` renders the FL-23 view
      with mocks even when the backend is down.
- [ ] `pytest tests/` is green.
- [ ] README screenshot/GIF placeholders are replaced with real assets.
- [ ] `LICENSE` is AGPL-3.0 (not GPL).
- [ ] All `# TODO: verify` markers in `config/districts/fl-23.yml` are
      either resolved or explicitly acknowledged in the README as v1
      caveats.
- [ ] `docs/methodology.md` is reviewed and you (the maintainer) are
      comfortable defending every constant in §3.
- [ ] No `.env` file in `git status`. Run `git ls-files | grep -i env`
      and confirm only `.env.example` shows up.

## Launch day, 3-hour seeding plan

Pick a Tuesday or Wednesday morning. Avoid Mondays (too much noise),
Fridays (low engagement), and weekends.

### Hour 1 — set the table

- [ ] **Show HN post.** Title format (Show HN is reviewed for tone):
      `Show HN: DayLight – open-source voter transparency, starting with one Florida district`
      Body: 4-6 sentences. What it does, who built it (gift framing), what's
      genuinely novel (down-ballot + AI synthesis), how to fork it. Link
      to the repo. Don't include external blog posts or signups — HN
      reviewers downrank promotional posts.

- [ ] **Reddit cross-posts** (post to each, don't crosspost a link — each
      community wants a different framing):
   - r/civictech: emphasize the methodology and forking story.
   - r/programming: emphasize the architecture (config-extensible YAML,
     AGPL, AI synthesis layer).
   - r/florida: emphasize the FL-23 down-ballot coverage.
   - r/sanders, r/Conservative, r/moderatepolitics: emphasize the
     neutrality contract. Same post in each — the test is whether all
     three communities receive it well.

- [ ] **Awesome-list PRs.** Submit to:
   - github.com/topics/awesome-civictech
   - github.com/sindresorhus/awesome (if it fits)
   - github.com/awesome-foss/awesome-civictech
   Each one is a 5-minute PR adding a single line.

### Hour 2 — journalism + civic networks

- [ ] **5 cold emails to journalists.** Subject:
      `Open-source voter transparency tool — thought you might find this useful`
      Body: 3 sentences. What DayLight is. Who built it (gift framing,
      no PR pitch). Link. End with "happy to chat if useful; equally
      happy if you just take it and run."

      Targets (verify current beat and email before sending):
      - ProPublica election-data reporter
      - The Intercept national-security/influence reporter
      - 404 Media (anyone covering open-source civic tech)
      - Wired US politics/tech crossover desk
      - Your local newspaper's investigative desk (the Sun Sentinel for FL-23)

- [ ] **Code for America brigade outreach.** Find brigades in your state
      via codeforamerica.org/brigades. Drop a note: "Built a thing,
      thought your brigade might find it useful for local races." Don't
      ask for anything. They have networks; if they like it, they'll share.

- [ ] **Civic-tech funders, as a notification, not a pitch.** Light-touch
      DMs or emails to:
   - Knight Foundation civic-tech program officer
   - Democracy Fund (Pierre Omidyar)
   - Mozilla Open Source Support team
   "Built this as a gift, AGPL, no funding ask. If it's useful to your
   network, please share."

### Hour 3 — social and personal networks

- [ ] **X/Twitter announcement thread.** 5-7 tweets. First tweet: what it
      is, in 1 sentence + link. Subsequent tweets: features (down-ballot,
      methodology, neutrality, AI synthesis, fork-your-district).
      Last tweet: explicit "this is a gift, AGPL, I'm not maintaining it,
      come help."

      Tag thoughtfully (don't spam): @lessig, @AnnaGifty, @balajis,
      @vitalik (funds civic public goods), @ProPublica, @opensecretsdc.

- [ ] **Mastodon / Bluesky cross-posts.** Civic-tech audiences live on
      both. Adapt the Twitter thread for each platform's culture.

- [ ] **Personal LinkedIn post.** Different audience than the above —
      focus on the "I built this in my spare time as a gift" narrative,
      not the technical features.

- [ ] **Tell three people directly.** Not for the broadcast — for the
      "this person cares about this kind of thing and might pick it up"
      effect. Reach out to civic-tech folks you actually know.

## Critical rules

1. **Post once per channel, not three times.** The project is a gift.
   Spamming undermines the framing.
2. **Don't argue in comments.** If someone says it's biased, ask them to
   open a `[Correction]` issue with sources. Don't relitigate.
3. **Don't promise maintenance you won't deliver.** If you said in the
   README you're stepping back, act like it. Let the community find a
   maintainer.
4. **Watch for partisan amplification with caution.** If only one side
   shares it loudly, the project's neutrality reputation is damaged.
   Both sides liking it is the success criterion.

## Week-two follow-up

About a week after launch, check:

- [ ] GitHub stars, forks, issues, watchers.
- [ ] HN post karma + comment quality.
- [ ] Any inbound journalist replies.
- [ ] Whether a community maintainer has stepped up via
      `[Maintainer Application]` issues.

If a maintainer steps up, hand off cleanly: invite to repo, add to README,
move yourself to "founder, stepping back" framing.

If no maintainer has stepped up but engagement is strong, leave it open
and revisit in 30 days.

If engagement is silent, the project still did its job — the artifact
exists, the methodology is in the world, and someone in 2027 will
rediscover and extend it. That counts as success for a gift.
