# Workspace 2 and the recorded response repair

November 26, 2026 (Eastern). This update follows the fall submission baseline in PR #12.

## Why the old page could remain visible

The optional real check ran before the frontend build. Its rejected first turn exited the launcher under `set -e`, so the build never ran. The old `run-local.sh` fallback served an existing `frontend/dist`. Both startup commands now use the same guarded launch path, build before the optional check and start the updated app even when that check reports failure. No failed check is labeled successful; no automatic retry is added. The default launch sends no inference.

## Recognizing the new layout

The owner workspace has a dark left navigation rail, business account area, published/draft/open-inquiry summary and focused editor. The footer in the rail says **Workspace 2**. Customer Inventory now uses the available width; requirements are collapsed until needed. Find my fit has a shorter heading and a dedicated conversation workspace. Original navigation labels and business functions are retained. At phone widths the rail becomes a horizontal navigation strip.

## Exact recorded AI failure

The supplied real response had a provider completion, valid budget/seat preferences and valid City Hybrid / Compact Hatch values. Application validation rejected it at `claims / unsupported_number / answer`: the model cited price, seats and comparison sources but omitted individual MPG, mileage and cargo source IDs. The `k` abbreviation already parsed correctly; the missing field citations caused the failure.

The sanitizer replay uses the same published fictional specifications and answer wording, with short fixture identifiers replacing record IDs. It reproduced the rejection before the fix. The resolver now checks specification values in an unambiguous named-vehicle specification block against **that exact already-cited published vehicle** and attaches the matching field/revision sources. It does not accept numbers from an unrelated vehicle or fill missing specifications. Wrong price, MPG, mileage and cargo values remain rejected. The provider instruction also requests every relevant field source in `source_ids`, with source identifiers kept out of the answer prose.

This is a bounded validation repair, not a semantic guarantee about every possible sentence. The original historical request remains rejected in the database. A sanitized offline replay is not a new live success. Current diagnostics report validation version **5**.

## Verification and next Mac check

Local checks: 86 backend tests, 12 frontend tests and production build. Seven new regressions cover the recorded response, wrong/missing/foreign evidence and actual shell startup behavior after an optional failure. Rendered workflows run in GitHub Actions with simulated Auth/Grok; no paid requests are made by those tests.

After pulling main, stop the existing server with Control+C and run `bash scripts/launch-showcase.sh`. Refresh Safari and sign in. Confirm the dark rail / Workspace 2 marker and diagnostics version 5 before another paid action. Use the customer inventory link, select Compact Hatch and City Hybrid, open Find my fit and deliberately submit one needs question. The optional three-turn `--practice --verify-live` check remains available, but it is not needed to load the design.

Budget reservations, historical counts and existing records remain preserved. The new default does not spend AI credit. The real retest must still be checked on the configured Mac. Existing report/slide files describe the PR #12 evidence baseline; this source update records the newer repair and test count until the final submission freeze.
