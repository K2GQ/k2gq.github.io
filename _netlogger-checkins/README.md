# NetLogger original check-in files — upload staging area

This folder is the collection point for the **original NetLogger check-in files**
used by the Roseland Amateur Radio Club net reports. Files placed here are
source records, **not website content**.

## Weekly upload procedure

1. Once each Tuesday net is complete, use NetLogger to save the **original
   CheckIns .log file**.
2. Open this directory on GitHub and choose **Add file → Upload files**.
3. Upload the saved .log without renaming or editing it, and commit the upload
   to the repository's `master` branch. The filename timestamp is UTC and is
   converted automatically to the corresponding Eastern net date.
4. **Do not upload a screenshot.** October 20, 2026, was the final
   screenshot-based report. October 27, 2026, and future nets are log-only.
5. After the automation workflow is approved and merged, it will validate the
   CheckIns file, regenerate the shared database, commit only the permitted
   fields, and explicitly request a GitHub Pages rebuild.
6. Check **Actions → NetLogger Check-in Database Update** for success, then
   open the Net Reports page and select the latest Tuesday date.

Only nonblank NetLogger rows count as check-ins. The original log stays in this
folder; the published JSON contains the nine approved fields only. Previously
approved manual historical records are preserved, and native logs take
precedence when available.

## Public repository notice

**This GitHub repository is public.** The leading underscore keeps this
directory out of the usual Jekyll website build, but it **does not make the
files private on GitHub**. Before uploading, ensure files do not contain
private phone numbers, email addresses, or other information that should not
be made public. If unredacted files contain private details, use a private
repository or private storage instead; let me know before uploading them.

Once the automation workflow is enabled, pushing a new .log file to `master` triggers the database update. A workflow failure must be corrected before the new net can be considered published.
