# Workspace 2 and the recorded response repair

November 26, 2026 (Eastern). This update follows the fall submission baseline in PR #12.

## Current citation handling — validation version 7

The latest real failed request (owner-reported request ID `11cbf5bb-9002-42dc-9c3a-9533e2a1bb87`) returned provider success and failed at `sources / unapproved_source / answer`. It used 4,756 tokens and took 2,072 ms. Its raw answer was not retained, so the exact marker cannot be reconstructed from that diagnostic. This is a different failure category from the earlier numeric rejection.

Version 6 incorrectly required a known single-bracket citation to be duplicated in `source_ids`, and treated a double-bracket citation to approved policy/knowledge as a scalar insertion with a missing value. Version 7 resolves known single, grouped and policy citations against the same published snapshot, collecting their canonical field/revision references. It does not resolve unknown references by guessing.

If a model's inline reference is unusable, ALL model prose is discarded. The application separately validates the structured preferences, declared sources and recommendations, then may deliver a revalidated server fact summary as `accepted_with_limits`, preserving the `sources / unapproved_source / answer` reason. Foreign declared references, fabricated needs, invalid recommendations and stale snapshots remain blocked. No unknown citation or unsupported warranty claim is displayed or recorded as accepted evidence. No retry is introduced.

Validation: 96 backend tests, 13 frontend tests and build pass locally. New regressions cover valid unlisted/grouped inline citations, approved knowledge markers, the exact reported rejection category recovering safely, and unchanged rejection of invalid structured data. The rendered workflow exercises normal policy citations and a limited source-failure response with mocked Auth/Grok. No live Grok call was made here. Read-only `GET /health` now shows `showcase_validation_version: 7` without signing in or making an AI call; this verifies which server code is loaded.

## Earlier delivery repair — validation version 6

The next manual request was again rejected at `claims / unsupported_number / answer`. Its exact model wording was not retained by the ordinary chat route, so the diagnostic alone cannot identify which quantity failed. The earlier recorded-response patch was insufficient for general model wording.

The shopping request now uses short per-request source IDs and asks the model to insert `[[S1]]` values. `backend/shopping_delivery.py` renders those values from the published source snapshot, maps citations back to the original field/revision IDs, and runs the existing validator. The model still interprets needs and writes the trade-off explanation. Provider requests contain explicit USD prices, never integer cents mislabeled as dollars.

For an `unsupported_number` prose failure only, the application discards ALL model answer/follow-up wording. After the structured preferences, references and recommendations passed checks, it builds and revalidates a server fact summary for the selected or eligible cited vehicles. The UI labels it **Confirmed listing summary**; evidence records **accepted_with_limits**, preserving the numeric rejection category and the source IDs actually delivered. The rejected numeric claim is never displayed, silently edited into a purportedly accepted model explanation, or saved as normal acceptance. Invalid needs/recommendations, foreign sources and stale publications still fail. No provider retry is introduced. The optional acceptance script stops on limited delivery and does not report full live success.

Validation: 93 backend tests, 13 frontend interaction tests and the production build pass locally. Regressions cover source insertion, wrong USD/MPG units, discarded numeric prose, continued preferences, source isolation, stale snapshots, limited UI/evidence labeling and no automatic retry. Rendered browser workflows run in CI with simulated Auth/Grok. No paid call was made in this repair environment; acceptance by real Grok on the configured Mac is still a separate check.

After pulling main, stop the running server with Control+C and run `bash scripts/launch-showcase.sh`. Refresh Safari. Under System status → Technical API diagnostics confirm `showcase_validation_version: 6`. Launch and refresh make no inference request. Historical rejected records remain unchanged.

## Why the old page could remain visible

The optional real check ran before the frontend build. Its rejected first turn exited the launcher under `set -e`, so the build never ran. The old `run-local.sh` fallback served an existing `frontend/dist`. Both startup commands now use the same guarded launch path, build before the optional check and start the updated app even when that check reports failure. No failed check is labeled successful; no automatic retry is added. The default launch sends no inference.

## Recognizing the new layout

The owner workspace has a dark left navigation rail, business account area, published/draft/open-inquiry summary and focused editor. The footer in the rail says **Workspace 2**. Customer Inventory now uses the available width; requirements are collapsed until needed. Find my fit has a shorter heading and a dedicated conversation workspace. Original navigation labels and business functions are retained. At phone widths the rail becomes a horizontal navigation strip.

## Exact recorded AI failure

The supplied real response had a provider completion, valid budget/seat preferences and valid City Hybrid / Compact Hatch values. Application validation rejected it at `claims / unsupported_number / answer`: the model cited price, seats and comparison sources but omitted individual MPG, mileage and cargo source IDs. The `k` abbreviation already parsed correctly; the missing field citations caused the failure.

The sanitizer replay uses the same published fictional specifications and answer wording, with short fixture identifiers replacing record IDs. It reproduced the rejection before the fix. The resolver now checks specification values in an unambiguous named-vehicle specification block against **that exact already-cited published vehicle** and attaches the matching field/revision sources. It does not accept numbers from an unrelated vehicle or fill missing specifications. Wrong price, MPG, mileage and cargo values remain rejected. The provider instruction also requests every relevant field source in `source_ids`, with source identifiers kept out of the answer prose.

This was a bounded version 5 repair, not a semantic guarantee about every possible sentence. The original historical request remains rejected in the database. A sanitized offline replay is not a new live success. The version 6 section above supersedes the delivery behavior below.

## Verification and next Mac check

Local checks: 86 backend tests, 12 frontend tests and production build. Seven new regressions cover the recorded response, wrong/missing/foreign evidence and actual shell startup behavior after an optional failure. Rendered workflows run in GitHub Actions with simulated Auth/Grok; no paid requests are made by those tests.

After pulling main, stop the existing server with Control+C and run `bash scripts/launch-showcase.sh`. Refresh Safari and sign in. Confirm the dark rail / Workspace 2 marker and diagnostics version 5 before another paid action. Use the customer inventory link, select Compact Hatch and City Hybrid, open Find my fit and deliberately submit one needs question. The optional three-turn `--practice --verify-live` check remains available, but it is not needed to load the design.

Budget reservations, historical counts and existing records remain preserved. The new default does not spend AI credit. The real retest must still be checked on the configured Mac. Existing report/slide files describe the PR #12 evidence baseline; this source update records the newer repair and test count until the final submission freeze.
