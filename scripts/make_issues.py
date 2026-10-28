#!/usr/bin/env python3
"""Create GitHub issues on Bilal140202/myang-studio as the todo/QA tracker for the
procrastination long-form video (v2.0.0). Token from GITHUB_TOKEN env."""
import json, os, sys, urllib.request

REPO = "Bilal140202/myang-studio"
TOKEN = os.environ["GITHUB_TOKEN"]

ISSUES = [
 ("[ENGINE] mega-shot audit: choose best backend for photo-led 16:9 documentary",
  "Audit the full mega-shot library and pick the engine for the 12+ min procrastination video.\n\n"
  "Decision record:\n- Backend candidates: footage / canvas2d / threejs / blender / ai-image\n"
  "- Chosen: **footage template (stills.js Ken Burns + 2.5D parallax)** — 'fast (download+extract)', best for real archival/documentary photos, per-scene cached render\n"
  "- Local images wired via `search: { file, author, license }` -> license book (giay_phep.json + GHI_CONG.md)\n"
  "- 16:9 1920x1080, MS_ENCODER=x264 (no GPU in sandbox)\n\nQA: engine decision recorded in docs/engine-decision.md"),
 ("[TODO] Research desk: sourced facts for 'How to stop procrastination'",
  "nghien_cuu.md with 20+ facts, each with source (Steel 2007 meta-analysis, Pychyl/Sirois emotion-regulation, "
  "Ariely & Wertenbroch deadlines, Gollwitzer implementation intentions, Wohl self-forgiveness, Dai & Milkman fresh-start, TMT formula). QA: every on-screen number must exist in nghien_cuu.md"),
 ("[TODO] Script: 12+ min fast-paced catchy documentary (~2300 words, 45+ short scenes)",
  "xp check script >= 8/10. 4-layer frames (fact -> mechanism -> meaning -> hook), sentences <= 28 words, "
  "3+ retention hooks, open loops between chapters, dual text layers (loi verbatim for voice, phu_de keywords). QA: duration projection >= 720s"),
 ("[TODO] Narration: Edge TTS documentary voice + word timestamps",
  "en-US-AndrewNeural (deep US male, best edge voice for documentary) rate +10% for fast pace. "
  "gen_edge_narration.py -> segN.wav + segN.json (WordBoundary) -> xp narrate --import-from -> patch_word_timings.py -> xp timeline. QA: 100% word coverage, no dropped words"),
 ("[TODO] Images: imgagent (wikimedia/openverse, CC) -> license book",
  "pip install imgagent; batch queries per scene topic; ~55-70 landscape images; record author/license per asset "
  "-> video.yaml search: {file, author, license}. QA: zero assets without license entry; GHI_CONG.md complete"),
 ("[TODO] Music + mix: original underscore + auto SFX, -14 LUFS",
  "Original per-video score via xp compose (ABC) or synthesized underscore fallback; auto ducking; sfx level 1.0. "
  "QA: master loudness -14±1 LUFS; no clipping; voice clearly dominant under music"),
 ("[TODO] Render + export: 1920x1080 landscape master",
  "xp art n/a (footage backend) -> xp render (per-scene cache) -> xp export. QA: duration >= 12:00, h264+aac, landscape; frame spot-checks at 6 timestamps"),
 ("[QA] Frame + sync QA on master",
  "Check frames at ~8 timestamps: visual/narration consistency, labels word-locked, no burned caption drift, "
  "credits present. ASR cross-check vocabulary vs script. QA gate: ASR text >= 95% match"),
 ("[TODO] SRT via audio-to-text (ASR) on the actual final audio",
  "Split master mix into <=30s chunks at scene boundaries (16 kHz mono) -> z-ai ASR -> merge -> SRT sidecar. "
  "Standalone deliverable (caption-free master policy). QA: SRT text matches ASR of final audio by construction"),
 ("[TODO] Thumbnail + YouTube publish pack",
  "xp thumbnail (big-number / red-circle / cinematic styles) + out/youtube_dang_bai.md (titles, description, chapters, tags, credits). QA: thumbnail 1280x720, readable at 200px"),
 ("[TODO] Release v2.0.0 + docs/worklog push",
  "Push worklog.md, docs/, video project to Bilal140202/myang-studio + workspace backup repo. "
  "Release v2.0.0 assets: mp4, srt, thumbnail, publish pack, social captions. QA: release assets downloadable, DELIVERY.md policy respected"),
 ("[ENGINE] Long-form structure: xp series (6 episodes + teaser) instead of one giant render",
  "Decision: build 12+ min as series `videos/procrastination-fix/` (loat.yaml + tap-01..tap-06, 16x9, footage template) "
  "+ narrated teaser (opening hook) + chapter cards + end card. `xp series assemble` -> continuous music, YouTube chapters, -14 LUFS, SRT. "
  "Per-episode renders dodge sandbox SIGKILL on long processes. QA: assembled duration >= 12:00, chapters >= 3, each >= 10s"),
 ("[TODO] Workspace backup push (safety net)",
  "Push full /home/z/my-project workspace snapshot (mega-shot engine, studio, scripts, docs, worklog) to Bilal140202/workspace-backup. "
  "Excludes: build layers caches, node_modules, >100MB files. Token via env only. QA: push succeeds, file count > 2500"),
]

def api(url, data=None, method="POST"):
    req = urllib.request.Request(url, method=method,
        data=json.dumps(data).encode() if data else None,
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r) if r.status != 204 else {}

# milestone (idempotent: reuse existing with same title)
import urllib.error
MS_TITLE = "Procrastination long-form (v2.0.0)"
try:
    ms = api(f"https://api.github.com/repos/{REPO}/milestones",
             {"title": MS_TITLE, "state": "open",
              "description": "12+ min fast-paced documentary: how to stop procrastination. Edge TTS, imgagent CC images, mega-shot footage engine. Issues = todo/QA tracker."})
except urllib.error.HTTPError:
    mss = api(f"https://api.github.com/repos/{REPO}/milestones?state=all", method="GET") or []
    ms = next((m for m in mss if m["title"] == MS_TITLE), None) or mss[0]
print(f"milestone #{ms['number']}")

created = []
for title, body in ISSUES:
    it = api(f"https://api.github.com/repos/{REPO}/issues",
             {"title": title, "body": body, "milestone": ms["number"]})
    created.append(it["number"]); print(f"  #{it['number']}  {title}")

print("ALL CREATED:", created)
