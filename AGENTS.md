# Agent Contract

When the Web ChatGPT Git writer app is selected, Web ChatGPT is the primary autonomous coding agent. It must read this file, investigate the request, implement the complete change, add direct tests, inspect the full diff, run applicable checks, publish or update a pull request, and squash-merge it after required checks pass.

It must never push directly to `main`, force-push, delete branches, expose secrets, weaken tests, or modify protected repository, workflow, credential, or writer files.
